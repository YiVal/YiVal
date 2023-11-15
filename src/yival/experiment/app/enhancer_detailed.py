from dash import dcc, html  # type: ignore

from yival.experiment.app.detailed_results import group_key_combination_layout

def enhancer_combo_page_layout(experiment_data):
    if not experiment_data.enhancer_output:
        return html.Div([html.H3("No Enhancer Output data available.")])
    return html.Div([
        html.H3(
            "Enhancer Detailed Experiment Results",
            style={'textAlign': 'center'}
        ),
        group_key_combination_layout(
            experiment_data.enhancer_output.group_experiment_results,
            highlight_key=experiment_data.enhancer_output.
            original_best_combo_key
        ),
        dcc.Link(
            'Go to Enhancer Experiment Results Analysis',
            href='/enhancer-experiment-results'
        ),
        html.Hr(),
        html.Div(
            id='current-page-context',
            style={'display': 'none'},
            children='enhancer'
        )
    ])