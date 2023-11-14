# type: ignore
import ast
import json
import os
import shutil
import re
import subprocess
import textwrap
import threading
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import dash  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
from dash import dcc, html  # type: ignore
from dash.dependencies import ALL, MATCH, Input, Output, State
from pydub import AudioSegment
from pyngrok import ngrok
from termcolor import colored

from yival.experiment.app.data_analysis import data_analysis_layout
from yival.experiment.app.detailed_results import combo_page_layout
from yival.experiment.app.enhancer_detailed import enhancer_combo_page_layout
from yival.experiment.app.enhancer_experiment import (
    enhancer_experiment_results_layout,
    generate_combo_metrics_data,
)
from yival.experiment.app.experiment_result import experiment_results_layout
from yival.experiment.app.hexagram import HEXAGRAMS, generate_hexagram_figure
from yival.experiment.app.html_structurer import determine_relative_color, handle_output
from yival.experiment.app.human_rating import (
    display_group_experiment_result_layout,
    get_group_experiment_result_from_hash,
)
from yival.experiment.app.interactive import input_page_layout
from yival.experiment.rate_limiter import RateLimiter
from yival.experiment.utils import (
    call_function_from_string,
    generate_experiment,
    get_function_args,
    run_single_input,
)
# fixed the ImportError: attempted relative import with no known parent package
# from relative import to absolute import
from yival.schemas.common_structures import InputData
from ...common.auto_cofig_utils import auto_generate_config
from ...schemas.common_structures import InputData
from ...schemas.experiment_config import (
    CombinationAggregatedMetrics,
    EvaluatorOutput,
    Experiment,
    ExperimentConfig,
    ExperimentResult,
)
from ..rate_limiter import RateLimiter
from ..utils import (
    call_function_from_string,
    generate_experiment,
    get_function_args,
    run_single_input,
)
from .hexagram import HEXAGRAMS, generate_hexagram_figure

ffmpeg_executable = shutil.which("ffmpeg")
AudioSegment.converter = ffmpeg_executable

