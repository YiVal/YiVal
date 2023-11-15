import shutil

import numpy as np
from dash import dcc, html  # type: ignore
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
from PIL import Image
from pydub import AudioSegment

from yival.experiment.app.media_formatter import pil_audio_to_base64, pil_image_to_base64
from yival.schemas.experiment_config import MultimodalOutput

ffmpeg_executable = shutil.which("ffmpeg")

AudioSegment.converter = ffmpeg_executable
def create_table(data):
    """Create an HTML table from a list of dictionaries, where the values can be strings or PIL images."""
    # Create the header row
    header_row = [
        html.Th(key if key != "Hashed Group Key" else "Human Rating")
        for key in data[0].keys()
    ]
    table_rows = [html.Tr(header_row)]

    # Create the data rows
    for record in data:
        row = []
        for key, value in record.items():
            if key == "Hashed Group Key":
                # Convert the hashed group key to a hyperlink
                href = f"/rating-result/{value}"
                cell = html.Td(
                    dcc.Link("Link", href=href)
                )  # Replace "Link text" with the text you want to display
            elif isinstance(value, dict):
                if "image_output" in value:
                    img = html.Img(
                        src=pil_image_to_base64(value["image_output"]),
                        style={
                            'width': '200px',
                            'height': '200px'
                        }
                    )
                else:
                    # show empty img
                    img = html.Img(src="")
                if "audio_output" in value:
                    audio = html.Audio(
                        controls=True,
                        src=pil_audio_to_base64(value["audio_output"])
                    )
                else:
                    # show empty audio
                    audio = html.Audio(
                        controls=False,
                        src=""
                    )
                text = html.P(value["text_output"])
                cell = html.Td([
                    text, html.Br(), img, html.Br(), audio,
                    html.Br(), value["evaluate"]
                ])
            else:
                cell = html.Td(value)
            row.append(cell)
        table_rows.append(html.Tr(row))
    return table_rows

def create_video_table(data):
    """Create an HTML table from a list of dictionaries, where the values can be strings or video."""
    # Create the header row
    header_row = [
        html.Th(key if key != "Hashed Group Key" else "Human Rating")
        for key in data[0].keys()
    ]
    table_rows = [html.Tr(header_row)]

    # Create the data rows
    for record in data:
        row = []
        for key, value in record.items():
            if key == "Hashed Group Key":
                # Convert the hashed group key to a hyperlink
                href = f"/rating-result/{value}"
                cell = html.Td(
                    dcc.Link("Link", href=href)
                )  # Replace "Link text" with the text you want to display on UI
            elif isinstance(value, dict):
                text = html.P(value["text_output"])
                video = html.Div(
                    children=html.Video(
                        controls=True,
                        id='movie_player',
                        src=value["video_output"],
                        autoPlay=False
                    ),
                    style={
                        'height': '200px',
                        'width': '200px',
                    }
                )
                cell = html.Td([
                    text, html.Br(), video,
                    html.Br(), value["evaluate"]
                ])
            else:
                cell = html.Td(value)
            row.append(cell)
        table_rows.append(html.Tr(row))
    return table_rows


def handle_output(output):
    print("output")
    print(output)
    if isinstance(output, list):
        if all(isinstance(item, Image.Image) for item in output):
            return [
                html.Img(src=pil_image_to_base64(img), className="image")
                for img in output
            ]
        if all(isinstance(item, AudioSegment) for item in output):
            return [
                html.Audio(
                    controls=True,
                    src=pil_audio_to_base64(audio)
                    )
                for audio in output
            ]
        else:
            return [html.P(str(item)) for item in output]
    else:
        return html.P(str(output))

def df_to_table(df):
    return html.Table([html.Tr([html.Th(col) for col in df.columns])] + [
        html.Tr([html.Td(row[col]) for col in df.columns])
        for index, row in df.iterrows()
    ])
    
def format_with_tags(cell):
    # Split the cell content using the yival_raw_output tags
    raw_output_start = "<yival_raw_output>"
    raw_output_end = "</yival_raw_output>"

    if raw_output_start in cell and raw_output_end in cell:
        raw_output_content, rest = cell.split(raw_output_end, 1)
        raw_output_content = raw_output_content.replace(
            raw_output_start, ""
        ).strip()

        # Format the rest of the content
        formatted_evaluator_outputs = []
        for line in rest.split("\n"):
            formatted_evaluator_outputs.append(
                "▶ " + line.strip() if ":" in line else line.strip()
            )

        # Combine raw_output and formatted evaluator outputs
        return raw_output_start + "\n" + raw_output_content + "\n" + raw_output_end + "\n" + "\n".join(
            formatted_evaluator_outputs
        )
    else:
        return cell

def format_dataframe_column(cell):
    # If the cell contains the yival_raw_output tags
    if "<yival_raw_output>" in cell and "</yival_raw_output>" in cell:
        return format_with_tags(cell)
    else:
        # Otherwise, format the cell content using the original "▶" logic
        return "\n".join([
            "▶ " + line if ":" in line else line
            for line in cell.split("\n")
        ])

def determine_relative_color(value, values):
    if not isinstance(value, (int, float)):
        return "black"

    p25, p50, p75 = np.percentile(values, [25, 50, 75])

    if value <= p25:
        return "green"
    elif value <= p50:
        return "lightgreen"
    elif value <= p75:
        return "orange"
    else:
        return "red"
    
def colorize_metric(combinations):
    # Extract all metrics from the results dynamically
    all_metrics = {key: [] for key in combinations[0].keys()}
    for combo in combinations:
        for key, value in combo.items():
            if isinstance(value, (int, float)):
                all_metrics[key].append(value)

    colored_combinations = []
    for combo in combinations:
        colored_combo = {}
        for key, value in combo.items():
            color = determine_relative_color(
                value, all_metrics.get(key, [])
            )
            colored_combo[key] = {"value": value, "color": color}
        colored_combinations.append(colored_combo)

    return colored_combinations