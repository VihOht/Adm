from google import genai


def connect_client():
    client = genai.Client()
    return client


def generate_response(message, prompt):
    client = connect_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=[f"{prompt}\n\n{message}"]
    )
    return response
