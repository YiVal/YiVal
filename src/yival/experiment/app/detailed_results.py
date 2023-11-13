
# type: ignore
import hashlib
import shutil
import urllib.parse
from typing import List, Optional

from dash import dash_table, dcc, html  # type: ignore
from pydub import AudioSegment

from yival.experiment.app.html_structurer import (
    create_table,
    create_video_table,
    format_dataframe_column,
)
from yival.experiment.app.media_formatter import (
    extract_and_decode_audio,
    extract_and_decode_image,
    extract_and_decode_video,
    include_audio_base64,
    include_image_base64,
    include_video,
)
from yival.experiment.app.utils import generate_group_key_combination_data
# fixed the ImportError: attempted relative import with no known parent package
# from relative import to absolute import
from yival.schemas.experiment_config import GroupedExperimentResult

ffmpeg_executable = shutil.which("ffmpeg")

AudioSegment.converter = ffmpeg_executable

test_data_hint = html.Div([
    html.Small(
        "Click on each test data below to perform human labeling.",
        style={
            "color": "#888888",
            "display": "block",
            "marginBottom": "10px"
        }
    )
])

def combo_page_layout(experiment_data):
    return html.Div([
        html.H3(
            "Detailed Experiment Results", style={'textAlign': 'center'}
        ),
        html.Hr(),
        group_key_combination_layout(
            experiment_data.group_experiment_results
        ),
        dcc.Link(
            'Go to Enhancer Experiment Results Analysis',
            href='/enhancer-experiment-results'
        ),
        html.Br(),
        dcc.Link(
            'Go to Enhancer Detailed Experiment Results',
            href='/enhancer-group-key-combo'
        ),
        html.Br(),
        html.Hr(),
        html.Div(
            id='current-page-context',
            style={'display': 'none'},
            children='default'
        )
    ])
    
def group_key_combination_layout(
        group_experiment_results: List[GroupedExperimentResult],
        highlight_key: Optional[str] = None
    ):
    df_group_key = generate_group_key_combination_data(
        group_experiment_results
    )
    print("df_group_key")
    print(df_group_key)
    for col in df_group_key.columns:
        if col != "Test Data":
            df_group_key[col] = df_group_key[col].apply(
                format_dataframe_column
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
                'column_id': 'Prompt Variations',
                'filter_query':
                f'{{Prompt Variations}} eq "{highlight_key}"'
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
    print("df_group_key")
    print(df_group_key)
    data_dict = df_group_key.to_dict('records'),
    print("data_dict")
    print(data_dict)
    if include_image_base64(data_dict):
        new_data_dict = extract_and_decode_image(data_dict)
        return html.Div([
            html.A(
                'Export to CSV',
                id='export-link-group-key-combo',
                download="group_key_combo.csv",
                href=csv_data_url,
                target="_blank"
            ),
            html.Br(), test_data_hint,
            html.Table(
                create_table(new_data_dict), id='group-key-combo-table'
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
    if include_video(data_dict):
        new_data_dict = extract_and_decode_video(data_dict)
        return html.Div([
            html.A(
                'Export to CSV',
                id='export-link-group-key-combo',
                download="group_key_combo.csv",
                href=csv_data_url,
                target="_blank"
            ),
            html.Br(), test_data_hint,
            html.Table(
                create_video_table(new_data_dict),
                id='group-key-combo-table'
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
    if include_audio_base64(data_dict):
        new_data_dict = extract_and_decode_audio(data_dict)
        return html.Div([
            html.A(
                'Export to CSV',
                id='export-link-group-key-combo',
                download="group_key_combo.csv",
                href=csv_data_url,
                target="_blank"
            ),
            html.Br(),
            html.Table(
                create_table(new_data_dict), id='group-key-combo-table'
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
    else:
            return html.Div([
                html.A(
                    'Export to CSV',
                    id='export-link-group-key-combo',
                    download="group_key_combo.csv",
                    href=csv_data_url,
                    target="_blank"
                ),
                html.Br(),
                test_data_hint,
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