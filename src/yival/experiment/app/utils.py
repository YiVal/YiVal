from typing import List

import pandas as pd  # type: ignore

from yival.schemas.experiment_config import GroupedExperimentResult


def sanitize_group_key(group_key):
    import re
    pattern = r'content:\s*\{(.*?)\}'
    match = re.search(pattern, group_key)

    if match:
        content = match.group(1).strip()
        items = content.split(",")
        group_key = ", ".join([item.strip() for item in items])
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
        """Return style for best value in a non-numeric column containing metrics."""
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
                "raw_output":
                exp_result.raw_output,
                "evaluator_outputs":
                "\n".join([
                    f"{e.name} : {e.display_name} = {e.result}"
                    for e in exp_result.evaluator_outputs
                ]) if exp_result.evaluator_outputs else None
            }
            formatted_output = f"raw_output: {nested_output['raw_output']}\n{nested_output['evaluator_outputs']}"
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
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val = df[col].min()
            max_val = df[col].max()
            range_val = max_val - min_val

            for val in df[col].unique():
                normalized = (val - min_val) / range_val

                # Check if the column is "Average Token Usage" or "Average Latency"
                if col in ["Average Token Usage", "Average Latency"]:
                    bg_color = f"rgb({255*normalized}, {255*(1-normalized)}, 150)"
                else:
                    bg_color = f"rgb({255*(1-normalized)}, {255*normalized}, 150)"

                styles.append({
                    'if': {
                        'filter_query': f'{{{col}}} eq {val}',
                        'column_id': col
                    },
                    'backgroundColor': bg_color
                })
        else:  # For aggregated metrics columns and evaluator outputs
            metrics_values = df[col].str.extractall(r":\s?(\d+\.\d+)"
                                                    ).astype(float)
            if not metrics_values.empty:
                min_val = metrics_values[0].min()
                max_val = metrics_values[0].max()
                range_val = max_val - min_val
                for _, val in metrics_values[0].items():
                    normalized = (val - min_val) / range_val
                    bg_color = f"rgb({255*(1-normalized)}, {255*normalized}, 150)"
                    styles.append({
                        'if': {
                            'filter_query': f'{{{col}}} contains "{val}"',
                            'column_id': col
                        },
                        'backgroundColor': bg_color
                    })
    return styles
