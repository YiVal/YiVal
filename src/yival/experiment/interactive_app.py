import importlib
import inspect

import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State

from yival.experiment.app import create_dash_app

# Sample Data
DATASET_SOURCE_TYPES = ["DATASET", "MACHINE_GENERATED"]
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


header_styles = {
    "background": "linear-gradient(45deg, #2C3E50, #3498DB)",
    "padding": "20px 0",
    "border-radius": "10px",
    "margin-bottom": "20px"
}

tab_styles = {
    "cursor": "pointer",
    "transition": "all 0.3s",
    "padding": "10px 15px",
    "border-radius": "5px"
}

tab_active_styles = {
    **tab_styles,
    "background": "#2C3E50",
    "color": "#FFFFFF"
}

button_styles = {
    "background": "linear-gradient(45deg, #2C3E50, #3498DB)",
    "border": "none",
    "transition": "all 0.3s",
    "border-radius": "5px"
}

tab_styles = {
    "cursor": "pointer",
    "transition": "all 0.3s",
    "padding": "10px 15px",
    "border-radius": "5px",
    "border-bottom": "3px solid transparent"
}

tab_active_styles = {
    "border-bottom": "3px solid #2C3E50"
}

demo_switch = dbc.Checklist(
    options=[{"label": "Demo Mode", "value": 1}],
    value=[],
    id="demo-switch",
    inline=True,
    switch=True,
    className="mb-4"
)


def get_function_args(func_string: str):
    import sys
    sys.path.append('/Users/taofeng/YiVal')    
    module_name, function_name = func_string.rsplit('.', 1)
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    signature = inspect.signature(function)
    return {
        name: param.annotation
        for name, param in signature.parameters.items()
    }


def data_input_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader("Data Input Configuration"),
            dbc.ModalBody([
                dbc.Label("Enter custom function:", className='mb-2'),
                dbc.Input(type="text", id="custom-function-input", placeholder="/path/to/custom_function.py"),
            ]),
            dbc.ModalFooter([
                dbc.Button("Save", id="save-data-input-button", className="ml-auto"),
                dbc.Button("Close", id="close-data-input-modal", className="ml-auto")
            ]),
        ],
        id="data-input-modal",
        centered=True,
    )


# Modal for Configuration
def config_modal(tab_id):
    return dbc.Modal(
        [
            dbc.ModalHeader([html.I(className="fas fa-cog"), f"{tab_id} Configuration"]),
            dbc.ModalBody(f"Configuration details for {tab_id}."),
            dbc.ModalFooter(
                dbc.Button("Close", id=f"close-{tab_id}-modal", className="ml-auto")
            ),
        ],
        id=f"{tab_id}-modal",
        centered=True,
    )

run_button = dbc.Button([
    html.I(className="fas fa-play"), " Run"
], id="run-button", style=button_styles, className="mt-3")


sidebar = html.Div(
    [
        demo_switch,
        html.Div(
            id="user-input-section",
            children=[
                dbc.Label("User Input:", className='mb-2 text-info display-5, text-primary'),  # Adjusted font size with display-5 class
                dbc.RadioItems(
                    id="user-input-toggle",
                    options=[{'label': 'On', 'value': 'on'}, {'label': 'Off', 'value': 'off'}],
                    value='off',
                    inline=True,
                    className='mb-4'
                ),
                html.Div(id="user-input-content", className='border p-4 rounded'),
                run_button
            ]
        ),
        html.Div(
            id="task-description-section",
            children=[
                dbc.Label("Task Description:", className='mb-2 text-info display-5'),
                dbc.Input(type="text", placeholder="Describe the task...")
            ],
            style={"display": "none"}
        )
    ],
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "20%",  # adjust as per your requirement
        "padding": "20px",
        "background-color": "#f8f9fa",
        "z-index": 1,  # to bring sidebar to the front
        "overflow-y": "auto"
    },
    id="sidebar"
)

@app.callback(
    [Output('var-config', 'style'),
     Output('eval-config', 'style'),
     Output('imp-config', 'style'),
     Output('wrap-config', 'style')],
    Input('config-tabs', 'active_tab')
)
def update_tab_styles(active_tab):
    styles = {
        'var-config': tab_styles,
        'eval-config': tab_styles,
        'imp-config': tab_styles,
        'wrap-config': tab_styles
    }
    styles[active_tab] = {**tab_styles, **tab_active_styles}
    return styles['var-config'], styles['eval-config'], styles['imp-config'], styles['wrap-config']

# Layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(html.H1("YiVal", className='mb-4 text-white display-3', style=header_styles), width=12),
                dbc.Col(
                    dbc.Tabs(
                        [
                            dbc.Tab(label='Data Input', tab_id='data-input', style=tab_styles),
                            dbc.Tab(label='Variation', tab_id='var-config', style=tab_styles),
                            dbc.Tab(label='Evaluator', tab_id='eval-config', style=tab_styles),
                            dbc.Tab(label='Improver', tab_id='imp-config', style=tab_styles),
                            dbc.Tab(label='Wrappers', tab_id='wrap-config', style=tab_styles),
                        ],
                        id='config-tabs',
                        active_tab='var-config',
                        className='mb-4'
                    ),
                    width=12,
                    className='text-center'
                ),
            ]
        ),
        # Configuration Modals
        config_modal('var-config'),
        config_modal('eval-config'),
        config_modal('imp-config'),
        config_modal('wrap-config'),
        data_input_modal(),

        dbc.Row(
            [
                # Left Side (User Input)
                dbc.Col(
                    [
                        demo_switch,
                        html.Div(
                            id="user-input-section",
                            children=[
                                dbc.Label("User Input:", className='mb-2 text-info display-5,  text-primary'),  # Adjusted font size with display-5 class
                                dbc.RadioItems(
                                    id="user-input-toggle",
                                    options=[{'label': 'On', 'value': 'on'}, {'label': 'Off', 'value': 'off'}],
                                    value='off',
                                    inline=True,
                                    className='mb-4'
                                ),
                                html.Div(id="user-input-content", className='border p-4 rounded'),
                                run_button
                            ]
                        ),
                        html.Div(
                            id="task-description-section",
                            children=[
                                dbc.Label("Task Description:", className='mb-2 text-info'),
                                dbc.Input(type="text", placeholder="Describe the task...")
                            ],
                            style={"display": "none"}
                        )
                    ],
                    width=3,
                    style={"borderRight": "2px solid #dee2e6", "height": "100%"}
                ),

                # Right Side (Results)
                dbc.Col(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H4("Results:", className="card-title text-success"),  # Adjusted font size with display-4 class
                                    html.Div(id="results-table", className="card-text", ),
                                ]
                            ),
                            className='mb-4 shadow-lg'  # Added shadow for a raised card effect
                        )
                    ],
                    width=9,
                    style={"borderLeft": "2px solid #dee2e6", "height": "100%"} 
                )
            ],
            className='mb-5'
        )
    ],
    fluid=True,
)


@app.callback(
    [Output("user-input-section", "style"), Output("task-description-section", "style")],
    [Input("demo-switch", "value")]
)
def toggle_demo_mode(demo_value):
    if demo_value == [1]:  # If demo mode is turned on
        return {"display": "none"}, {"display": "block"}
    else:
        return {"display": "block"}, {"display": "none"}

@app.callback(
    Output('data-input-modal', 'is_open'),
    [Input("config-tabs", "active_tab"), Input('close-data-input-modal', 'n_clicks'), Input('save-data-input-button', 'n_clicks')],
    [State('data-input-modal', 'is_open')]
)
def toggle_data_input_modal(active_tab, close_clicks, save_clicks, is_open):
    if active_tab == 'data-input' or close_clicks or save_clicks:
        return not is_open
    return is_open


@app.callback(
    Output('user-input-content', 'children'),
    [Input('user-input-toggle', 'value'),
     Input('save-data-input-button', 'n_clicks')],
    [State('custom-function-input', 'value')]
)
def combined_callback(toggle_value, save_clicks, function_path):
    ctx = dash.callback_context

    # Check if the callback was triggered by the toggle
    if ctx.triggered[0]['prop_id'] == 'user-input-toggle.value':
        if toggle_value == 'on':
            return [
                dbc.Label("Enter custom function:", className='mb-2'),
                dbc.Input(type="text", placeholder="/path/to/custom_function.py")
            ]
        else:
            return [
                dbc.Label("Select Source Type:", className='mb-2'),
                dbc.Select(id="source-type-dropdown", options=[{'label': s, 'value': s} for s in DATASET_SOURCE_TYPES], value=DATASET_SOURCE_TYPES[0]),
                html.Div(id="dataset-config", className='mt-4'),
                html.Div(id="machine-generated-config", className='mt-4')
            ]

    # Check if the callback was triggered by the save button
    elif ctx.triggered[0]['prop_id'] == 'save-data-input-button.n_clicks' and function_path:
        args = get_function_args(function_path)
        children = []
        for key, value in args.items():
            children.extend([
                dbc.Label(f"{key} ({value}):", className='mb-2'),
                dbc.Input(type="text", placeholder=f"Enter value for {key}"),
                html.Br()
            ])
        return children

    return []  # default return


@app.callback(
    Output('results-table', 'children'),
    [Input('run-button', 'n_clicks')]
)
def display_experiment_dashboard(n_clicks):
    if n_clicks:
        import pickle
        with open("auto_prompt_updated_pickle_latest.pkl", "rb") as file:
            experiment=pickle.load(file)
        _, layouts = create_dash_app(experiment)
        layout_to_return = layouts['/experiment-results']
        print(layout_to_return)
        # When the run button is clicked, display the experiment dashboard in the results section
        return layout_to_return
    return []  # Return an empty list if no clicks (i.e., at the start)
    
@app.callback(
    [Output(f"{tab_id}-modal", "is_open") for tab_id in ['var-config', 'eval-config', 'imp-config', 'wrap-config']],
    [Input("config-tabs", "active_tab")] + [Input(f"close-{tab_id}-modal", "n_clicks") for tab_id in ['var-config', 'eval-config', 'imp-config', 'wrap-config']],
    [State(f"{tab_id}-modal", "is_open") for tab_id in ['var-config', 'eval-config', 'imp-config', 'wrap-config']]
)
def toggle_modal(active_tab, *args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, False, False, False
    source = ctx.triggered[0]['prop_id'].split('.')[0]
    return [active_tab == tab_id and 'close' not in source for tab_id in ['var-config', 'eval-config', 'imp-config', 'wrap-config']]

if __name__ == '__main__':
    app.run_server(debug=True)
