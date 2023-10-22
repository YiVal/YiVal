import base64
import io
import json
from typing import List

import pandas as pd  # type: ignore
from PIL import Image

from yival.schemas.experiment_config import GroupedExperimentResult


def sanitize_group_key(group_key: str):
    try:
        json_str = group_key.replace('example_id:', '"example_id":').replace(
            'content:', '"content":'
        ).replace('expected_result:', '"expected_result":')
        escaped_json_str = json_str.replace("\n", "\\n").replace("\t", "\\t")
        valid_json_str = escaped_json_str.replace(": None", ": null")
        data_dict = json.loads(valid_json_str)
        content = data_dict['content']
        if content:
            items = [str(value) for value in content.values()]
            group_key = ", ".join([item.strip() for item in items])
            return group_key
    except Exception:
        return group_key
    return ""


def sanitize_column_name(name):
    return name.replace('"', '').replace(':', '')


import pandas as pd


def highlight_best_values(df: pd.DataFrame, *cols) -> list:

    def numeric_col_best_value_style(col: str) -> dict:
        """Return style for best value in a numeric column."""
        best_val = df[col].min()
        return {
            'if': {
                'filter_query': f'{{{col}}} eq {best_val}',
                'column_id': col
            },
            'border': '2px solid red'
        }

    def non_numeric_col_best_value_style(col: str) -> dict:
        """Return style for best value in a non-numeric column containing
           metrics."""
        metrics_values = df[col].str.extractall(r":\s?(\d+\.\d+)"
                                                ).astype(float)
        if not metrics_values.empty:
            best_val = metrics_values[0].min()
            return {
                'if': {
                    'filter_query': f'{{{col}}} contains "{best_val}"',
                    'column_id': col
                },
                'border': '2px solid red'
            }
        return {}

    styles = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            styles.append(numeric_col_best_value_style(col))
        else:
            style = non_numeric_col_best_value_style(col)
            if style:  # Check if the style was generated for the non-numeric column
                styles.append(style)

    return styles


def image_to_base64(image: Image.Image) -> str:
    '''Converts an image to base64 string.'''
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def process_raw_output(raw_output):
    if isinstance(raw_output, list) and all(
        isinstance(item, Image.Image) for item in raw_output
    ):
        return [image_to_base64(image) for image in raw_output]
    else:
        return raw_output


def generate_group_key_combination_data(
    group_experiment_results: List[GroupedExperimentResult]
) -> pd.DataFrame:
    data_list = []
    all_combos = set()
    for group in group_experiment_results:
        group_key = group.group_key
        group_key = sanitize_group_key(group_key)
        if group_key == "":
            pass
        row_dict = {"Test Data": group_key}
        for exp_result in group.experiment_results:
            combo_str = sanitize_column_name(
                str(exp_result.combination).replace("{", "").replace("}", "")
            )
            nested_output = {
                "text_output":
                process_raw_output(exp_result.raw_output.text_output),
                "image_output":
                process_raw_output(
                    getattr(exp_result.raw_output, 'image_output', None)
                ),
                "video_output":
                process_raw_output(
                    getattr(exp_result.raw_output, 'video_output', None)
                ),
                "evaluator_outputs":
                "\n".join([
                    f"{e.name} : {e.display_name} = {e.result}"
                    for e in exp_result.evaluator_outputs
                ]) if exp_result.evaluator_outputs else None
            }
            video_text = ''
            video_output = nested_output['video_output']
            if video_output is not None:
                for video_url in nested_output['video_output']:
                    video_text += f"<yival_video_output>{video_url}</yival_video_output>"

            formatted_output = f"<yival_raw_output>{nested_output['text_output']}</yival_raw_output>{nested_output['image_output']}{video_text}\n{nested_output['evaluator_outputs']}"
            row_dict[combo_str] = formatted_output
            all_combos.add(combo_str)
        data_list.append(row_dict)

    df = pd.DataFrame(data_list)
    # Ensure all combo columns exist
    for combo in all_combos:
        if combo not in df.columns:
            df[combo] = None

    return df


def generate_heatmap_style(df, *cols):
    styles = []

    light_positive = (173, 216, 230)
    dark_positive = (70, 130, 180)

    light_negative = (255, 245, 235)
    dark_negative = (255, 150, 140)

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val = df[col].min()
            max_val = df[col].max()
            range_val = max_val - min_val if min_val != max_val else 1
            for val in df[col].unique():
                normalized = (val - min_val) / range_val

                if col in ["Average Token Usage", "Average Latency"]:
                    bg_color = tuple(
                        int(
                            light_negative[i] + normalized *
                            (dark_negative[i] - light_negative[i])
                        ) for i in range(3)
                    )
                else:
                    bg_color = tuple(
                        int(
                            light_positive[i] + normalized *
                            (dark_positive[i] - light_positive[i])
                        ) for i in range(3)
                    )

                bg_color_str = f"rgb({bg_color[0]}, {bg_color[1]}, {bg_color[2]})"
                styles.append({
                    'if': {
                        'filter_query': f'{{{col}}} eq {val}',
                        'column_id': col
                    },
                    'backgroundColor': bg_color_str
                })
        else:  # For aggregated metrics columns and evaluator outputs
            metrics_values = df[col].str.extractall(r":\s?(\d+\.\d+)"
                                                    ).astype(float)
            if not metrics_values.empty:
                min_val = metrics_values[0].min()
                max_val = metrics_values[0].max()
                range_val = max_val - min_val if min_val != max_val else 1
                for _, val in metrics_values[0].items():
                    normalized = (val - min_val) / range_val
                    bg_color = tuple(
                        int(
                            light_positive[i] + normalized *
                            (dark_positive[i] - light_positive[i])
                        ) for i in range(3)
                    )

                    bg_color_str = f"rgb({bg_color[0]}, {bg_color[1]}, {bg_color[2]})"
                    styles.append({
                        'if': {
                            'filter_query': f'{{{col}}} contains "{val}"',
                            'column_id': col
                        },
                        'backgroundColor': bg_color_str
                    })
    return styles
