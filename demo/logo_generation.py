'''This script is used to generate logo for a tech startup company.'''

import requests
import json
import time
from PIL import Image
import io
import os

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from yival.wrappers.string_wrapper import StringWrapper

BASE_URL = "https://api.thenextleg.io"
TOKEN = os.getenv('MIDJOURNEY_TOKEN')

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}
tech_startup_business='Innovatech Solutions'
s = requests.Session()

def post_request(payload):
    '''post request to get messageId'''
    url = f"{BASE_URL}/v2/imagine"
    response = s.post(url, headers=HEADERS, data=payload)
    return response.json()

def get_request(messageId):
    '''get response from messageId'''
    url = f"{BASE_URL}/v2/message/{messageId}?expireMins=2"
    while True:
        response = s.get(url, headers=HEADERS)
        response_json = response.json()
        '''if get response, then break'''
        if response_json.get('progress') == 100:
            break
        else:
            time.sleep(2)
    print(f"Successfully get response from messageId: {messageId}")
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
    print(f"Successfully load images.")

    return logo_list

def logo_generation(tech_startup_business):
    payload = json.dumps({
      "msg":
        str(
            StringWrapper(
                "Design a single image logo for a tech startup company. The logo should represent cutting-edge technology, forward-thinking, high-quality solutions. It should be visually appealing and memorable, incorporating the company's name or its initials. No text in graphic. Company names ", name="task"
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
    messageId = post_response.get("messageId")
    response = get_request(messageId)
    logo_res=load_image(response)
    print("Done")
    return logo_res


# if __name__ == "__main__":
#     logo_generation(tech_startup_business)

