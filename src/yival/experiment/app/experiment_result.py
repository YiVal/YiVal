# type: ignore
import shutil
import textwrap
import urllib.parse

from dash import dash_table, dcc, html  # type: ignore
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
from pydub import AudioSegment

from yival.experiment.app.media_formatter import pil_audio_to_base64, pil_image_to_base64
from yival.experiment.app.utils import (
    generate_heatmap_style,
    generate_legend,
    highlight_best_values,
)
# fixed the ImportError: attempted relative import with no known parent package
# fixed the ImportError: attempted relative import with no known parent package
# from relative import to absolute import
from yival.schemas.experiment_config import MultimodalOutput

ffmpeg_executable = shutil.which("ffmpeg")

AudioSegment.converter = ffmpeg_executable


def experiment_results_layout(df, experiment_data):
    print("experiment_results_layout")
    print("df")
    print(df)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_data_url = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(
        csv_string
    )
    sample_columns = [col for col in df.columns if "Sample" in col]
    contains_images = any(
        df[col].apply(
            lambda x: isinstance(x, MultimodalOutput) and x.image_output is
            not None
        ).any() for col in sample_columns
    )
    contains_videos = any(
        df[col].apply(
            lambda x: isinstance(x, MultimodalOutput) and x.video_output is
            not None
        ).any() for col in sample_columns
    )
    contains_audios = any(
        df[col].apply(
            lambda x: isinstance(x, MultimodalOutput) and x.audio_output is
            not None
        ).any() for col in sample_columns
    )
    multi_div = None
    print(contains_images)
    print(contains_audios)
    if contains_images:
        multi_div = image_combo_aggregated_metrics_layout(df)
    elif contains_videos:
        multi_div = video_combo_aggregated_metrics_layout(df)
    elif contains_audios:
        multi_div = audio_combo_aggregated_metrics_layout(df)
    else:
        multi_div = combo_aggregated_metrics_layout(df, experiment_data)

    return html.Div([
        html.H3(
            "Experiment Results Analysis", style={'textAlign': 'center'}
        ),
        html.Hr(),
        html.Div([multi_div],
                    style={
                        'overflowY': 'auto',
                        'overflowX': 'auto'
                    }),
        html.Hr(),
        generate_legend(),
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


def combo_aggregated_metrics_layout(df, experiment_data):

    columns = [{"name": i, "id": i} for i in df.columns]
    sample_columns = [col for col in df.columns if "Sample" in col]
    for col in sample_columns:
        df[col] = df[col].apply(
            lambda x: x.text_output
            if isinstance(x, MultimodalOutput) else x
        )
    sample_style = [{
        'if': {
            'column_id': col
        },
        'width': '15%'
    } for col in sample_columns]

    # styles = highlight_best_values(df, *df.columns)
    styles = generate_heatmap_style(df, *df.columns)
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
                'column_id':
                'Prompt Variations',
                'filter_query':
                f'{{Prompt Variations}} eq "{best_combination_str}"',
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
                'Prompt Variations': {
                    'value': reason_str,
                    'type': 'markdown'
                }
            } if row["Prompt Variations"] == best_combination_str else {}
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
                'column_id': 'Prompt Variations'
            },
            'width': '40%'
        }, {
            'if': {
                'column_id': 'Average Token Usage(Cost Proportional)'
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
        
        
def image_combo_aggregated_metrics_layout(df):
    sample_columns = [col for col in df.columns if "Sample" in col]

    # Process each column with MultimodalOutput
    for col in sample_columns:
        df[col] = df[col].apply(
            lambda x: html.Div([
                html.P(f'<text_output> {x.text_output} </text_output>'),
                html.Div(
                    html.Img(
                        src=pil_image_to_base64(x.image_output[0]),
                        style={
                            'maxHeight': '100%',
                            'maxWidth': '100%',
                            'objectFit': 'contain'
                        }
                    ),
                    style={
                        'height': '200px',
                        'width': '200px',
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center',
                        'overflow': 'hidden'
                    }
                )
            ]) if isinstance(x, MultimodalOutput) and x.image_output is
            not None else x
        )
    
    for index, row in df.iterrows():
        for col_index, col in enumerate(df.columns):
            if col_index == 1:
                print("row[col][:250]")
                print(row[col])

    # Create html.Table
    table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        [
            html.Tr([
                DangerouslySetInnerHTML(
                    f'<details><summary>{row[col][:250]}...</summary>{row[col]}</details>'
                ) if col_index == 1 else html.Td(row[col])
                for col_index, col in enumerate(df.columns)
            ]) for index, row in df.iterrows()
        ]
    )

    return table

def video_combo_aggregated_metrics_layout(df):
    sample_columns = [col for col in df.columns if "Sample" in col]

    # Process each column with MultimodalOutput
    for col in sample_columns:
        df[col] = df[col].apply(
            lambda x: html.Div([
                html.P(f'<text_output> {x.text_output} </text_output>'),
                html.Div(
                    children=[
                        html.Video(
                            controls=True,
                            id='movie_player',
                            src=x.video_output[0],
                            autoPlay=False
                        )
                    ],
                    style={
                        'height': '200px',
                        'width': '200px',
                        'display': 'flex',
                        # 'justifyContent': 'center',
                        # 'alignItems': 'center',
                        # 'overflow': 'hidden'
                    }
                )
            ]) if isinstance(x, MultimodalOutput) and x.video_output is
            not None else x
        )
        # Create html.Table
    table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        [
            html.Tr([
                DangerouslySetInnerHTML(
                    f'<details><summary>{row[col][:250]}...</summary>{row[col]}</details>'
                ) if col_index == 1 else html.Td(row[col])
                for col_index, col in enumerate(df.columns)
            ]) for index, row in df.iterrows()
        ]
    )

    return table

def audio_combo_aggregated_metrics_layout(df):
    sample_columns = [col for col in df.columns if "Sample" in col]

    # Process each column with MultimodalOutput
    for col in sample_columns:
        df[col] = df[col].apply(
            lambda x: html.Div([
                html.Div(
                    DangerouslySetInnerHTML(
                        f'<details><summary>{x.text_output[:250]}...</summary><text_output> {x.text_output} </text_output></details>'
                    )
                ),
                html.Div(
                    html.Audio(
                        controls=True,
                        src=pil_audio_to_base64(x.audio_output[0]),
                        style={
                            'maxHeight': '100%',
                            'maxWidth': '100%',
                            'objectFit': 'contain'
                        }
                    ),
                    style={
                        'height': '200px',
                        'width': '200px',
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center',
                        'overflow': 'hidden'
                    }
                )
            ]) if isinstance(x, MultimodalOutput) and x.audio_output is
            not None else x
        )
        
    # Create html.Table
    table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        [
            html.Tr([
                DangerouslySetInnerHTML(
                    f'<details><summary>{row[col][:250]}...</summary>{row[col]}</details>'
                ) if col_index == 1 else html.Td(row[col])
                for col_index, col in enumerate(df.columns)
            ]) for index, row in df.iterrows()
        ]
    )


    return table