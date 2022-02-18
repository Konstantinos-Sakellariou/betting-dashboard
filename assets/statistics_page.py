import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from assets.functions_and_datasets import dataset
import pandas as pd
from assets.header import dash_header
from assets.footer import dash_footer


leagues = ['VTB', 'Super-Lig', 'LNB', 'Lega-A', 'Euroleague', 'Eurocup',
           'Champions-League', 'BBL', 'Basket-League', 'ACB', 'NBA', 'All_Leagues']

seasons = ['2010-2011', '2011-2012', '2012-2013', '2013-2014', '2014-2015', '2015-2016', '2016-2017',
           '2017-2018', '2018-2019', '2019-2020', '2020-2021', 'All_Seasons']

unique_teams = dataset.Home_Team.append(dataset.Away_Team).unique()
teams = list(pd.Series(unique_teams).append(pd.Series('All_Teams')))

stats_page = html.Div([

    dash_header,

    dbc.Container([

        dbc.Row([dbc.Col(), dbc.Col(), dbc.Col(),
                 dbc.Col(html.Div([
                     html.Label("!! Do Refresh the page after each selection",
                                style={"fontSize": "15px", "margin-bottom": "5px auto", "text-align": "center",
                                       "color": "red"})])), dbc.Col(), dbc.Col(), dbc.Col()]),

        dbc.Row([
            dbc.Col(),
            dbc.Col(),
            dbc.Col([
                html.Label("Filter 1: Season", style={"fontSize": "20px", "margin-bottom": "5px auto",
                                                      "text-align": "center", "color": "white"}),
                dcc.Dropdown(id='filter_1',
                             options=[{'label': i, 'value': i} for i in seasons],
                             value='All_Seasons', style={"background-color": "#CAECD8"},
                             multi=False,
                             persistence=True,
                             persistence_type='session'
                             )]),
            dbc.Col(html.Div([
                html.Label("Filter 2: League", style={"fontSize": "20px", "margin-bottom": "5px auto",
                                                      "text-align": "center", "color": "white"}),
                dcc.Dropdown(id='filter_2',
                             options=[{'label': i, 'value': i} for i in leagues],
                             value='All_Leagues', style={"background-color": "#CAECD8"},
                             multi=False,
                             persistence=True,
                             persistence_type='session'
                             )])),
            dbc.Col(html.Div([
                html.Label("Filter 3: Team", style={"fontSize": "20px", "margin-bottom": "5px auto",
                                                    "text-align": "center", "color": "white"}),
                dcc.Dropdown(id='filter_3',
                             options=[{'label': i, 'value': i} for i in teams],
                             value='All_Teams', style={"background-color": "#CAECD8"},
                             multi=False,
                             persistence=True,
                             persistence_type='session'
                             )])),
            dbc.Col(),
            dbc.Col(),
        ]),

        html.Br(),

        html.Div(id="table_stats", style={"background-color": "#102031"})], fluid=True),

    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),

    dash_footer,

], style={"background-color": "#102031"})
