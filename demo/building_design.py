'''This script is used to generate image from a building design prompt'''

import os

from openai import OpenAI

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


def prompt_generation(prompt: str) -> str:
    '''generate prompt for chatgpt based on the input'''
    logger = TokenLogger()
    logger.reset()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=1.0,
        max_tokens=3000
    )
    if response.choices[0].message.content is not None:
        res = str(response.choices[0].message.content[:1000])
    else:
        res = "No content found"

    if response.usage is not None:
        token_usage = response.usage.total_tokens
    else:
        token_usage = 0
    logger.log(token_usage)
    return res


# def load_image(response):
#     '''load image from response'''
#     print("[INFO] start load images")
#     url = f"{BASE_URL}/getImage"
#     image_urls = response['response']['imageUrls']
#     image_list = []
#     for image_url in image_urls:
#         payload = json.dumps({"imgUrl": image_url})
#         response = s.post(url, headers=HEADERS, data=payload)
#         if response.status_code == 200:
#             image_data = response.content
#             image = Image.open(io.BytesIO(image_data))
#             image_list.append(image)
#         else:
#             print(
#                 f"[Error] Failed to load image from {image_url}. Response code: {response.status_code}"
#             )
#     print("[INFO] Successfully load images.")

#     return image_list


def building_design(location: str, function: str, state: ExperimentState):
    # Ensure you have your OpenAI API key set up
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = prompt_generation(
        str(
            StringWrapper(
                "Generate a building design for a building",
                name="task",
                variables={
                    "location": location,
                    "function": function,
                },
                state=state
            )
        )
    )
    print(f"prompt: {prompt}")
    response = client.images.generate(
        model="dall-e-3", prompt=prompt, n=1, size="1024x1024"
    )
    print(f"response: {response}")
    # image_res = MultimodalOutput(
    #     text_output=response['response']['content'],
    #     image_output=response['response']['imageUrls'],
    # )
    # return image_res
    return response


def main():
    '''main function'''
    location = "New York"
    function = "office"
    state = ExperimentState()
    print(building_design(location, function, state))


if __name__ == "__main__":
    main()
