# type: ignore
import shutil

from dash import dcc, html  # type: ignore
from pydub import AudioSegment

# fixed the ImportError: attempted relative import with no known parent package
# from relative import to absolute import

ffmpeg_executable = shutil.which("ffmpeg")

AudioSegment.converter = ffmpeg_executable


def data_analysis_layout(df):
    return html.Div([
        html.H3("Data Analysis", style={'textAlign': 'center'}),
        analysis_layout(df),
        html.Hr(),
        dcc.Link(
            'Go back to Experiment Results Analysis',
            href='/experiment-results'
        ),
        html.Br(),
        dcc.Link(
            'Go to Detailed Experiment Results', href='/group-key-combo'
        ),
        html.Br(),
        dcc.Link(
            'Go to Enhancer Experiment Results Analysis',
            href='/enhancer-experiment-results'
        ),
        html.Br(),
        dcc.Link(
            'Go to Enhancer Detailed Experiment Results',
            href='/enhancer-group-key-combo'
        ),
        html.Br()
    ])
        
def analysis_layout(df): 
    evaluator_outputs = [
        col for col in df.columns
        if (col != 'Prompt Variations' and 'Sample' not in col)
    ]
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