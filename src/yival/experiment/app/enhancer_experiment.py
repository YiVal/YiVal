import json
import shutil
import textwrap
import urllib.parse
from typing import List

import pandas as pd  # type: ignore
from dash import dcc, html  # type: ignore
from pydub import AudioSegment

from yival.experiment.app.experiment_result import combo_aggregated_metrics_layout
from yival.experiment.app.utils import generate_legend, sanitize_column_name
# fixed the ImportError: attempted relative import with no known parent package
# from relative import to absolute import
from yival.schemas.experiment_config import CombinationAggregatedMetrics, GroupedExperimentResult

# ffmpeg_executable = "/opt/homebrew/Cellar/ffmpeg/6.0_1/bin/ffmpeg"
ffmpeg_executable = shutil.which("ffmpeg")
AudioSegment.converter = ffmpeg_executable

def generate_combo_metrics_data(
        combo_metrics: List[CombinationAggregatedMetrics],
        group_experiment_results: List[GroupedExperimentResult]
    ) -> pd.DataFrame:
    print("group_experiment_results")
    print(group_experiment_results)
    data = []
    for metric in combo_metrics:
        row = {
            "Prompt Variations":
            "\n".join(
                textwrap.wrap(
                    str(metric.combo_key).replace('"',
                                                    "").replace("'", ""), 90
                )
            )
        }

        for k, v in metric.aggregated_metrics.items():
            row[k] = ', '.join([f"{m.name}: {m.value}" for m in v])
        row['Average Token Usage(Cost Proportional)'] = str(
            metric.average_token_usage
        )
        row['Average Latency'] = str(metric.average_latency)

        if metric.combine_evaluator_outputs:
            for e in metric.combine_evaluator_outputs:
                column_name = f"{e.name} Output"
                if e.display_name:
                    column_name += f" ({e.display_name})"
                row[f"{e.name} Output"] = e.result

        sample_count = 0
        for group in group_experiment_results:
            matching_results = [
                exp_result.raw_output
                for exp_result in group.experiment_results
                if json.dumps(exp_result.combination) == metric.combo_key
            ]
            if matching_results:

                json_str = group.group_key.replace(
                    'example_id:', '"example_id":'
                ).replace('content:', '"content":').replace(
                    'expected_result:', '"expected_result":'
                )
                escaped_json_str = json_str.replace("\n", "\\n"
                                                    ).replace("\t", "\\t")
                valid_json_str = escaped_json_str.replace(
                    ": None", ": null"
                )
                try:
                    data_dict = json.loads(valid_json_str)
                    content = data_dict['content']
                    if content:
                        items = [str(value) for value in content.values()]
                        group_key = ", ".join([
                            item.strip() for item in items
                        ])
                    else:
                        group_key = ""
                except Exception as e:
                    group_key = group.group_key
                group_key = sanitize_column_name(group_key)
                # if sample_count < 3:
                #     row[f"Sample {sample_count + 1} ({group_key})"
                #         ] = matching_results[0]
                #     sample_count += 1
                # else:
                #     break
                row[f"Sample {sample_count + 1} ({group_key})"
                    ] = matching_results[0]
                sample_count += 1

        data.append(row)
    print("data")
    print(data)
    for index, row in enumerate(data):
        row["Iteration"] = index
    df = pd.DataFrame(data)
    column_order = ["Iteration"
                    ] + [col for col in df if col != "Iteration"]
    df = df[column_order]
    if 'Average Token Usage(Cost Proportional)' in df:
        df['Average Token Usage(Cost Proportional)'] = pd.to_numeric(
            df['Average Token Usage(Cost Proportional)'], errors='coerce'
        )
    if 'Average Latency' in df:
        df['Average Latency'] = pd.to_numeric(
            df['Average Latency'], errors='coerce'
        )
    return df

def enhancer_experiment_results_layout(experiment_data):
    if not experiment_data.enhancer_output:
        return html.Div([html.H3("No Enhancer Output data available.")])

    df_enhancer = generate_combo_metrics_data(
        experiment_data.enhancer_output.combination_aggregated_metrics,
        experiment_data.enhancer_output.group_experiment_results
    )

    csv_string = df_enhancer.to_csv(index=False, encoding='utf-8')
    csv_data_url = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(
        csv_string
    )

    return html.Div([
        html.H3(
            "Enhancer Experiment Results Analysis",
            style={'textAlign': 'center'}
        ),
        html.P(
            "*Note: iteration 0 is the user task input, other iterations are YiVal autotune results.",
            style={
                'textAlign': 'center',
                'color': 'grey'
            }
        ),
        combo_aggregated_metrics_layout(df_enhancer, experiment_data),
        html.Hr(),
        generate_legend(),
        html.A(
            'Export to CSV',
            id='export-link-enhancer-experiment-results',
            download="enhancer_experiment_results.csv",
            href=csv_data_url,
            target="_blank"
        ),
        html.Br(),
        dcc.Link('Go to Data Analysis', href='/data-analysis'),
        html.Br(),
        dcc.Link(
            'Go to Detailed Experiment Results', href='/group-key-combo'
        ),
        html.Br(),
        dcc.Link(
            'Go to Enhancer Detailed Experiment Results',
            href='/enhancer-group-key-combo'
        ),
        html.Br()
    ])