def create_dash_app(
    experiment_data: Experiment, experiment_config: ExperimentConfig,
    function_args: Dict[str, Any], all_combinations, state, logger, evaluator,
    interactive_mode
):

    def parallel_task(data_point, all_combinations, logger, evaluator):
        """Task to be run in parallel for processing data points."""
        RateLimiter(60 / 60)()  # Ensure rate limit
        return run_single_input(
            data_point,
            experiment_config,
            all_combinations=all_combinations,
            logger=logger,
            evaluator=evaluator
        )

   

    def generate_navigation():
        return dbc.NavbarSimple(
            children=[
                dbc.NavItem(
                    dbc.NavLink(
                        "Experiment Results Analysis",
                        href="/experiment-results"
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Detailed Experiment Results", href="/group-key-combo"
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Enhancer Experiment Results Analysis",
                        href="/enhancer-experiment-results"
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Enhancer Detailed Experiment Results",
                        href="/enhancer-group-key-combo"
                    )
                ),
                dbc.NavItem(
                    dbc.Button(
                        "Export Data",
                        id="export-btn",
                        color="primary",
                        className="ml-2"
                    )
                ),
                dbc.NavItem(dbc.NavLink(
                    "Playground",
                    href="/interactive",
                )),
                dbc.NavItem(
                    dbc.NavLink("Data Analysis", href="/data-analysis")
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Use Best Combinations",
                        href="/use-best-result",
                    )
                ),
            ],
            brand="YiVal",
            brand_href="/",
            color="primary",
            dark=True,
        )

    def index_page():
        return html.Div([
            html.H1("Yijing (I Ching)"),
            html.Button('Cast Your Fortune', id='cast-fortune-btn'),
            html.Div(id='hexagram-container')
        ])

    def use_best_result_layout():
        if experiment_data.enhancer_output:
            best_combination = experiment_data.enhancer_output.selection_output.best_combination
        elif experiment_data.selection_output:
            best_combination = experiment_data.selection_output.best_combination
        else:
            best_combination = experiment_data.group_experiment_results[
                0].experiment_results[0].combination
        best_combination = str(best_combination)

        return html.Div([
            dbc.Row([
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.
                                    H4("Parameters", className="text-center"),
                                    className="bg-light"
                                ),
                                dbc.CardBody([
                                    html.Div([
                                        dbc.Label(
                                            key,
                                            className="mr-2 font-weight-bold",
                                            width=4
                                        ),
                                        dbc.Col(
                                            dbc.Input(
                                                id=f"best-input-{key}",
                                                type=value,
                                                placeholder=key
                                            ),
                                            width=8
                                        )
                                    ],
                                             className=
                                             "d-flex align-items-center mb-4")
                                    for key, value in
                                    list(function_args.items())[:-1]
                                ],
                                             className="p-4"),
                                dbc.Button(
                                    "Run",
                                    id="best-result-btn",
                                    color="primary",
                                    className="mt-2 mb-4 w-100"
                                ),
                                # Enhanced Section for Combinations Selection
                                html.Hr(),
                                html.Div([
                                    html.H5(
                                        "Best Combination",
                                        className="text-center mt-2"
                                    ),
                                    html.P(
                                        "This is the best combination from the available combinations.",
                                        className="text-muted small text-center"
                                    ),
                                    html.P(
                                        best_combination,
                                        id="best-combination",
                                        style={
                                            "border": "1px solid #ced4da",
                                            "border-radius": "4px",
                                            "padding": "5px",
                                            "margin-bottom": "20px"
                                        }
                                    )
                                ],
                                         style={"padding": "10px"}),
                            ],
                            className="m-4 shadow-sm rounded"
                        ),
                    ],
                    width=3
                ),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H4("Results", className="text-center"),
                            className="bg-light"
                        ),
                        dcc.Loading(
                            id="loading-results",
                            type="default",
                            children=html.
                            Div(id="best-results-section", className="p-4")
                        )
                    ],
                             className="m-4 shadow-sm rounded")
                ],
                        width=9)
            ]),
            dbc.Container(fluid=True, className="p-3")
        ])

    
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

    app.config.suppress_callback_exceptions = True

    df = generate_combo_metrics_data(
        experiment_data.combination_aggregated_metrics,
        experiment_data.group_experiment_results
    )

    @app.callback(
        dash.dependencies.Output('page-content', 'children'),
        [dash.dependencies.Input('url', 'pathname')]
    )
    def display_page(pathname):
        if pathname.startswith('/rating-result/'):
            hashed_group_key = pathname.split('/')[-1]
            is_from_enhancer = "?source=enhancer" in hashed_group_key
            hashed_group_key = hashed_group_key.replace('?source=enhancer', '')
            return display_group_experiment_result_layout(
                hashed_group_key, experiment_config, experiment_data, is_from_enhancer
            )
        elif pathname == '/experiment-results':
            return experiment_results_layout(df, experiment_data)
        elif pathname == '/group-key-combo':
            return combo_page_layout(experiment_data)
        elif pathname == '/enhancer-experiment-results':
            return enhancer_experiment_results_layout(experiment_data)
        elif pathname == '/enhancer-group-key-combo':
            return enhancer_combo_page_layout(experiment_data)
        elif pathname == '/interactive':
            return input_page_layout(experiment_data, function_args)
        elif pathname == '/use-best-result':
            return use_best_result_layout()
        elif pathname == '/data-analysis':
            return data_analysis_layout(df)
        else:
            return index_page()

    @app.callback(
        Output('comparative-scatter-plot-token', 'figure'),
        [Input('evaluator-dropdown-token', 'value')]
    )
    def update_comparative_scatter_token(selected_evaluator):
        if selected_evaluator is None:
            fig = px.scatter(title="No selected_evaluator")
            return fig
        return px.scatter(
            df,
            x='Average Token Usage(Cost Proportional)',
            y=selected_evaluator,
            title=
            f'Comparative Scatter plot of Average Token Usage(Cost Proportional) vs {selected_evaluator}',
            size_max=15
        )

    @app.callback(
        Output('comparative-scatter-plot-latency', 'figure'),
        [Input('evaluator-dropdown-latency', 'value')]
    )
    def update_comparative_scatter_latency(selected_evaluator):
        if selected_evaluator is None:
            fig = px.scatter(title="No selected_evaluator")
            return fig
        return px.scatter(
            df,
            x='Average Latency',
            y=selected_evaluator,
            title=
            f'Comparative Scatter plot of Average Latency vs {selected_evaluator}',
            size_max=15
        )

    @app.callback(
        Output('hexagram-container', 'children'),
        [Input('cast-fortune-btn', 'n_clicks')]
    )
    def update_hexagram(n_clicks):
        import random
        hexagram = random.choice(HEXAGRAMS)
        return [
            generate_hexagram_figure(hexagram["figure"]),
            html.H4(hexagram["name"]),
            html.P(hexagram["description"]),
            html.P(
                hexagram["reading"],
                style={
                    "color": "blue",
                    "fontStyle": "italic"
                }
            )
        ]

    @app.callback(
        Output('correlation-coefficient', 'children'),
        [Input('evaluator-dropdown-token', 'value')]
    )
    def display_correlation_coefficient(selected_evaluator):
        try:
            # Create a temporary variable to hold numerical data
            if df[selected_evaluator
                  ].dtype == 'object':  # if it's a string type
                # Extract the numerical part from each entry
                temp_evaluator_data = df[selected_evaluator].str.extract(
                    '(\d+\.\d+)'
                ).astype(float)
            else:
                # If it's already numerical, use it as is
                temp_evaluator_data = df[selected_evaluator]

            # Ensure 'Average Token Usage' is also numerical
            temp_avg_token_usage = pd.to_numeric(
                df['Average Token Usage(Cost Proportional)'], errors='coerce'
            )

            # Check if the columns exist and are not null, and if their lengths match
            if temp_avg_token_usage is not None and temp_evaluator_data is not None and len(
                temp_avg_token_usage
            ) == len(temp_evaluator_data):
                correlation = temp_avg_token_usage.corr(temp_evaluator_data)
                return f"Correlation between Average Token Usage(Cost Proportional) and {selected_evaluator}: {correlation:.2f}"
            else:
                return "Data not available for correlation calculation."

        except Exception as e:
            return f"An error occurred: {str(e)}"

    @app.callback(
        Output('slider-values-store', 'data'),
        [Input({
            'type': 'rating-slider',
            'index': ALL
        }, 'value')], [State('slider-values-store', 'data')],
        prevent_initial_call=True
    )
    def update_slider_store(slider_values, current_data):
        # The IDs of triggered inputs
        ctx = dash.callback_context

        triggered_slider_ids = [
            json.loads(t['prop_id'].split('.')[0])['index']
            for t in ctx.triggered
        ]
        all_slider_ids = [
            json.loads(prop_id.split('.')[0])['index']
            for prop_id in ctx.inputs.keys()
        ]

        # Create a dictionary to map slider IDs to their values
        slider_id_to_value = dict(zip(all_slider_ids, slider_values))

        for slider_id in triggered_slider_ids:
            current_data[slider_id] = slider_id_to_value[slider_id]

        return current_data

    @app.callback(
        Output('output-div', 'children'), [
            Input('save-button', 'n_clicks'),
            State('current-group-key', 'value'),
            State('slider-values-store', 'data'),
            State('is-from-enhancer', 'data')
        ]
    )  # We'll handle the dynamic State components inside the function itself
    def update_output(
        n_clicks, hashed_group_key, slider_values_store, is_from_enhancer
    ):
        if not n_clicks:
            return dash.no_update

        # 2. Determine the Current Group
        group_result = get_group_experiment_result_from_hash(hashed_group_key, experiment_data)
        if not group_result:
            return "Error fetching group result."

        for index, exp_result in enumerate(group_result.experiment_results):
            for rating_config in experiment_config["human_rating_configs"]:
                slider_key = f"{rating_config['name']}-{index}"
                if slider_key in slider_values_store:
                    slider_value = slider_values_store[slider_key]
                    existing_output = next((
                        e for e in exp_result.evaluator_outputs
                        if e.name == "human_evaluator"
                        and e.display_name == rating_config['name']
                    ), None)
                    if existing_output:
                        existing_output.result = slider_value
                    else:
                        new_output = EvaluatorOutput(
                            name="human_evaluator",
                            result=slider_value,
                            display_name=rating_config['name'],
                            metric_calculators=[{
                                'method': 'AVERAGE'
                            }]
                        )
                        exp_result.evaluator_outputs.append(new_output)

        if is_from_enhancer:
            results = []
            for e in experiment_data.enhancer_output.group_experiment_results:
                for r in e.experiment_results:
                    results.append(r)
            r = generate_experiment(
                results=results,
                evaluator=None,
                evaluate_all=False,
                evaluate_group=False
            )
            experiment_data.enhancer_output.combination_aggregated_metrics = r.combination_aggregated_metrics
        else:
            results = []
            for e in experiment_data.group_experiment_results:
                for r in e.experiment_results:
                    results.append(r)
            r = generate_experiment(
                results=results,
                evaluator=None,
                evaluate_all=False,
                evaluate_group=False
            )
            experiment_data.combination_aggregated_metrics = r.combination_aggregated_metrics
        return "Data saved successfully!"

    @app.callback(
        dash.dependencies.Output('url', 'pathname'), [
            dash.dependencies.Input('group-key-combo-table', 'active_cell'),
            dash.dependencies.Input('group-key-combo-table', 'data'),
            dash.dependencies.Input('current-page-context', 'children')
        ]
    )
    def navigate_to_hashed_page(active_cell, table_data, page_context):
        if page_context is None or page_context == dash.no_update:
            page_context = 'default'
        if active_cell:
            row = active_cell["row"]
            col_id = active_cell["column_id"]
            if col_id == "Test Data":
                hashed_group_key = table_data[row]["Hashed Group Key"]
                if page_context == 'enhancer':
                    return f'/rating-result/{hashed_group_key}?source=enhancer'
                return f'/rating-result/{hashed_group_key}'
        return dash.no_update

    @app.callback(
        Output("export-data-modal", "is_open"),
        [
            Input("export-btn", "n_clicks"),
            Input("close-export-modal", "n_clicks"),
            Input("confirm-export", "n_clicks")
        ],
        [State("export-data-modal", "is_open")],
    )
    def toggle_modal(n1, n2, n3, is_open):
        if n1 or n2 or n3:
            return not is_open
        return is_open

    @app.callback(
        Output('button-click-output', 'children'),
        Input('confirm-export', 'n_clicks'), State('file-path-input', 'value')
    )
    def export_callback(n, file_path):
        if n:
            import pickle
            with open(file_path, "wb") as f:
                pickle.dump(experiment_data, f)
            return f"Data would be exported to: {file_path}"
        return dash.no_update

    all_results: List[html.Div] = []
    best_all_results: List[html.Div] = []

    @app.callback(
        Output("results-section", "children"),
        Input("interactive-btn", "n_clicks"),
        [State(f"input-{key}", "value") for key in function_args.keys()] + [
            State("combinations-select", "value"),
            State("enhancer-toggle", "value")
        ],
        prevent_initial_call=True
    )
    def update_results(n_clicks, *input_values_and_combinations_and_toggle):
        if not n_clicks:
            return []
        *input_values, selected_combinations_str, use_enhancer = input_values_and_combinations_and_toggle
        use_enhancer = "enhancer" in use_enhancer if use_enhancer else False
        if selected_combinations_str is None:
            return html.Div(
                "Please select at least one combination.",
                style={"color": "red"}
            )

        selected_combinations = [
            ast.literal_eval(combo_str)
            for combo_str in selected_combinations_str
        ]

        missing_fields = [
            key for i, key in enumerate(function_args.keys())
            if input_values[i] is None
            and key != "yival_expected_result (Optional)"
        ]
        if missing_fields:
            return html.Div(
                f"Please fill out the following required fields: {', '.join(missing_fields)}",
                style={"color": "red"}
            )

        content = {}
        i = 0
        expected_result = None
        for k, v in function_args.items():
            if k == "yival_expected_result (Optional)" and input_values[
                i] is not None:
                expected_result = input_values[i]
            else:
                if input_values[i] is not None:
                    content[k] = input_values[i]
            i += 1

        if experiment_config["custom_function"
                             ] == "demo.complete_task.complete_task":
            content["task"] = selected_combinations[0]['task']
        input_data = InputData(
            content=content, expected_result=expected_result
        )
        results: List[ExperimentResult] = []
        with ThreadPoolExecutor() as executor:
            for res in executor.map(
                parallel_task, [input_data], [selected_combinations], [logger],
                [evaluator]
            ):
                results.extend(res)

        if interactive_mode:
            ress = []
            for g in experiment_data.group_experiment_results:
                for r in g.experiment_results:
                    ress.append(r)
            ress.extend(results)
            updated_experiment = generate_experiment(ress, evaluator)
            experiment_data.group_experiment_results = updated_experiment.group_experiment_results
            experiment_data.combination_aggregated_metrics = updated_experiment.combination_aggregated_metrics
        all_metrics = {
            "Latency": [result.latency for result in results],
            "Token Usage": [result.token_usage for result in results]
        }

        # Extracting numeric evaluator outputs
        for result in results:
            for output in result.evaluator_outputs:
                if isinstance(output.result, (int, float)):
                    if output.name not in all_metrics:
                        all_metrics[output.name] = []
                    all_metrics[output.name].append(output.result)
                    
        current_result = [
            html.Div([
                html.H5(f"Result {i+1}"),
                html.Ul([
                    html.Li(f"Combination: {result.combination}"),
                    html.Li("Text Raw Output:"),
                    html.Div(
                        handle_output(result.raw_output.text_output),
                        className="raw-output"
                    ),
                    html.Li("Image Raw Output:"),
                    html.Div(
                        handle_output(result.raw_output.image_output),
                        className="raw-output"
                    ),
                    html.Li("Audio Raw Output:"),
                    html.Div(
                        handle_output(result.raw_output.audio_output),
                        className="raw-output"
                    ),
                    html.Li(
                        f"Latency: {result.latency} s",
                        style={
                            "color":
                            determine_relative_color(
                                result.latency, all_metrics["Latency"]
                            )
                        }
                    ),
                    html.Li(
                        f"Token Usage: {result.token_usage}",
                        style={
                            "color":
                            determine_relative_color(
                                result.token_usage, all_metrics["Token Usage"]
                            )
                        }
                    ),
                    html.Li("Evaluator Outputs:"),
                    html.Ul([
                        html.Li(
                            f"{output.name} ({output.display_name}): {output.result}",
                            style={
                                "color":
                                determine_relative_color(
                                    output.result,
                                    all_metrics.get(output.name, [])
                                ) if isinstance(output.result,
                                                (int, float)) else "black"
                            }
                        ) for output in result.evaluator_outputs
                    ])
                ])
            ]) for i, result in enumerate(results)
        ]

        input_summary = ", ".join([
            f"{key}: {value}"
            for key, value in zip(function_args.keys(), input_values)
        ])
        toggle_id = {"type": "toggle", "index": n_clicks}
        collapse_id = {"type": "collapse", "index": n_clicks}

        current_result_card = html.Div([
            dbc.Button(
                input_summary,
                id=toggle_id,
                className="mb-2 w-100",
                color="info"
            ),
            dbc.Collapse([
                item for sublist in [[res, html.Hr()]
                                     for res in current_result]
                for item in sublist
            ],
                         id=collapse_id,
                         is_open=True)
        ],
                                       className="mb-3")

        all_results.insert(0, current_result_card)

        return all_results

    @app.callback(
        Output("best-results-section", "children"),
        Input("best-result-btn", "n_clicks"),
        [
            State(f"best-input-{key}", "value")
            for key in list(function_args.keys())[:-1]
        ] + [State("best-combination", "children")],
        prevent_initial_call=True
    )
    def update_best_results(n_clicks, *input_values_and_combinations):
        if not n_clicks:
            return []
        *input_values, best_combination = input_values_and_combinations
        # Create a new InputData instance
        input_data = InputData(
            dict(zip(list(function_args.keys())[:-1], input_values))
        )
        missing_fields = [
            key for i, key in enumerate(list(function_args.keys())[:-1])
            if input_values[i] is None
            and key != "yival_expected_result (Optional)"
        ]
        if missing_fields:
            return html.Div(
                f"Please fill out the following required fields: {', '.join(missing_fields)}",
                style={"color": "red"}
            )

        state.active = True
        best_varation = json.loads(best_combination)
        for key in best_varation:
            best_varation[key] = [best_varation[key]]
        state.current_variations = best_varation

        if "custom_function" in experiment_config:
            if experiment_config["custom_function"
                                 ] == "demo.complete_task.complete_task":
                additional_data = {'task': best_combination}
                content = {**input_data.content, **additional_data}
                res = call_function_from_string(
                    experiment_config["custom_function"],
                    **content,
                    state=state
                )
            else:
                res = call_function_from_string(
                    experiment_config["custom_function"],
                    **input_data.content,
                    state=state
                )
        else:
            res = None
        print("res")
        print(res)
        best_current_result = [
            html.Div([
                html.Ul([
                    html.Li("Text Raw Output:"),
                    html.Div(
                        handle_output(res.text_output), className="raw-output"
                    ),
                ] + ([
                    html.Li("Image Raw Output:"),
                    html.Div(
                        handle_output(res.image_output),
                        className="raw-output"
                    )
                ] if res.image_output is not None else [])
                +([
                    html.Li("Audio Raw Output:"),
                    html.Div(
                        handle_output(res.audio_output),
                        className="raw-output"
                    )
                ] if res.audio_output is not None else []))
            ])
        ]

        input_summary = ", ".join([
            f"{key}: {value}" for key, value in
            zip(list(function_args.keys())[:-1], input_values)
        ])
        toggle_id = {"type": "toggle", "index": n_clicks}
        collapse_id = {"type": "collapse", "index": n_clicks}
        best_current_result_card = html.Div([
            dbc.Button(
                input_summary,
                id=toggle_id,
                className="mb-2 w-100",
                color="info"
            ),
            dbc.Collapse([
                item for sublist in [[res, html.Hr()]
                                     for res in best_current_result]
                for item in sublist
            ],
                         id=collapse_id,
                         is_open=True)
        ],
                                            className="mb-3")

        best_all_results.insert(0, best_current_result_card)
        return best_all_results

    def truncate_text(text, max_length=60):  # Adjust max_length as needed
        """Truncate text to a specified length and append ellipses."""
        return text if len(text) <= max_length else text[:max_length] + "..."

    @app.callback(
        Output("combinations-select", "options"),
        [Input("enhancer-toggle", "value")]
    )
    def update_combinations_options(use_enhancer):
        unique_combination = {}

        if "enhancer" in use_enhancer:
            # Use enhancer combinations
            for group in experiment_data.enhancer_output.group_experiment_results:
                for result in group.experiment_results:
                    if str(result.combination) not in unique_combination:
                        unique_combination[str(result.combination)
                                           ] = result.combination

        else:
            for group in experiment_data.group_experiment_results:
                for result in group.experiment_results:
                    if str(result.combination) not in unique_combination:
                        unique_combination[str(result.combination)
                                           ] = result.combination

            # Combine with all_combinations
            for combination in all_combinations:
                if str(combination) not in unique_combination:
                    unique_combination[str(combination)] = combination

        return [{
            "label": truncate_text(str(combo)),
            "value": str(combo)
        } for combo in unique_combination.values()]

    @app.callback(
        Output({
            "type": "collapse",
            "index": MATCH
        }, "is_open"),
        Input({
            "type": "toggle",
            "index": MATCH
        }, "n_clicks"),
        State({
            "type": "collapse",
            "index": MATCH
        }, "is_open"),
        prevent_initial_call=True
    )
    def toggle_collapse(n, is_open):
        return not is_open

    app.layout = html.Div(
        [
            html.Div(
                [
                    dcc.Location(id='url', refresh=False),
                    generate_navigation(),
                    html.Div(
                        id='page-content',
                        style={
                            'fontFamily': 'Arial, sans-serif',
                            'margin': '2% 10%',
                            'padding': '2% 3%',
                            'border': '1px solid #ddd',
                            'borderRadius': '5px',
                            'backgroundColor': '#f9f9f9',
                            'fontSize': '18px',
                            'boxShadow': '0 4px 8px 0 rgba(0, 0, 0, 0.1)',
                        }
                    )
                ],
                className="main-content",
                style={
                    'backgroundColor': '#f9f9f9',  # Light Grey
                    'padding': '20px'
                }
            ),
            dbc.Modal([
                dbc.ModalHeader("Export Data"),
                dbc.ModalBody([
                    html.
                    Label("Please enter the file path for exporting data:"),
                    dcc.Input(
                        id="file-path-input",
                        type="text",
                        placeholder="Enter file path..."
                    ),
                ]),
                dbc.ModalFooter([
                    dbc.Button(
                        "Close", id="close-export-modal", className="ml-auto"
                    ),
                    dbc.
                    Button("Export", id="confirm-export", className="ml-auto"),
                ]),
            ],
                      id="export-data-modal"),
            html.Div(id='button-click-output')
        ],
        className="main-wrapper"
    )

    return app


