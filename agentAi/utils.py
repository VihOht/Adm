from google import genai
from google.genai import types


def connect_client():
    client = genai.Client()
    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    tools = [grounding_tool]

    config = types.GenerateContentConfig(tools=tools)
    return client, config


def generate_response(message, prompt):
    client, config = connect_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=[f"{prompt}\n\n{message}"], config=config
    )
    return response
