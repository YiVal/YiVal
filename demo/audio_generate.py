import io
import json
import os
import time

import openai
# from IPython.display import Audio
# from pydub import AudioSegment
import requests
from pydub import AudioSegment
# from io import BytesIO
# import pygame
# import tempfile
from requests.adapters import HTTPAdapter  # type: ignore
from requests.packages.urllib3.util.retry import Retry  # type: ignore
from demo.animal_story import load_image
from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper

ffmpeg_executable = "/opt/homebrew/Cellar/ffmpeg/6.0_1/bin/ffmpeg"

# Set the ffmpeg path in the AudioSegment
AudioSegment.converter = ffmpeg_executable
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')

s = requests.Session()

def prompt_generation(prompt: str, style) -> str:
    '''generate prompt for chatgpt based on the input'''
    logger = TokenLogger()
    logger.reset()
    openai.api_key = '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'
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1.0,
        max_tokens=3000
    )
    res = str(
        f'music style: {style} ' +
        response['choices'][0]['message']['content'][:1000]
    )
    token_usage = response['usage']['total_tokens']
    logger.log(token_usage)
    return res

def post_request(payload):
    '''post request to get messageid'''
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {REPLICATE_API_TOKEN}"
    }
    response = s.post(url, headers=headers, data=payload)
    return response.json()

def get_request(response_id):
    '''get response from messageId'''
    prediction_url = "https://api.replicate.com/v1/predictions/"+response_id
    # print(prediction_url)
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}"
    }
    response = s.get(prediction_url, headers=headers)

    if response.status_code == 200:
        result = response.json()
        # print("Response:", result)
        while True:
            time.sleep(15) 
            response = s.get(prediction_url, headers=headers)
            result = response.json()
            if result['status'] == 'succeeded':
                break
            
        # print(f"[INFO] Successfully get response from messageId: {response_id}")
        return response.json()

        # URL of the audio file
        # audio_url = result['output']

def load_audio(response):
    audio_url = response['output']
    audio_list = []
    response = s.get(audio_url)
    if response.status_code == 200:
        audio = AudioSegment.from_wav(io.BytesIO(response.content))
        audio_list.append(audio)
    # else:
    #     print(
    #         f"[Error] Failed to load audio from {audio_list}. Response code: {response.status_code}"
    #     )
    # print("[INFO] Successfully load audios.")
    # print(audio_list)
    return audio_list

def audio_generation(key: str, rhythm: str, melody: str, music_instrument: str, music_genre: str, state: ExperimentState):
    payload = json.dumps({
        "version": "7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
        "input": {
                    "model_version": "melody",
                    "prompt":prompt_generation(
                                str(
                                    StringWrapper(
                                        "Produce a music of a",
                                        name="task",
                                        variables={
                                            "key": key,
                                            "rhythm": rhythm,
                                            "melody": melody,
                                            "music_instrument": music_instrument
                                        },
                                        state=state
                                    )
                                ),
                                style=music_genre
                            )
                }
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
    # print(post_response)
    responseid = post_response.get("id")
    response = get_request(responseid)
    audio_res = MultimodalOutput(
        text_output=response['input']['prompt'],
        audio_output=load_audio(response),
    )
    return audio_res
    

if __name__ == "__main__":
    audio_generation('major g', 'slow', "soothing, joyful", 'piano', "ballad", ExperimentState())
          