def create_input_app():
    default_task = "generate tiktok video title"
    default_context_info = "target_audience,content_summary"
    default_evaluation_aspects = ""

    def generate_navigation():
        return dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink(
                    "Create Task",
                    href="/create_task",
                )),
            ],
            brand="YiVal",
            brand_href="/",
            color="primary",
            dark=True,
        )

    def index_page():
        return html.Div([
            html.H1("Yijing (I Ching)"),
            html.Button('Cast Your Fortune', id='cast-fortune'),
            html.Div(id='hexagram-container')
        ])

    def input_task_layout():
        return html.Div([
            html.Label(
                '[?] What task would you like to set up? For example:',
                style={'margin': '10px'}
            ),
            dcc.Input(
                id='task',
                type='text',
                placeholder='Task',
                value=default_task,
                style={
                    'width': '100%',
                    'height': '50px',
                    'fontSize': '18px',
                    'margin': '10px'
                }
            ),
            html.Label(
                '[?] Provide input for the task, separated by comma. For example:',
                style={'margin': '10px'}
            ),
            dcc.Input(
                id='context_info',
                type='text',
                placeholder='Context Info',
                value=default_context_info,
                style={
                    'width': '100%',
                    'height': '50px',
                    'fontSize': '18px',
                    'margin': '10px'
                }
            ),
            html.Label(
                '[?] Please provide evaluation aspects (optional):',
                style={'margin': '10px'}
            ),
            dcc.Input(
                id='evaluation_aspects',
                type='text',
                placeholder='Evaluation Aspects (optional)',
                value=default_evaluation_aspects,
                style={
                    'width': '100%',
                    'height': '50px',
                    'fontSize': '18px',
                    'margin': '10px'
                }
            ),
            html.Button(
                'Submit',
                id='submit-button',
                n_clicks=0,
                style={
                    'fontSize': '18px',
                    'margin': '10px'
                }
            ),
            html.Div(id='output-div')
        ],
                        style={
                            'backgroundColor': '#f0f0f0',
                            'padding': '20px'
                        })

    app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        external_stylesheets=[dbc.themes.FLATLY]
    )

    @app.callback(
        Output('output-div', 'children'), [Input('submit-button', 'n_clicks')],
        [
            State('task', 'value'),
            State('context_info', 'value'),
            State('evaluation_aspects', 'value')
        ]
    )
    def update_output(n_clicks, task, context_info, evaluation_aspects):
        if n_clicks > 0:
            parameters = context_info.split(",")
            aspect = []
            if evaluation_aspects:
                aspect = evaluation_aspects.split(",")

            if task != default_task and context_info != default_context_info and evaluation_aspects != default_evaluation_aspects:
                auto_generate_config(task, parameters, aspect)
                print(
                    colored(
                        "\n[INFO][auto_gen] Generating configuration...",
                        "yellow"
                    )
                )
                subprocess.run([
                    "yival", "run", "auto_generated_config.yaml",
                    "--output_path=auto_generated.pkl"
                ])
            else:
                print(
                    colored(
                        "\n[INFO][auto_gen] Using default configuration...",
                        "yellow"
                    )
                )
                subprocess.run([
                    "yival", "run", "default_auto_generated_config.yaml",
                    "--output_path=default_auto_generated.pkl"
                ])

            return 'Configuration generated and yival run completed.'

    @app.callback(
        dash.dependencies.Output('page-content', 'children'),
        [dash.dependencies.Input('url', 'pathname')]
    )
    def display_page(pathname):
        if pathname == '/create_task':
            return input_task_layout()
        else:
            return index_page()

    @app.callback(
        Output('hexagram-container', 'children'),
        [Input('cast-fortune', 'n_clicks')]
    )
    def update_hexagram(n_clicks):
        import random
        hexagram = random.choice(HEXAGRAMS)
        return [
            generate_hexagram_figure(hexagram["figure"]),
            html.H4(hexagram["name"]),
            html.P(hexagram["description"]),
            html.P(
                hexagram["reading"],
                style={
                    "color": "blue",
                    "fontStyle": "italic"
                }
            )
        ]

    app.layout = html.Div(
        [
            dcc.Location(id='url', refresh=False),
            generate_navigation(),
            html.Div(
                id='page-content',
                style={
                    'fontFamily': 'Arial, sans-serif',
                    'margin': '2% 10%',
                    'padding': '2% 3%',
                    'border': '1px solid #ddd',
                    'borderRadius': '5px',
                    'backgroundColor': '#f9f9f9',
                    'fontSize': '18px',
                    'boxShadow': '0 4px 8px 0 rgba(0, 0, 0, 0.1)',
                }
            )
        ],
        className="main-content",
        style={
            'backgroundColor': '#f9f9f9',  # Light Grey
            'padding': '20px'
        }
    )

    return app


