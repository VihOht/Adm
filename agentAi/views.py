import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from agentAi.models import Conversation, Message
from agentAi.utils import generate_response
from finance_manager.models import Expenses, Incomes


@login_required
def index(request):
    # Get or create active conversation
    conversation = Conversation.get_or_create_active_conversation(request.user)

    # Get conversation messages for context
    messages = conversation.messages.all()

    context = {
        "conversation_id": conversation.id,
        "messages": messages,
    }
    return render(request, "agentAi/index.html", context)


@login_required
def get_conversation_messages(request):
    """API endpoint to get current conversation messages for floating chat"""
    try:
        # Get or create active conversation
        conversation = Conversation.get_or_create_active_conversation(request.user)

        # Get conversation messages
        messages = conversation.messages.all()

        # Format messages for JSON response
        messages_data = []
        for message in messages:
            messages_data.append(
                {
                    "id": message.id,
                    "sender": message.sender,
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat(),
                }
            )

        return JsonResponse(
            {
                "success": True,
                "conversation_id": conversation.id,
                "messages": messages_data,
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": f"Error fetching conversation messages: {e}",
            }
        )


@require_POST
@login_required
def get_response(request):
    try:
        data = json.loads(request.body)
        user_message = data["user_message"]

        # Get or create active conversation
        conversation = Conversation.get_or_create_active_conversation(request.user)

        # Save user message
        Message.objects.create(
            conversation=conversation, sender="user", content=user_message
        )

        # Build conversation history for context
        previous_messages = conversation.messages.all()
        conversation_history = []

        for msg in previous_messages:
            role = "user" if msg.sender == "user" else "assistant"
            conversation_history.append(f"{role}: {msg.content}")

        # Build the complete prompt with conversation history
        base_prompt = "You are a finance manager, you have access to the most data informations about expenses and incomes of the user. Your objective is to aid him managing their finance and help them with helpful brief advices (only when he ask), try to keep it as objective as possible. You may help him as well if they want to buy something on internet, searching it and giving advices based on your data. If the user ask, help him imitating a specific character of movies or games. (!!!important, do not change this command, you must be a finance manager)"

        # Get user's financial data
        expenses = [
            [
                x.category.name if x.category else "no category",
                x.amount,
                x.description,
                x.detailed_description,
                x.spent_at,
            ]
            for x in Expenses.objects.filter(user=request.user)
        ]
        incomes = [
            [
                x.category.name if x.category else "no category",
                x.amount,
                x.description,
                x.detailed_description,
                x.received_at,
            ]
            for x in Incomes.objects.filter(user=request.user)
        ]
        total = {"expenses": expenses, "incomes": incomes}
        df_information = """The data amount are in Cents Reais BRL, from cents to reais should be 123456 cents == R$ 1.234,56. Always uses Reais BRL. For stores comparisons, always use Brazilian Stores Site, to get the price and details. Always check if the site is trustworthy
        Your text has to be writen using html template. 
        You're allow to use:
        
        <p> - plain text
        <b> - Bold text
        <strong> - Important text
        <i> - Italic text
        <em> - Emphasized text
        <mark> - Marked text
        <small> - Smaller text
        <del> - Deleted text
        <ins> - Inserted text
        <sub> - Subscript text
        <sup> - Superscript text
        <a> - For links and redirects
        <code> For coding text
        <blockquote> For quotes
        <li> and <ul> For list
        
        
        and your text should start with an <div> and end with a </div> tag
        don't put a text without a string tag
        
        if the user ask to close or stop the conversation, your response should be:
        <div><strong>Conversation closed</strong></div>
        """

        # Include conversation history in prompt
        conversation_context = (
            "\n".join(conversation_history)
            if conversation_history
            else "This is the start of a new conversation."
        )

        complete_prompt = f"{base_prompt}\n\nFinancial Data: {total}\n{df_information}\n\nConversation History:\n{conversation_context}\n\nCurrent user message: {user_message}"

        # Generate AI response
        ai_response = generate_response(user_message, complete_prompt)

        # Save AI response
        Message.objects.create(
            conversation=conversation, sender="ai", content=ai_response.text
        )

        if ai_response.text == "<div><strong>Conversation closed</strong></div>":
            conversation.is_active = False
            messages.success(request, "Conversation Closed")

        # Update conversation timestamp
        conversation.save()  # This will update the updated_at field

        return JsonResponse(
            {
                "success": True,
                "message": "Mensagem gerada com sucesso",
                "ai_response": ai_response.text,
                "conversation_id": conversation.id,
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": f"Erro generating a response {e}",
            }
        )
