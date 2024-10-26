import dash_html_components as html
import dash_bootstrap_components as dbc
from assets.functions_and_datasets import (archived_predictions, predictions_summary_table,
                                           predictions_dataset, recommended_preds, recommended_preds_archive)
import dash_table
from assets.header import dash_header
from assets.footer import dash_footer

archived_predictions = archived_predictions.loc[lambda x: x.League != "NBA"].reset_index(drop=True)
predictions_summary_table = predictions_summary_table.loc[lambda x: x.League != "NBA"].reset_index(drop=True)
predictions_dataset = predictions_dataset.loc[lambda x: x.League != "NBA"].reset_index(drop=True)
recommended_preds_archive = recommended_preds_archive.loc[lambda x: x.League != "NBA"].reset_index(drop=True)


preds_page = html.Div([

    dash_header,

    dbc.Row([dbc.Col(), dbc.Col(), dbc.Col(),
             html.H2("Recommended Predictions", style={"fontSize": "30px", "margin-top": "20px", "color": "white",
                                                       "background-color": "#102031", "margin-bottom": "20px"}),
             dbc.Col(), dbc.Col(), dbc.Col()]),

    dbc.Row([
        dbc.Col(html.Div([dash_table.DataTable(
            id='table',
            columns=[
                {"name": i, "id": i, "selectable": True} for i in recommended_preds.columns
            ],
            data=recommended_preds.to_dict('records'),
            editable=True,
            style_cell=dict(textAlign='center', whiteSpace='normal', minWidth='180px', width='180px',
                            maxWidth='180px'),
            style_header=dict(backgroundColor="#CAECD8"),
            style_data=dict(backgroundColor="lavender"),
            style_table={"height": "200px", "width": "450", 'overflowY': 'auto'},
            page_size=5,
            sort_action='native',
            sort_mode='single',
            sort_by=[{'column_id': 'pop', 'direction': 'asc'}])])),

    ]),

    html.Br(),
    html.Br(),

    dbc.Row([dbc.Col(), dbc.Col(), dbc.Col(),
             html.H2("Next Days Predictions", style={"fontSize": "30px", "margin-top": "20px", "color": "white",
                                                     "background-color": "#102031", "margin-bottom": "20px"}),
             dbc.Col(), dbc.Col(), dbc.Col()]),

    dbc.Row([dbc.Col(),
             dbc.Col(html.Div([dash_table.DataTable(
                 id='table',
                 columns=[
                     {"name": i, "id": i, "deletable": True, "selectable": True} for i in predictions_dataset.columns
                 ],
                 data=predictions_dataset.to_dict('records'),
                 editable=True,
                 row_deletable=True,
                 style_cell=dict(textAlign='center'),
                 style_header=dict(backgroundColor="#CAECD8"),
                 style_data=dict(backgroundColor="lavender"),
                 style_table={"height": "500px", "width": "400", 'overflowY': 'auto'},
                 page_size=20,
                 filter_action='native',
                 sort_action='native',
                 sort_mode='single',
                 sort_by=[{'column_id': 'pop', 'direction': 'asc'}])])),
             dbc.Col(),
             ]),

    html.Br(),
    html.Br(),

    dbc.Row([dbc.Col(), dbc.Col(), dbc.Col(),
             html.H2("Archived Predictions", style={"fontSize": "30px", "margin-top": "20px", "color": "white",
                                                    "background-color": "#102031", "margin-bottom": "20px"}),
             dbc.Col(), dbc.Col(), dbc.Col()]),

    dbc.Row([dbc.Col(),
             dbc.Col(html.Div([dash_table.DataTable(
                 id='table',
                 columns=[
                     {"name": i, "id": i, "deletable": True, "selectable": True} for i in archived_predictions.columns
                 ],
                 data=archived_predictions.to_dict('records'),
                 editable=True,
                 row_deletable=True,
                 style_cell=dict(textAlign='center'),
                 style_header=dict(backgroundColor="#CAECD8"),
                 style_data=dict(backgroundColor="lavender"),
                 style_table={"height": "500px", "width": "400", 'overflowY': 'auto'},
                 page_size=20,
                 filter_action='native',
                 sort_action='native',
                 sort_mode='single',
                 sort_by=[{'column_id': 'pop', 'direction': 'asc'}])])),
             dbc.Col(),
             ]),

    html.Br(),
    html.Br(),

    dbc.Row([dbc.Col(), dbc.Col(), dbc.Col(),
             html.H2("Summary Statistics", style={"fontSize": "30px", "margin-top": "20px", "color": "white",
                                                  "background-color": "#102031", "margin-bottom": "20px"}),
             dbc.Col(), dbc.Col(), dbc.Col()]),

    dbc.Row([dbc.Col(), dbc.Col(),
             dbc.Col(html.Div([dash_table.DataTable(
                 id='table',
                 columns=[
                     {"name": i, "id": i, "selectable": True} for i in predictions_summary_table.columns
                 ],
                 data=predictions_summary_table.to_dict('records'),
                 style_cell=dict(textAlign='center'),
                 style_header=dict(backgroundColor="#CAECD8"),
                 style_data=dict(backgroundColor="lavender"),
                 style_table={"height": "480px", 'overflowY': 'auto'},
                 tooltip_delay=0,
                 tooltip_duration=None,
                 tooltip_data=[{"How_Many_Lines": str(recommended_preds_archive[['Date', 'Home_Team',
                                                                                 'Away_Team']].reset_index(
                     drop=True))}],
                 # tooltip_data=[{
                 #     column: {'value': str(value), 'type': 'markdown'}
                 #     for column, value in row.items()
                 # } for row in predictions_summary_table.to_dict('records') ],
                 sort_action='native',
                 sort_mode='single',
                 sort_by=[{'column_id': 'pop', 'direction': 'asc'}])])),

             dbc.Col(), dbc.Col(), ]),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),

    dash_footer,

], style={"background-color": "#102031"})
