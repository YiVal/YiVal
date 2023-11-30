'''This script is used to generate image from a story.'''

import io
import json
import os
import time

import requests
from openai import OpenAI
from PIL import Image
from requests.adapters import HTTPAdapter  # type: ignore
from requests.packages.urllib3.util.retry import Retry  # type: ignore

from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper

TOKEN = os.getenv('MIDJOURNEY_TOKEN')
BASE_URL = "https://api.thenextleg.io"  #Add MIDJOURNEY_TOKEN to the environment variables

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

s = requests.Session()


def prompt_generation(prompt: str, style) -> str:
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
        res = str(
            f'Drawing style: {style}, ' +
            response.choices[0].message.content[:1000]
        )
    else:
        res = "No content found"

    if response.usage is not None:
        token_usage = response.usage.total_tokens
    else:
        token_usage = 0

    logger.log(token_usage)
    return res


def post_request(payload):
    '''post request to get messageid'''
    url = f"{BASE_URL}/v2/imagine"
    response = s.post(url, headers=HEADERS, data=payload)
    return response.json()


def get_request(messageId):
    '''get response from messageId'''
    url = f"{BASE_URL}/v2/message/{messageId}?expireMins=2"
    while True:
        time.sleep(2)
        response = s.get(url, headers=HEADERS)
        response_json = response.json()
        if response_json.get('progress') == 100:
            break
    print(f"[INFO] Successfully get response from messageId: {messageId}")
    return response.json()


def load_image(response):
    '''load image from response'''
    print("[INFO] start load images")
    url = f"{BASE_URL}/getImage"
    image_urls = response['response']['imageUrls']
    image_list = []
    for image_url in image_urls:
        payload = json.dumps({"imgUrl": image_url})
        response = s.post(url, headers=HEADERS, data=payload)
        if response.status_code == 200:
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            image_list.append(image)
        else:
            print(
                f"[Error] Failed to load image from {image_url}. Response code: {response.status_code}"
            )
    print("[INFO] Successfully load images.")

    return image_list


def image_generation(
    species, character, drawing_style, state: ExperimentState
):
    payload = json.dumps({
        "msg":
        prompt_generation(
            str(
                StringWrapper(
                    "Draw a picture of a",
                    name="task",
                    variables={
                        "animal_species": species,
                        "animal_character": character,
                    },
                    state=state
                )
            ),
            style=drawing_style
        ),
        "ref":
        "",
        "webhookOverride":
        "",
        "ignorePrefilter":
        "false"
    })
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    s.mount("http://", adapter)
    s.mount("https://", adapter)

    post_response = post_request(payload)
    messageid = post_response.get("messageId")
    response = get_request(messageid)
    image_res = MultimodalOutput(
        text_output=response['response']['content'],
        image_output=load_image(response),
    )
    return image_res


if __name__ == "__main__":
    image_generation('duck', 'cute', 'Picture Book Style', ExperimentState())
