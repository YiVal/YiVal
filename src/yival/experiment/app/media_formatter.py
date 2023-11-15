import base64
import io
import re
import shutil

from PIL import Image
from pydub import AudioSegment

# ffmpeg_executable = "/opt/homebrew/Cellar/ffmpeg/6.0_1/bin/ffmpeg"
ffmpeg_executable = shutil.which("ffmpeg")
AudioSegment.converter = ffmpeg_executable


def include_image_base64(data_dict):
    """Check if a string includes a base64 encoded image."""
    pattern = r'iVBORw.+'
    for item in data_dict:
        for record in item:
            for value in record.values():
                if re.search(pattern, value):
                    return True
    return False

def include_video(data_dict):
    """Check if a string includes a video."""
    pattern = r'<yival_video_output>'
    for item in data_dict:
        for record in item:
            for value in record.values():
                if re.search(pattern, value):
                    return True
    return False

def include_audio_base64(data_dict):
    """Check if a string includes a base64 encoded audio."""

    pattern = r'data:audio/[\w+-]+;base64,[\w/+]*={0,2}'
    for item in data_dict:
        for record in item:
            for value in record.values():
                if re.search(pattern, value):
                    return True
    return False

def base64_to_img(base64_string):
    """Convert a base64 string into a PIL Image."""
    decoded = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(decoded))
    return image

def base64_to_audio(base64_string):
    """Convert a base64 string into a PyDub AudioSegment."""
    base64_data = re.search(r'base64,(.*)', base64_string).group(1)
    decoded = base64.b64decode(base64_data)
    audio = AudioSegment.from_file(io.BytesIO(decoded), format="wav") 
    return audio

def extract_and_decode_image_from_string(data_string):
    """Extract and decode the first image from a string include base64 encoded and return a dictionary."""
    # Extract text_output, image_output and evaluate part
    image_output_string_match = re.search(
        r"\['(.*?)',", data_string, re.DOTALL
    )
    if image_output_string_match:
        text_output_match = re.search(
            r'<yival_raw_output>\n(.*?)\n</yival_raw_output>', data_string,
            re.DOTALL
        )
        text_output = text_output_match.group(1)
        image_output_string = image_output_string_match.group(1)
        evaluate_match = re.search(r"\](.*)", data_string, re.DOTALL)
        evaluate = evaluate_match.group(1).strip()
        # Check if image_output_string is base64 image
        image_output = base64_to_img(image_output_string)
        return {
            "text_output": text_output,
            "image_output": image_output,
            "evaluate": evaluate
        }
    else:
        return None
    
def extract_and_decode_video_from_string(data_string):
    """Extract and decode the first video from a string include video urls and return a dictionary."""
    # Extract text_output, video_output and evaluate part
    video_output_string_match = re.search(
        r"<yival_video_output>(.*?)</yival_video_output>", data_string,
        re.DOTALL
    )
    if video_output_string_match:
        text_output_match = re.search(
            r'<yival_raw_output>\n(.*?)\n</yival_raw_output>', data_string,
            re.DOTALL
        )
        text_output = text_output_match.group(1)
        video_output = video_output_string_match.group(1)
        evaluate_match = re.search(
            r"</yival_video_output>(.*)", data_string, re.DOTALL
        )
        evaluate = evaluate_match.group(1).strip()
        return {
            "text_output": text_output,
            "video_output": video_output,
            "evaluate": evaluate
        }
    else:
        return None
    
def extract_and_decode_audio_from_string(data_string):
    """Extract and decode the first audio from a string containing base64-encoded audio and return an AudioSegment."""
    audio_output_string_match = re.search(
        r'data:audio/[\w+-]+;base64,[\w/+]*={0,2}', data_string, re.DOTALL
    )
    if audio_output_string_match:
        text_output_match = re.search(
            r'<yival_raw_output>\n(.*?)\n</yival_raw_output>', data_string,
            re.DOTALL
        )
        text_output = text_output_match.group(1)
        audio_output_string = audio_output_string_match.group(0)
        print("audio_output_string")
        print(audio_output_string)
        evaluate_match = re.search(r"\](.*)", data_string, re.DOTALL)
        evaluate = evaluate_match.group(1).strip()
        audio_output = base64_to_audio(audio_output_string)
        print("audio_output")
        print(audio_output)
        return {
            "text_output": text_output,
            "audio_output": audio_output,
            "evaluate": evaluate
        }
    else:
        return None

def extract_and_decode_image(data_dict):
    """Extract and decode image from a dictionary include base64 encoded."""
    new_data_dict = []
    for item in data_dict:
        for record in item:
            new_record = {}
            for key, value in record.items():
                if isinstance(value, str):
                    image = extract_and_decode_image_from_string(value)
                    if image is not None:
                        new_record[key] = image
                    else:
                        new_record[key] = value
                else:
                    new_record[key] = value
            new_data_dict.append(new_record)
    return new_data_dict

def extract_and_decode_video(data_dict):
    """Extract and decode video from a dictionary include video url."""
    new_data_dict = []
    for item in data_dict:
        for record in item:
            new_record = {}
            for key, value in record.items():
                if isinstance(value, str):
                    video = extract_and_decode_video_from_string(value)
                    if video is not None:
                        new_record[key] = video
                    else:
                        new_record[key] = value
                else:
                    new_record[key] = value
            new_data_dict.append(new_record)
    return new_data_dict


def extract_and_decode_audio(data_dict):
    """Extract and decode audio from a dictionary containing base64-encoded audio."""
    new_data_dict = []
    for item in data_dict:
        for record in item:
            new_record = {}
            for key, value in record.items():
                if isinstance(value, str):
                    audio = extract_and_decode_audio_from_string(value)
                    if audio is not None:
                        new_record[key] = audio
                    else:
                        new_record[key] = value
                else:
                    new_record[key] = value
        new_data_dict.append(new_record)
    return new_data_dict


def pil_image_to_base64(image: Image, format: str = "PNG") -> str:
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue())
    return "data:image/png;base64," + img_str.decode()


def pil_audio_to_base64(audio: AudioSegment, format: str = "wav") -> str:
    temp_audio_file = f'temporary_audio.{format}'
    audio.export(temp_audio_file, format=format)

    # Read the exported audio file as bytes
    with open(temp_audio_file, 'rb') as audio_file:
        audio_bytes = audio_file.read()

    # Encode the audio data as base64
    audio_base64 = base64.b64encode(audio_bytes).decode()

    # Print the data URI
    data_uri = f"data:audio/{format};base64,{audio_base64}"
    return data_uri
