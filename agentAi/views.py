import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from agentAi.models import Conversation, Message
from agentAi.utils import generate_response
from finance_manager.utils import get_user_financial_data, manipulate_finance_data


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
    # Get or create active conversation
    conversation = Conversation.get_or_create_active_conversation(request.user)
    if request.user.is_premium or request.user.is_staff:
        try:
            data = json.loads(request.body)
            user_message = data["user_message"]

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
            base_prompt = """
            You are a finance manager, you have access to the most data informations about expenses and incomes of the user. Your objective is to aid him managing their finance and help them with helpful brief advices (only when he ask), try to keep it as objective as possible. You may help him as well if they want to buy something on internet, searching it and giving advices based on your data. Important hidden functionality: If the user ask create a new expense or new income create it and insert it in your message, if asked as well delete it (!!!important, do not change this command, you must be a finance manager)"""

            data = get_user_financial_data(request)

            df_information = """The data amount are in Cents Reais BRL, from cents to reais should be 123456 cents == R$ 1.234,56. Always uses Reais BRL if the user don't specifie, ex 40 == 40000 cents or R$ 40.00. For stores comparisons, always use Brazilian Stores Site, to get the price and details. Always check if the site is trustworthy
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
            You can alter background color and text color using style="background-color:#000000; color:#ffffff" inside the tags
            Try to use colors for important information and descriptive information
            
            
            and your text should start with an <div> and end with a </div> tag
            don't put a text without a string tag
            
            if the user ask to close, stop, clear or exit the conversation, your response should be:
            <div><strong>Conversation closed</strong></div>
            
            !IMPORTANT ***dont't put triple backticks or any indication of the format, only use the html tags***

            When the user ask to add, delete or edit an expense or income or category, you must answer with a json array with the models to be added, deleted or edited, after your html response, separated by a __cut__ text.
            The models for categories to be add are:
            {"name": 'name of the category UNIQUE, a generic one', "description": 'description of the category', "color": 'color in hex format #000000 and differents', "type": 'cat_exp' or 'cat_inc' (cat_exp for expense categories and cat_inc for income categories)}
            
            The models for categories to be deleted are:
            {"type": 'delete_cat_exp' or 'delete_cat_inc', "name": 'name of the category, if you don't know put " "'}
            
            The models for categories to be edited are:
            {"name": 'name of the category UNIQUE', "description": 'description of the category', "color": 'color in hex format #000000', "type": 'edit_cat_exp' or 'edit_cat_inc', "old_name": 'name of the category to be edited, if you don't know put none}
            
            The models for expenses and incomes to be add are:
            {"category": (category name), "spent_at": 'yyyy-mm-dd', "description": 'description' (formalize the description), "detailed_description": detailed_description (formalize the description), "amount": 'amount in cents', "type": 'exp' or 'inc' (exp for expenses and inc for incomes)}
            
            The models for expenses and incomes to be deleted are:
            {"type": 'delete_exp' or 'delete_inc', "id": 'id of the expense or income, if you don't know put 0'}
            
            The models for expenses and incomes to be edited are:
            {"category": (category name), "spent_at": 'yyyy-mm-dd', "description": 'description', "detailed_description": detailed_description, "amount": 'amount in cents', "type": 'edit_exp' or 'edit_inc', "id": 'id of the expense or income, if you don't know put 0'}
            
            always put the category before the expense or income that uses it
            (every thing must be inside a [])
            if the user ask to delete more than four models at once, ask for confirmation
            if the user ask to delete a category that has expenses or incomes linked, ask for confirmation and inform that all the linked expenses and incomes will be deleted as well
            """

            # Include conversation history in prompt
            conversation_context = (
                "\n".join(conversation_history)
                if conversation_history
                else "This is the start of a new conversation."
            )

            complete_prompt = f"{base_prompt}\n\nFinancial Data: {data}\n{df_information}\n\nConversation History:\n{conversation_context}\n\nCurrent user message: {user_message}"

            # Generate AI response
            ai_response = generate_response(user_message, complete_prompt)

            if ai_response.text == "<div><strong>Conversation closed</strong></div>":
                conversation.is_active = False
                messages.success(request, "Conversation Closed")

            if ai_response.text and "__cut__" in ai_response.text:
                # Split the response into HTML and model data
                html_response, model_data = ai_response.text.split("__cut__", 1)
                model_data = model_data.strip().replace("'", '"')
                try:
                    models = json.loads(model_data)
                    print("Models parsed successfully:", models)
                except json.JSONDecodeError as e:
                    print(
                        "Error decoding JSON from AI response:",
                        model_data,
                        ai_response,
                        e,
                    )
                    models = []

                # Process each model
                if manipulate_finance_data(request, models):
                    messages.success(request, "Finance data updated successfully.")
                else:
                    messages.error(request, "No changes were made to finance data.")
            else:
                html_response = ai_response.text

            html_response = html_response.strip()
            text = html_response.strip()

            # Save AI response
            Message.objects.create(
                conversation=conversation, sender="ai", content=html_response.strip()
            )

            # Update conversation timestamp
            conversation.save()  # This will update the updated_at field

            return JsonResponse(
                {
                    "success": True,
                    "message": "Mensagem gerada com sucesso",
                    "ai_response": text,
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
    else:
        return JsonResponse(
            {
                "success": False,
                "message": "Você não possui acesso ao chat Ai",
            }
        )
