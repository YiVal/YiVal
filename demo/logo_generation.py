'''This script is used to generate logo for a tech startup company.'''

import os
import io
import json
import time
import requests
from PIL import Image

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from yival.wrappers.string_wrapper import StringWrapper

TOKEN = os.getenv('MIDJOURNEY_TOKEN')
BASE_URL = "https://api.thenextleg.io" #Add MIDJOURNEY_TOKEN to the environment variables

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

s = requests.Session()

def post_request(payload):
    '''post request to get messageid'''
    url = f"{BASE_URL}/v2/imagine"
    response = s.post(url, headers=HEADERS, data=payload)
    return response.json()

def get_request(messageid):
    '''get response from messageid'''
    url = f"{BASE_URL}/v2/message/{messageid}?expireMins=2"
    while True:
        response = s.get(url, headers=HEADERS)
        response_json = response.json()
        if response_json.get('progress') == 100:
            break
        else:
            time.sleep(2)
    print(f"Successfully get response from messageid: {messageid}")
    return response.json()

def load_image(response):
    '''load image from response'''
    url = f"{BASE_URL}/getImage"
    image_urls = response['response']['imageUrls']
    logo_list=[]
    for image_url in image_urls:
        payload = json.dumps({
            "imgUrl": image_url
        })
        response = s.post(url, headers=HEADERS, data=payload)
        if response.status_code == 200:
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            logo_list.append(image)
        else:
            print(f"Failed to load image from {image_url}. Response code: {response.status_code}")
    print("Successfully load images.")

    return logo_list

def logo_generation(tech_startup_business):
    payload = json.dumps({
      "msg":
        str(
            StringWrapper(
                "Design a single image logo for a tech startup company. Visually appealing and memorable. No text in graphic. Company names ", name="task"
            )
        ) + f'{tech_startup_business}',
      "ref": "",
      "webhookOverride": "", 
      "ignorePrefilter": "false"
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
    messageid = post_response.get("messageid")
    response = get_request(messageid)
    logo_res=load_image(response)
    return logo_res

# if __name__ == "__main__":
#     logo_generation('Innovatech Solutions')