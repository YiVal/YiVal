import hashlib
import textwrap
import urllib.parse
from typing import List, Optional

import dash  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
from dash import dash_table, dcc, html  # type: ignore
from dash.dependencies import Input, Output  # type: ignore

from ..schemas.experiment_config import (
    CombinationAggregatedMetrics,
    Experiment,
    ExperimentConfig,
    GroupedExperimentResult,
)


def create_dash_app(experiment_data: Experiment, experiment_config: ExperimentConfig):
    
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
    
    def get_group_experiment_result_from_hash(hashed_group_key):
        for group_result in experiment_data.group_experiment_results:
            group_key = sanitize_group_key(group_result.group_key)
            if hashlib.sha256(group_key.encode()).hexdigest() == hashed_group_key:
                return group_result
        return None


    def sanitize_column_name(name):
        return name.replace('"', '').replace(':', '')

    def index_page():
        return html.Div([
            html.Nav([
                html.Div([
                    html.A("Dashboard", href="/", className="navbar-brand"),
                    html.Ul([
                        html.Li(html.A("Experiment Results Analysis", href="/experiment-results", className="nav-link"), className="nav-item"),
                        html.Li(html.A("Data Analysis", href="/data-analysis", className="nav-link"), className="nav-item"),
                        html.Li(html.A("Group Key Combination", href="/group-key-combo", className="nav-link"), className="nav-item"),
                        html.Li(html.A("Improver Experiment Results Analysis", href="/improver-experiment-results", className="nav-link"), className="nav-item"),
                        html.Li(html.A("Improver Group Key Combination", href="/improver-group-key-combo", className="nav-link"), className="nav-item")
                    ], className="navbar-nav")
                ], className="container-fluid")
            ], className="navbar navbar-expand-lg navbar-light bg-light"),
            html.Div([
                html.Div("Welcome to the Dashboard!", className="card-title"),
                html.P("Choose one of the options from the navigation bar to proceed.", className="card-text")
            ], className="card-body")
        ], className="container mt-5")

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
            dcc.Link('Go to Group Key Combination', href='/group-key-combo'),
            html.Br(),
            dcc.Link(
                'Go to Improver Experiment Results Analysis',
                href='/improver-experiment-results'
            ),
            html.Br(),
            dcc.Link(
                'Go to Improver Group Key Combination',
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
            dcc.Link('Go to Group Key Combination', href='/group-key-combo'),
            html.Br(),
            dcc.Link(
                'Go to Improver Experiment Results Analysis',
                href='/improver-experiment-results'
            ),
            html.Br(),
            dcc.Link(
                'Go to Improver Group Key Combination',
                href='/improver-group-key-combo'
            ),
            html.Br()
        ])

    def combo_page_layout():
        return html.Div([
            html.H3("Combo Page Title", style={'textAlign': 'center'}),
            group_key_combination_layout(
                experiment_data.group_experiment_results
            ),
            dcc.Link(
                'Go to Improver Experiment Results Analysis',
                href='/improver-experiment-results'
            ),
            html.Br(),
            dcc.Link(
                'Go to Improver Group Key Combination',
                href='/improver-group-key-combo'
            ),
            html.Br(),
            html.Hr()
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
            # Extract sample results

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
                        ] = matching_results[
                            0]  # Take the first matching sample result
                    sample_count += 1

            data.append(row)
        df = pd.DataFrame(data)
        # Convert 'Average Token Usage' and 'Average Latency' columns to numeric
        df['Average Token Usage'] = pd.to_numeric(
            df['Average Token Usage'], errors='coerce'
        )
        df['Average Latency'] = pd.to_numeric(
            df['Average Latency'], errors='coerce'
        )
        return df

    app = dash.Dash(
        __name__,
        external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
    )
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
            hashed_group_key = pathname.split('/')[-1]  # Extract the last part of the URL which is the hash
            return display_group_experiment_result_layout(hashed_group_key, experiment_config)
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
        else:
            return index_page()

    def analysis_layout(df):
        evaluator_outputs = [col for col in df.columns if "Output" in col]

        return html.Div(
            [
                # Comparative Scatter Plots for Token Usage
                html.Div([
                    dcc.Dropdown(
                        id='evaluator-dropdown-token',
                        options=[{
                            'label': evaluator,
                            'value': evaluator
                        } for evaluator in evaluator_outputs],
                        value=evaluator_outputs[0]
                        if evaluator_outputs else None,
                        multi=False
                    ),
                    dcc.Graph(id='comparative-scatter-plot-token')
                ],
                         className="six columns"),

                # Comparative Scatter Plots for Latency
                html.Div([
                    dcc.Dropdown(
                        id='evaluator-dropdown-latency',
                        options=[{
                            'label': evaluator,
                            'value': evaluator
                        } for evaluator in evaluator_outputs],
                        value=evaluator_outputs[0]
                        if evaluator_outputs else None,
                        multi=False
                    ),
                    dcc.Graph(id='comparative-scatter-plot-latency')
                ],
                         className="six columns"),

                # Display Correlation Coefficient
                html.Div([html.P(id='correlation-coefficient')],
                         className="twelve columns"),
            ],
            className="row"
        )

    @app.callback(
        Output('comparative-scatter-plot-token', 'figure'),
        [Input('evaluator-dropdown-token', 'value')]
    )
    def update_comparative_scatter_token(selected_evaluator):
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
        return px.scatter(
            df,
            x='Average Latency',
            y=selected_evaluator,
            title=
            f'Comparative Scatter plot of Average Latency vs {selected_evaluator}',
            size_max=15
        )

    @app.callback(
        Output('correlation-coefficient', 'children'),
        [Input('evaluator-dropdown-token', 'value')]
    )
    def display_correlation_coefficient(selected_evaluator):
        correlation = df['Average Token Usage'].corr(df[selected_evaluator])
        return f"Correlation between Average Token Usage and {selected_evaluator}: {correlation:.2f}"

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
            dcc.Link('Go to Group Key Combination', href='/group-key-combo'),
            html.Br(),
            dcc.Link(
                'Go to Improver Group Key Combination',
                href='/improver-group-key-combo'
            ),
            html.Br()
        ])

    def improver_combo_page_layout():
        if not experiment_data.improver_output:
            return html.Div([html.H3("No Improver Output data available.")])
        return html.Div([
            html.H3(
                "Improver Combo Page Title", style={'textAlign': 'center'}
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
                    str(exp_result.combination).replace("{",
                                                        "").replace("}", "")
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

    def group_key_combination_layout(
        group_experiment_results: List[GroupedExperimentResult],
        highlight_key: Optional[str] = None
    ):
        df_group_key = generate_group_key_combination_data(
            group_experiment_results
        )
        # Process each cell to selectively enclose evaluator outputs
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

        # Conditional styling for cells containing evaluator outputs
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
                'if': {'column_id': 'Test Data'},
                'color': '#007BFF',  # Blue color
                'textDecoration': 'underline',
                'cursor': 'pointer'
            }
        )
        df_group_key["Hashed Group Key"] = df_group_key["Test Data"].apply(
            lambda group_key: hashlib.sha256(group_key.encode()).hexdigest()
        )

        return html.Div([
            html.H3(
                "Group Key Combination Analysis",
                style={'textAlign': 'center'}
            ),
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
            html.Br(),  # Adding a line break
            dcc.Link('Go to Data Analysis', href='/data-analysis'),
            html.Br()  # Adding a line break
        ])
        
    def display_group_experiment_result_layout(hashed_group_key, experiment_config):
        group_result = get_group_experiment_result_from_hash(hashed_group_key)
        if not group_result:
            return html.Div("No data found for this group key.", style={'font-size': '24px', 'color': 'red', 'margin': '40px', 'text-align': 'center'})

        children = [html.H2("Rate experiment results", style={'text-align': 'center', 'margin-bottom': '70px', 'font-weight': 'bold', 'color': '#2E86C1', 'border-bottom': '4px solid #3498DB', 'padding-bottom': '30px', 'font-size': '28px'})]
        
        for exp_result in group_result.experiment_results:
            # Displaying only the raw output
            children.append(html.Div("Raw Output:", style={'font-weight': 'bold', 'font-size': '26px', 'margin-top': '50px', 'color': '#2C3E50'}))
            children.append(html.Div(str(exp_result.raw_output), style={'margin': '25px 0', 'border': '2px solid #AED6F1', 'padding': '25px', 'background-color': '#EAF2F8', 'border-radius': '10px', 'box-shadow': '0 4px 12px rgba(0, 0, 0, 0.1)', 'font-size': '22px'}))
            
            for rating_config in (experiment_config["human_rating_configs"] or []):
                # Displaying rating instructions if present in rating_config
                if "instructions" in rating_config:
                    children.append(html.Div("Instructions:", style={'font-weight': 'bold', 'font-size': '24px', 'margin-top': '40px', 'color': '#5D6D7E'}))
                    children.append(html.Div(rating_config["instructions"], style={'margin': '20px 0', 'background-color': '#D5F5E3', 'padding': '20px', 'border-radius': '10px', 'font-size': '22px'}))
                    
                # Slider to represent the rating scale
                children.append(html.Div(rating_config["name"], style={'font-size': '24px', 'margin-top': '40px', 'color': '#5D6D7E'}))
                scale_bar = dcc.Slider(
                    min=rating_config["scale"][0],
                    max=rating_config["scale"][1],
                    marks={i: str(i) for i in range(int(rating_config["scale"][0]), int(rating_config["scale"][1]) + 1)},
                    value=(rating_config["scale"][0] + rating_config["scale"][1]) / 2,
                    disabled=False
                )
                children.append(scale_bar)

        return html.Div(children, style={'padding': '80px', 'background-color': '#FCF3CF', 'border-radius': '20px', 'box-shadow': '0 8px 25px rgba(0, 0, 0, 0.1)', 'font-family': 'Arial, sans-serif', 'width': '90%', 'margin': '2% auto'})


    @app.callback(
        dash.dependencies.Output('url', 'pathname'),
        [dash.dependencies.Input('group-key-combo-table', 'active_cell'),
        dash.dependencies.Input('group-key-combo-table', 'data')]
    )
    def navigate_to_hashed_page(active_cell, table_data):
        if active_cell:
            row = active_cell["row"]
            col_id = active_cell["column_id"]
            if col_id == "Test Data":
                hashed_group_key = table_data[row]["Hashed Group Key"]
                return f'/rating-result/{hashed_group_key}'
        return dash.no_update

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

    def highlight_best_values(df, *cols):
        styles = []
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                best_val = df[col].min()
                styles.append({
                    'if': {
                        'filter_query': f'{{{col}}} eq {best_val}',
                        'column_id': col
                    },
                    'border': '2px solid red'
                })
            else:  # For aggregated metrics columns and evaluator outputs
                metrics_values = df[col].str.extractall(r":\s?(\d+\.\d+)"
                                                        ).astype(float)
                if not metrics_values.empty:
                    best_val = metrics_values[0].min()
                    styles.append({
                        'if': {
                            'filter_query': f'{{{col}}} contains "{best_val}"',
                            'column_id': col
                        },
                        'border': '2px solid red'
                    })
        return styles

    def generate_navigation():
        return html.Div([
            dcc.Link('Experiment Results Analysis', href='/experiment-results'),
            html.Span(" | ", className="nav-divider"),
            dcc.Link('Data Analysis', href='/data-analysis'),
            html.Span(" | ", className="nav-divider"),
            dcc.Link('Group Key Combination', href='/group-key-combo'),
            html.Span(" | ", className="nav-divider"),
            dcc.Link('Improver Experiment Results Analysis', href='/improver-experiment-results'),
            html.Span(" | ", className="nav-divider"),
            dcc.Link('Improver Group Key Combination', href='/improver-group-key-combo')
        ], className="navigation")


    # Define Dash App Layout
    app.layout = html.Div([
        # Main Content
        html.Div([
            dcc.Location(id='url', refresh=False),
            generate_navigation(), # Adding the navigation here
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
        ], className="main-content", style={
        'backgroundColor': '#f9f9f9', # Light Grey
        'padding': '20px'
    }),
        
    ], className="main-wrapper")

    return app


def display_results_dash(experiment_data, experiment_config):
    app = create_dash_app(experiment_data, experiment_config)
    app.run(debug=True, port=8073)