'''This script is used to generate logo for a tech startup company.'''

import io
import json
import os
import time

import openai
import requests
from PIL import Image
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from yival.wrappers.string_wrapper import StringWrapper

os.environ['MIDJOURNEY_TOKEN'] = '7ab0c4ac-4be4-419d-8656-ddb251383e17'
BASE_URL = "https://api.thenextleg.io"
TOKEN = os.getenv('MIDJOURNEY_TOKEN')

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}
tech_startup_business = 'Innovatech Solutions'
s = requests.Session()


def prompt_generation(prompt: str) -> str:
    print(f"[DEBUG] chatgpt input:{prompt}")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1.0,
        max_tokens=300
    )
    res = response['choices'][0]['message']['content'][:1000]
    print(f"[DEBUG] chatgpt output:{res}")
    return res


def post_request(payload):
    '''post request to get messageId'''
    url = f"{BASE_URL}/v2/imagine"
    response = s.post(url, headers=HEADERS, data=payload)
    return response.json()


def get_request(messageId):
    '''get response from messageId'''
    url = f"{BASE_URL}/v2/message/{messageId}?expireMins=2"
    while True:
        time.sleep(5)
        response = s.get(url, headers=HEADERS)
        print(f"[DEBUG] response: {response}, reponse_text:{response.text}")
        response_json = response.json()
        '''if get response, then break'''
        if response_json.get('progress') == 100:
            break
    print(
        f"[INFO][logl_generation] Successfully get response from messageId: {messageId}"
    )
    return response.json()


def load_image(response):
    '''load image from response'''
    url = f"{BASE_URL}/getImage"
    image_urls = response['response']['imageUrls']
    logo_list = []
    for image_url in image_urls:
        payload = json.dumps({"imgUrl": image_url})
        response = s.post(url, headers=HEADERS, data=payload)
        if response.status_code == 200:
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            logo_list.append(image)
        else:
            print(
                f"[Error][logo_generation] Failed to load image from {image_url}. Response code: {response.status_code}"
            )
    print(f"[INFO][logo_generation] Successfully load images.")

    return logo_list


def logo_generation(species, character):

    payload = json.dumps({
        "msg":
        prompt_generation(
            str(
                StringWrapper(
                    "Error",
                    name="task",
                    variables={
                        "animal_species": species,
                        "animal_character": character,
                    }
                )
            )
        ),
        # str(
        #     StringWrapper(
        #         "Design a single image logo for a tech startup company. The logo should represent cutting-edge technology, forward-thinking, high-quality solutions. It should be visually appealing and memorable, incorporating the company's name or its initials. No text in graphic. Company names ",
        #         name="task",
        #         variables={
        #             "animal_species": species,
        #             "animal_character": character,
        #         }
        #     )
        # ) + f'{tech_startup_business}',
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
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    s.mount("http://", adapter)
    s.mount("https://", adapter)

    post_response = post_request(payload)
    print(f"[DEBUG] post_response:{post_response}")
    messageId = post_response.get("messageId")
    print(f"[DEBUG] messageID: {messageId}")
    response = get_request(messageId)
    logo_res = load_image(response)
    print("Done")
    return logo_res


if __name__ == "__main__":
    logo_generation("你好", "你好")
