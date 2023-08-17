# type: ignore

import ast
import hashlib
import textwrap
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

import dash  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
from dash import dash_table, dcc, html  # type: ignore
from dash.dependencies import ALL, MATCH, Input, Output, State

from yival.experiment.rate_limiter import RateLimiter
from yival.experiment.utils import (
    generate_experiment,
    get_function_args,
    run_single_input,
)
from yival.schemas.experiment_config import (
    CombinationAggregatedMetrics,
    EvaluatorOutput,
    Experiment,
    ExperimentConfig,
    ExperimentResult,
    GroupedExperimentResult,
)

from ...schemas.common_structures import InputData
from .hexagram import HEXAGRAMS, generate_hexagram_figure
from .utils import (
    generate_group_key_combination_data,
    generate_heatmap_style,
    highlight_best_values,
    sanitize_column_name,
    sanitize_group_key,
)


def create_dash_app(
    experiment_data: Experiment, experiment_config: ExperimentConfig,
    function_args: Dict[str, Any], all_combinations, state, logger, evaluator,
    interactive_mode
):

    def parallel_task(data_point, all_combinations, state, logger, evaluator):
        """Task to be run in parallel for processing data points."""
        RateLimiter(10 / 60)()  # Ensure rate limit
        return run_single_input(
            data_point,
            experiment_config,
            all_combinations=all_combinations,
            state=state,
            logger=logger,
            evaluator=evaluator
        )

    def get_group_experiment_result_from_hash(hashed_group_key):
        for group_result in experiment_data.group_experiment_results:
            group_key = sanitize_group_key(group_result.group_key)
            if hashlib.sha256(group_key.encode()
                              ).hexdigest() == hashed_group_key:
                return group_result
        for group_result in experiment_data.improver_output.group_experiment_results:
            group_key = sanitize_group_key(group_result.group_key)
            if hashlib.sha256(group_key.encode()
                              ).hexdigest() == hashed_group_key:
                return group_result
        return None

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
                    dbc.NavLink("Data Analysis", href="/data-analysis")
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Detailed Test Results", href="/group-key-combo"
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Improver Experiment Results Analysis",
                        href="/improver-experiment-results"
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Improver Detailed Test Results",
                        href="/improver-group-key-combo"
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
                dbc.NavItem(
                    dbc.NavLink(
                        "Interactive Mode",
                        href="/interactive",
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

    def generate_combo_metrics_data(
        combo_metrics: List[CombinationAggregatedMetrics],
        group_experiment_results: List[GroupedExperimentResult]
    ) -> pd.DataFrame:
        data = []
        for metric in combo_metrics:
            row = {
                "Combo Key":
                "\n".join(
                    textwrap.wrap(
                        str(metric.combo_key).replace('"',
                                                      "").replace("'", ""), 90
                    )
                )
            }

            for k, v in metric.aggregated_metrics.items():
                row[k] = ', '.join([f"{m.name}: {m.value}" for m in v])
            row['Average Token Usage'] = str(metric.average_token_usage)
            row['Average Latency'] = str(metric.average_latency)

            if metric.evaluator_outputs:
                for e in metric.evaluator_outputs:
                    column_name = f"{e.name} Output"
                    if e.display_name:
                        column_name += f" ({e.display_name})"
                    row[f"{e.name} Output"] = e.result

            sample_count = 0
            for group in group_experiment_results:
                if sample_count >= 3:
                    break
                matching_results = [
                    exp_result.raw_output
                    for exp_result in group.experiment_results
                    if str(exp_result.combination) == metric.combo_key
                ]
                if matching_results:
                    import re
                    pattern = r'content:\s*\{(.*?)\}'
                    match = re.search(pattern, group.group_key)

                    if match:
                        content = match.group(1).strip()
                        items = content.split(",")
                        group_key = ", ".join([item.strip() for item in items])
                    else:
                        group_key = ""
                    group_key = sanitize_column_name(group_key)
                    row[f"Sample {sample_count + 1} ({group_key})"
                        ] = matching_results[0]
                    sample_count += 1

            data.append(row)
        df = pd.DataFrame(data)
        if 'Average Token Usage' in df:
            df['Average Token Usage'] = pd.to_numeric(
                df['Average Token Usage'], errors='coerce'
            )
        if 'Average Latency' in df:
            df['Average Latency'] = pd.to_numeric(
                df['Average Latency'], errors='coerce'
            )
        return df

    def experiment_results_layout():

        df = generate_combo_metrics_data(
            experiment_data.combination_aggregated_metrics,
            experiment_data.group_experiment_results
        )
        csv_string = df.to_csv(index=False, encoding='utf-8')
        csv_data_url = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(
            csv_string
        )
        return html.Div([
            html.H3(
                "Experiment Results Analysis", style={'textAlign': 'center'}
            ),
            combo_aggregated_metrics_layout(df),
            html.Hr(),
            html.A(
                'Export to CSV',
                id='export-link-experiment-results',
                download="experiment_results.csv",
                href=csv_data_url,
                target="_blank"
            ),
            html.Br(),
            dcc.Link('Go to Data Analysis', href='/data-analysis'),
            html.Br(),
            dcc.Link('Go to Detailed Test Results', href='/group-key-combo'),
            html.Br(),
            dcc.Link(
                'Go to Improver Experiment Results Analysis',
                href='/improver-experiment-results'
            ),
            html.Br(),
            dcc.Link(
                'Go to Improver Detailed Test Results',
                href='/improver-group-key-combo'
            ),
            html.Br()
        ])

    def data_analysis_layout():
        return html.Div([
            html.H3("Data Analysis", style={'textAlign': 'center'}),
            analysis_layout(df),
            html.Hr(),
            dcc.Link(
                'Go back to Experiment Results Analysis',
                href='/experiment-results'
            ),
            html.Br(),
            dcc.Link('Go to Detailed Test Results', href='/group-key-combo'),
            html.Br(),
            dcc.Link(
                'Go to Improver Experiment Results Analysis',
                href='/improver-experiment-results'
            ),
            html.Br(),
            dcc.Link(
                'Go to Improver Detailed Test Results',
                href='/improver-group-key-combo'
            ),
            html.Br()
        ])

    def combo_page_layout():
        return html.Div([
            html.H3("Detailed Test Results", style={'textAlign': 'center'}),
            group_key_combination_layout(
                experiment_data.group_experiment_results
            ),
            dcc.Link(
                'Go to Improver Experiment Results Analysis',
                href='/improver-experiment-results'
            ),
            html.Br(),
            dcc.Link(
                'Go to Improver Detailed Test Results',
                href='/improver-group-key-combo'
            ),
            html.Br(),
            html.Hr(),
            html.Div(
                id='current-page-context',
                style={'display': 'none'},
                children='default'
            )
        ])

    def improver_experiment_results_layout():
        if not experiment_data.improver_output:
            return html.Div([html.H3("No Improver Output data available.")])

        df_improver = generate_combo_metrics_data(
            experiment_data.improver_output.combination_aggregated_metrics,
            experiment_data.improver_output.group_experiment_results
        )

        csv_string = df_improver.to_csv(index=False, encoding='utf-8')
        csv_data_url = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(
            csv_string
        )

        return html.Div([
            html.H3(
                "Improver Experiment Results Analysis",
                style={'textAlign': 'center'}
            ),
            combo_aggregated_metrics_layout(df_improver),
            html.Hr(),
            html.A(
                'Export to CSV',
                id='export-link-improver-experiment-results',
                download="improver_experiment_results.csv",
                href=csv_data_url,
                target="_blank"
            ),
            html.Br(),
            dcc.Link('Go to Data Analysis', href='/data-analysis'),
            html.Br(),
            dcc.Link('Go to Detailed Test Results', href='/group-key-combo'),
            html.Br(),
            dcc.Link(
                'Go to Improver Detailed Test Results',
                href='/improver-group-key-combo'
            ),
            html.Br()
        ])

    def analysis_layout(df):
        evaluator_outputs = [col for col in df.columns if "Output" in col]

        return html.Div([
            html.Div([
                dcc.Dropdown(
                    id='evaluator-dropdown-token',
                    options=[{
                        'label': evaluator,
                        'value': evaluator
                    } for evaluator in evaluator_outputs],
                    value=evaluator_outputs[0] if evaluator_outputs else None,
                    multi=False
                ),
                dcc.Graph(id='comparative-scatter-plot-token')
            ],
                     className="six columns"),
            html.Div([
                dcc.Dropdown(
                    id='evaluator-dropdown-latency',
                    options=[{
                        'label': evaluator,
                        'value': evaluator
                    } for evaluator in evaluator_outputs],
                    value=evaluator_outputs[0] if evaluator_outputs else None,
                    multi=False
                ),
                dcc.Graph(id='comparative-scatter-plot-latency')
            ],
                     className="six columns"),
            html.Div([html.P(id='correlation-coefficient')],
                     className="twelve columns"),
        ],
                        className="row")

    def improver_combo_page_layout():
        if not experiment_data.improver_output:
            return html.Div([html.H3("No Improver Output data available.")])
        return html.Div([
            html.H3(
                "Improver Detailed Test Results",
                style={'textAlign': 'center'}
            ),
            group_key_combination_layout(
                experiment_data.improver_output.group_experiment_results,
                highlight_key=experiment_data.improver_output.
                original_best_combo_key
            ),
            dcc.Link(
                'Go to Improver Experiment Results Analysis',
                href='/improver-experiment-results'
            ),
            html.Hr(),
            html.Div(
                id='current-page-context',
                style={'display': 'none'},
                children='improver'
            )
        ])

    def combo_aggregated_metrics_layout(df):

        columns = [{"name": i, "id": i} for i in df.columns]
        sample_columns = [col for col in df.columns if "Sample" in col]
        sample_style = [{
            'if': {
                'column_id': col
            },
            'width': '15%'
        } for col in sample_columns]

        styles = highlight_best_values(df, *df.columns)
        styles += generate_heatmap_style(df, *df.columns)
        styles += sample_style

        # Highlight the best_combination row
        best_combination = experiment_data.selection_output.best_combination if experiment_data.selection_output else None
        tooltip_data = []
        if best_combination:
            best_combination_str = "\n".join(
                textwrap.wrap(
                    str(best_combination).replace('"', "").replace("'", ""), 90
                )
            )
            styles.append({
                'if': {
                    'column_id': 'Combo Key',
                    'filter_query':
                    f'{{Combo Key}} eq "{best_combination_str}"',
                },
                'backgroundColor': '#DFF0D8',  # Light green color
                'border': '2px solid #28A745',  # Darker green border
                'color': '#155724'  # Dark text color for contrast
            })

            # If selection_reason is available, add it as a tooltip:
            if experiment_data.selection_output and experiment_data.selection_output.selection_reason:
                reason_str = ', '.join([
                    f"{k}: {v}" for k, v in
                    experiment_data.selection_output.selection_reason.items()
                ])
                tooltip_data = [{
                    'Combo Key': {
                        'value': reason_str,
                        'type': 'markdown'
                    }
                } if row["Combo Key"] == best_combination_str else {}
                                for row in df.to_dict('records')]

        evaluator_names = [
            col.replace(" Output", "") for col in df.columns if "Output" in col
        ]

        columns = [{"name": i, "id": i} for i in df.columns]
        return dash_table.DataTable(
            id='combo-metrics-table',
            columns=columns,
            data=df.to_dict('records'),
            style_data_conditional=styles,
            style_cell={
                'whiteSpace': 'normal',
                'height': '60px',
                'textAlign': 'left',
                'fontSize': 16
            },
            style_table={
                'width': '100%',
                'maxHeight': '100vh',
                'overflowY': 'auto'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data={
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'backgroundColor': 'rgb(248, 248, 248)'
            },
            style_cell_conditional=[{
                'if': {
                    'column_id': 'Combo Key'
                },
                'width': '40%'
            }, {
                'if': {
                    'column_id': 'Average Token Usage'
                },
                'width': '20%'
            }, {
                'if': {
                    'column_id': 'Average Latency'
                },
                'width': '20%'
            }, {
                'if': {
                    'column_id': 'Evaluator Outputs'
                },
                'width': '15%'
            }, *[{
                'if': {
                    'column_id': col + " Output"
                },
                'width': '15%'
            } for col in evaluator_names]] + sample_style,
            filter_action="native",
            sort_action="native",
            page_size=10,
            tooltip_data=tooltip_data,
            tooltip_duration=None
        )

    def group_key_combination_layout(
        group_experiment_results: List[GroupedExperimentResult],
        highlight_key: Optional[str] = None
    ):
        df_group_key = generate_group_key_combination_data(
            group_experiment_results
        )
        for col in df_group_key.columns:
            if col != "Test Data":
                df_group_key[col] = df_group_key[col].apply(
                    lambda cell: "\n".join([
                        "▶ " + line if ":" in line else line
                        for line in cell.split("\n")
                    ])
                )

        csv_string = df_group_key.to_csv(index=False, encoding='utf-8')
        csv_data_url = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(
            csv_string
        )

        columns = [{"name": i, "id": i} for i in df_group_key.columns]

        styles_data_conditional = [
            {
                'if': {
                    'filter_query': '{' + col + '} contains "▶"',
                },
                'backgroundColor':
                '#E6F7FF',  # Light blue color for distinction
                'paddingLeft':
                15  # Padding to make angle brackets more visible
            } for col in df_group_key.columns if col != "Test Data"
        ]
        if highlight_key:
            styles_data_conditional.append({
                'if': {
                    'column_id': 'Combo Key',
                    'filter_query': f'{{Combo Key}} eq "{highlight_key}"'
                },
                'backgroundColor': '#FFCCCC'  # Highlighting with gold color
            })
        styles_data_conditional.append({
            'if': {
                'column_id': 'Test Data'
            },
            'color': '#007BFF',  # Blue color
            'textDecoration': 'underline',
            'cursor': 'pointer'
        })
        if "Test Data" in df_group_key:
            df_group_key["Hashed Group Key"] = df_group_key["Test Data"].apply(
                lambda group_key: hashlib.sha256(group_key.encode()).hexdigest(
                )
            )

        return html.Div([
            html.A(
                'Export to CSV',
                id='export-link-group-key-combo',
                download="group_key_combo.csv",
                href=csv_data_url,
                target="_blank"
            ),
            html.Br(),
            dash_table.DataTable(
                id='group-key-combo-table',
                columns=columns,
                data=df_group_key.to_dict('records'),
                style_cell={
                    'whiteSpace':
                    'pre-line',  # Allows for line breaks within cells
                    'height': 'auto',
                    'textAlign': 'left',
                    'fontSize': 16,
                    'border': '1px solid #eee'
                },
                style_table={
                    'width': '100%',
                    'maxHeight': '100vh',
                    'overflowY': 'auto',
                    'border': '1px solid #ddd'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_data={
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'backgroundColor': 'rgb(248, 248, 248)'
                },
                style_data_conditional=styles_data_conditional,
                filter_action="native",
                sort_action="native",
                page_size=10,
                tooltip_duration=None
            ),
            html.Hr(),
            dcc.Link(
                'Go back to Experiment Results Analysis',
                href='/experiment-results'
            ),
            html.Br(),
            dcc.Link('Go to Data Analysis', href='/data-analysis'),
            html.Br()
        ])

    import numpy as np

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

    def input_page_layout():
        # Function to truncate long text
        def truncate_text(text, max_length=60):  # Adjust max_length as needed
            """Truncate text to a specified length and append ellipses."""
            return text if len(text
                               ) <= max_length else text[:max_length] + "..."

        initial_combinations = {
            str(result.combination): result.combination
            for group in experiment_data.group_experiment_results
            for result in group.experiment_results
        }

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
                                                id=f"input-{key}",
                                                type=value,
                                                placeholder=key
                                            ),
                                            width=8
                                        )
                                    ],
                                             className=
                                             "d-flex align-items-center mb-4")
                                    for key, value in function_args.items()
                                ],
                                             className="p-4"),
                                dbc.Button(
                                    "Run",
                                    id="interactive-btn",
                                    color="primary",
                                    className="mt-2 mb-4 w-100"
                                ),
                                # Enhanced Section for Combinations Selection
                                html.Hr(),
                                html.Div([
                                    html.H5(
                                        "Select Combinations",
                                        className="text-center mt-2"
                                    ),
                                    html.P(
                                        "Choose from the available combinations to run. Multiple selections allowed.",
                                        className="text-muted small text-center"
                                    ),
                                    dcc.Dropdown(
                                        id="combinations-select",
                                        options=[{
                                            "label":
                                            truncate_text(str(combo)),
                                            "value":
                                            str(combo)
                                        } for combo in initial_combinations.
                                                 values()],
                                        multi=True,
                                        value=[
                                            str(combo) for combo in
                                            initial_combinations.values()
                                        ],
                                        style={
                                            "border": "1px solid #ced4da",
                                            "border-radius": "4px",
                                            "padding": "5px",
                                            "margin-bottom": "20px"
                                        }
                                    )
                                ],
                                         style={"padding": "10px"}),
                                # Toggle for improver combinations
                                dbc.Checklist(
                                    options=[{
                                        "label": "Use Improver Combinations",
                                        "value": "improver"
                                    }],
                                    value=[],
                                    id="improver-toggle",
                                    switch=True,
                                    inline=True,
                                    style={"padding": "10px"}
                                )
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
                            Div(id="results-section", className="p-4")
                        )
                    ],
                             className="m-4 shadow-sm rounded")
                ],
                        width=9)
            ]),
            dbc.Container(fluid=True, className="p-3")
        ])

    def display_group_experiment_result_layout(
        hashed_group_key, experiment_config, is_from_improver=False
    ):
        group_result = get_group_experiment_result_from_hash(hashed_group_key)
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
            dcc.Store(id='is-from-improver', data=is_from_improver)
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
            children.append(
                html.Div(
                    str(exp_result.raw_output),
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
            is_from_improver = "?source=improver" in hashed_group_key
            hashed_group_key = hashed_group_key.replace('?source=improver', '')
            return display_group_experiment_result_layout(
                hashed_group_key, experiment_config, is_from_improver
            )
        elif pathname == '/data-analysis':
            return data_analysis_layout()
        elif pathname == '/experiment-results':
            return experiment_results_layout()
        elif pathname == '/group-key-combo':
            return combo_page_layout()
        elif pathname == '/improver-experiment-results':
            return improver_experiment_results_layout()
        elif pathname == '/improver-group-key-combo':
            return improver_combo_page_layout()
        elif pathname == '/interactive':
            return input_page_layout()
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
            x='Average Token Usage',
            y=selected_evaluator,
            title=
            f'Comparative Scatter plot of Average Token Usage vs {selected_evaluator}',
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
        if 'Average Token Usage' in df:
            correlation = df['Average Token Usage'].corr(
                df[selected_evaluator]
            )
            return f"Correlation between Average Token Usage and {selected_evaluator}: {correlation:.2f}"

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
        import json

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
            State('is-from-improver', 'data')
        ]
    )  # We'll handle the dynamic State components inside the function itself
    def update_output(
        n_clicks, hashed_group_key, slider_values_store, is_from_improver
    ):
        if not n_clicks:
            return dash.no_update

        # 2. Determine the Current Group
        group_result = get_group_experiment_result_from_hash(hashed_group_key)
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

        if is_from_improver:
            results = []
            for e in experiment_data.improver_output.group_experiment_results:
                for r in e.experiment_results:
                    results.append(r)
            r = generate_experiment(
                results=results,
                evaluator=None,
                evaluate_all=False,
                evaluate_group=False
            )
            experiment_data.improver_output.combination_aggregated_metrics = r.combination_aggregated_metrics
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
                if page_context == 'improver':
                    return f'/rating-result/{hashed_group_key}?source=improver'
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

    @app.callback(
        Output("results-section", "children"),
        Input("interactive-btn", "n_clicks"),
        [State(f"input-{key}", "value") for key in function_args.keys()] + [
            State("combinations-select", "value"),
            State("improver-toggle", "value")
        ],
        prevent_initial_call=True
    )
    def update_results(n_clicks, *input_values_and_combinations_and_toggle):
        if not n_clicks:
            return []
        *input_values, selected_combinations_str, use_improver = input_values_and_combinations_and_toggle
        use_improver = "improver" in use_improver if use_improver else False
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
        input_data = InputData(
            content=content, expected_result=expected_result
        )
        results: List[ExperimentResult] = []
        with ThreadPoolExecutor() as executor:
            for res in executor.map(
                parallel_task, [input_data], [selected_combinations], [state],
                [logger], [evaluator]
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
                    html.Li(f"Raw Output: {result.raw_output}"),
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

    def truncate_text(text, max_length=60):  # Adjust max_length as needed
        """Truncate text to a specified length and append ellipses."""
        return text if len(text) <= max_length else text[:max_length] + "..."

    @app.callback(
        Output("combinations-select", "options"),
        [Input("improver-toggle", "value")]
    )
    def update_combinations_options(use_improver):
        unique_combination = {}

        if "improver" in use_improver:
            # Use improver combinations
            for group in experiment_data.improver_output.group_experiment_results:
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


def display_results_dash(
    experiment_data: Experiment,
    experiment_config,
    all_combinations,
    state,
    logger,
    evaluator,
    interactive=False
):
    if experiment_data.improver_output:
        for group_result in experiment_data.improver_output.group_experiment_results:
            experiment_results = []
            seen = set()
            for r in group_result.experiment_results:
                if str(r.combination) in seen:
                    continue
                else:
                    seen.add(str(r.combination))
                    experiment_results.append(r)
            group_result.experiment_results = experiment_results
    function_args = get_function_args(experiment_config["custom_function"])
    function_args["yival_expected_result (Optional)"] = 'str'
    app = create_dash_app(
        experiment_data, experiment_config, function_args, all_combinations,
        state, logger, evaluator, interactive
    )
    app.run(debug=True, port=8073)