def display_input_dash(port=8073):
    app = create_input_app()
    threading.Thread(target=run_app, args=(app, False, port)).start()


def display_results_dash(
    experiment_data: Experiment,
    experiment_config,
    all_combinations,
    state,
    logger,
    evaluator,
    interactive=False,
    port=8074
):
    if experiment_data.enhancer_output:
        for group_result in experiment_data.enhancer_output.group_experiment_results:
            experiment_results = []
            seen = set()
            for r in group_result.experiment_results:
                if str(r.combination) in seen:
                    continue
                else:
                    seen.add(str(r.combination))
                    experiment_results.append(r)
            group_result.experiment_results = experiment_results
    function_args = get_function_args(
        experiment_config["custom_function"], experiment_config["dataset"]
    )
    function_args["yival_expected_result (Optional)"] = 'str'
    app = create_dash_app(
        experiment_data, experiment_config, function_args, all_combinations,
        state, logger, evaluator, interactive
    )
    threading.Thread(target=run_app, args=(app, False, port)).start()


def run_app(app, debug, port):
    if os.environ.get("ngrok", False):
        public_url = ngrok.connect(port)
        print(f"Access Yival from this public URL :{public_url}")
        app.run(debug=debug, port=port)
    else:
        app.run(debug=debug, port=port)
