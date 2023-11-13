# type: ignore
import shutil

import dash_bootstrap_components as dbc  # type: ignore
from dash import dcc, html  # type: ignore
from pydub import AudioSegment

# fixed the ImportError: attempted relative import with no known parent package
# from relative import to absolute import

ffmpeg_executable = shutil.which("ffmpeg")

AudioSegment.converter = ffmpeg_executable

def input_page_layout(experiment_data, function_args):
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
                                html.H4("Input", className="text-center"),
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
                            # Toggle for enhancer combinations
                            dbc.Checklist(
                                options=[{
                                    "label": "Use Enhancer Combinations",
                                    "value": "enhancer"
                                }],
                                value=[],
                                id="enhancer-toggle",
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
