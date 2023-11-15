# type: ignore
import hashlib
import shutil

from dash import dcc, html  # type: ignore
from pydub import AudioSegment

from yival.experiment.app.media_formatter import pil_audio_to_base64, pil_image_to_base64
from yival.experiment.app.utils import sanitize_group_key

# fixed the ImportError: attempted relative import with no known parent package
# from relative import to absolute import

ffmpeg_executable = shutil.which("ffmpeg")

AudioSegment.converter = ffmpeg_executable


def get_group_experiment_result_from_hash(hashed_group_key, experiment_data):
    for group_result in experiment_data.group_experiment_results:
        group_key = sanitize_group_key(group_result.group_key)
        if hashlib.sha256(group_key.encode()
                            ).hexdigest() == hashed_group_key:
            return group_result
    for group_result in experiment_data.enhancer_output.group_experiment_results:
        group_key = sanitize_group_key(group_result.group_key)
        if hashlib.sha256(group_key.encode()
                            ).hexdigest() == hashed_group_key:
            return group_result
    return None


def display_group_experiment_result_layout(
        hashed_group_key, experiment_config, experiment_data, is_from_enhancer=False
    ):
    group_result = get_group_experiment_result_from_hash(hashed_group_key, experiment_data)
    if not group_result:
        return html.Div(
            "No data found for this group key.",
            style={
                'font-size': '24px',
                'color': 'red',
                'margin': '40px',
                'text-align': 'center'
            }
        )
    initial_slider_data = {}
    sanitized_key = sanitize_group_key(group_result.group_key)

    children = [
        html.H3(
            f"Group Key: {sanitized_key}",
            style={
                'text-align': 'center',
                'margin-bottom': '20px',
                'color': '#5D6D7E'
            }
        ),
        html.H2(
            "Rate experiment results",
            style={
                'text-align': 'center',
                'margin-bottom': '70px',
                'font-weight': 'bold',
                'color': '#2E86C1',
                'border-bottom': '4px solid #3498DB',
                'padding-bottom': '30px',
                'font-size': '28px'
            }
        ),
        dcc.Input(
            id='current-group-key', type='hidden', value=hashed_group_key
        )
    ]
    children.append(
        dcc.Store(id='is-from-enhancer', data=is_from_enhancer)
    )

    for index, exp_result in enumerate(group_result.experiment_results):
        # Displaying only the raw output
        children.append(
            html.Div(
                "Raw Output:",
                style={
                    'font-weight': 'bold',
                    'font-size': '26px',
                    'margin-top': '50px',
                    'color': '#2C3E50'
                }
            )
        )
        if exp_result.raw_output.image_output:
            images = []
            for image in exp_result.raw_output.image_output:
                img_str = pil_image_to_base64(image)
                img = html.Img(
                    src=img_str,
                    style={
                        'width': '200px',
                        'height': '200px',
                        'margin': 'auto'
                    }
                )
                images.append(img)
            text = html.P(
                exp_result.raw_output.text_output,
                style={'grid-column': 'span 4'
                        }  # Make the text span 4 columns
            ) if exp_result.raw_output.text_output else None
            content = html.Div([text] + images,
                                style={
                                    'display': 'grid',
                                    'grid-template-columns':
                                    'repeat(4, 1fr)',
                                    'justify-content': 'center',
                                    'align-items': 'center'
                                })
        elif exp_result.raw_output.video_output:
            videos = []
            for video in exp_result.raw_output.video_output:
                vid = html.Video(
                    controls=True,
                    id='movie_player',
                    src=video,
                    autoPlay=False,
                    style={
                        'width': '200px',
                        'height': '200px',
                        'margin': 'auto'
                    }
                )
                videos.append(vid)
            text = html.P(
                exp_result.raw_output.text_output,
                style={'grid-column': 'span 4'
                        }  # Make the text span 4 columns
            ) if exp_result.raw_output.text_output else None
            content = html.Div([text] + videos,
                                style={
                                    'display': 'grid',
                                    'grid-template-columns':
                                    'repeat(4, 1fr)',
                                    'justify-content': 'center',
                                    'align-items': 'center'
                                })
        elif exp_result.raw_output.audio_output:
            audios = []
            for audio in exp_result.raw_output.audio_output:
                aud_str = pil_audio_to_base64(audio)
                aud = html.Audio(
                    controls=True,
                    src=aud_str,
                    # style={
                    #     'width': '200px',
                    #     'height': '200px',
                    #     'margin': 'auto'
                    # }
                )
                audios.append(aud)
            text = html.P(
                exp_result.raw_output.text_output,
                style={'grid-column': 'span 4'
                        }  # Make the text span 4 columns
            ) if exp_result.raw_output.text_output else None
            content = html.Div([text] + audios,
                                style={
                                    'display': 'grid',
                                    'grid-template-columns':
                                    'repeat(4, 1fr)',
                                    'justify-content': 'center',
                                    'align-items': 'center'
                                })
        else:
            content = str(exp_result.raw_output.text_output)

        children.append(
            html.Div(
                content,
                style={
                    'margin': '25px 0',
                    'border': '2px solid #AED6F1',
                    'padding': '25px',
                    'background-color': '#EAF2F8',
                    'border-radius': '10px',
                    'box-shadow': '0 4px 12px rgba(0, 0, 0, 0.1)',
                    'font-size': '22px'
                }
            )
        )

        for rating_config_index, rating_config in enumerate(
            experiment_config["human_rating_configs"] or []
        ):
            existing_human_evaluator = next((
                e for e in exp_result.evaluator_outputs
                if e.name == "human_evaluator"
                and e.display_name == rating_config['name']
            ), None)

            # Displaying rating instructions if present in rating_config
            if "instructions" in rating_config:
                children.append(
                    html.Div(
                        "Instructions:",
                        style={
                            'font-weight': 'bold',
                            'font-size': '24px',
                            'margin-top': '40px',
                            'color': '#5D6D7E'
                        }
                    )
                )
                children.append(
                    html.Div(
                        rating_config["instructions"],
                        style={
                            'margin': '20px 0',
                            'background-color': '#D5F5E3',
                            'padding': '20px',
                            'border-radius': '10px',
                            'font-size': '22px'
                        }
                    )
                )

            # Slider to represent the rating scale
            slider_id = {
                "type": "rating-slider",
                "index": f"{rating_config['name']}-{index}"
            }
            slider_key = f"{rating_config['name']}-{index}"

            # Setting default value if evaluator output exists
            if existing_human_evaluator:
                default_value = existing_human_evaluator.result if existing_human_evaluator else (
                    rating_config["scale"][0] + rating_config["scale"][1]
                ) / 2
                initial_slider_data[slider_key] = default_value
            else:
                default_value = None

            children.append(
                html.Div(
                    rating_config["name"],
                    style={
                        'font-size': '24px',
                        'margin-top': '40px',
                        'color': '#5D6D7E'
                    }
                )
            )
            scale_bar = dcc.Slider(
                min=rating_config["scale"][0],
                max=rating_config["scale"][1],
                id=slider_id,
                marks={
                    i: str(i)
                    for i in range(
                        int(rating_config["scale"][0]),
                        int(rating_config["scale"][1]) + 1
                    )
                },
                value=default_value if default_value else
                (rating_config["scale"][0] + rating_config["scale"][1]) /
                2,
                disabled=False
            )
            children.append(scale_bar)
    children.append(
        html.Button(
            'Save',
            id='save-button',
            style={
                'display': 'block',
                'margin': '40px auto',
                'padding': '10px 20px',
                'background-color': '#2E86C1',
                'color': 'white',
                'border': 'none',
                'border-radius': '5px',
                'cursor': 'pointer'
            }
        )
    )

    # Add the output-div here
    children.append(html.Div(id='output-div'))
    children.append(
        dcc.Store(id='slider-values-store', data=initial_slider_data)
    )

    return html.Div(
        children,
        style={
            'padding': '80px',
            'background-color': '#FCF3CF',
            'border-radius': '20px',
            'box-shadow': '0 8px 25px rgba(0, 0, 0, 0.1)',
            'font-family': 'Arial, sans-serif',
            'width': '90%',
            'margin': '2% auto'
        }
    )
