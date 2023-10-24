import openai
import os
def headline_generation(tech_startup_business:str) :
    # Ensure you have your OpenAI API key set up
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print(f"openai_key_now: {openai.api_key}")
    messages = [{
        "role":
        "system",
        "content":
        "You are a helpful assistant that help company grow."
    }, {
        "role":
        "user",
        "content": '你好' + f'{tech_startup_business}'
    }]
    # Use the chat-based completion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    print(f"response: {response}")


headline_generation("YiVal")
