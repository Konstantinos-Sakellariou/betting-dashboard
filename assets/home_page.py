import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
from assets.functions_and_datasets import dataset
from assets.header import dash_header
from assets.footer import dash_footer

leagues = ['VTB', 'Super-Lig', 'LNB', 'Lega-A', 'Euroleague', 'Eurocup',
           'Champions-League', 'BBL', 'Basket-League', 'ACB', 'NBA', 'All_Leagues']

seasons = ['2010-2011', '2011-2012', '2012-2013', '2013-2014', '2014-2015', '2015-2016', '2016-2017',
           '2017-2018', '2018-2019', '2019-2020', '2020-2021', 'All_Seasons']

indicators = dataset.columns

unique_teams = dataset.Home_Team.append(dataset.Away_Team).unique()
teams = list(pd.Series(unique_teams).append(pd.Series('All_Teams')))

home_page = html.Div([

    dash_header,

    dbc.Row([dbc.Col(),
             dbc.Col([html.H3("League Analysis")],
                     style={"color": "white", "fontSize": "30px", "font-family": "cursive",
                            "margin-top": "5px", "margin-bottom": "5px"}),
             dbc.Col(),
             dbc.Col([html.H3("Team Analysis")], style={"fontSize": "30px", "color": "white", "font-family": "cursive",
                                                        "position": "relative", "left": "150px", "top": "0px",
                                                        "margin-top": "5px", "margin-bottom": "5px"}),
             dbc.Col(), ],
            style={"background-color": "#102031"}),

    dbc.Row([
        dbc.Col([html.Div([
            html.Label("X-axis feature", style={"fontSize": "20px", "margin-bottom": "5px auto",
                                                "text-align": "center", "position": "relative",
                                                "left": "125px", "top": "0px", "color": "white"}),
            dcc.Dropdown(id='X-axis_feature',
                         options=[{'label': i, 'value': i} for i in indicators],
                         value='Line', style={"background-color": "#CAECD8"},
                         multi=False,
                         persistence=True,
                         persistence_type='session')])]),

        dbc.Col(html.Div([
            html.Label("Y-axis feature", style={"fontSize": "20px", "margin-bottom": "5px auto",
                                                "text-align": "center", "position": "relative",
                                                "left": "125px", "top": "0px", "color": "white"}),
            dcc.Dropdown(id='Y-axis_feature',
                         options=[{'label': i, 'value': i} for i in indicators],
                         value='League', style={"background-color": "#CAECD8"},
                         multi=False,
                         persistence=True,
                         persistence_type='session'
                         )])),

        #  right side

        dbc.Col(html.Div([
            html.Label("Choose Team", style={"fontSize": "20px", "margin-bottom": "5px auto",
                                             "text-align": "center", "position": "relative",
                                             "left": "125px", "top": "0px", "color": "white"}),
            dcc.Dropdown(id='team',
                         options=[{'label': i, 'value': i} for i in teams],
                         value='Olympiacos', style={"background-color": "#CAECD8", "width": "1"},
                         multi=False,
                         persistence=True,
                         persistence_type='session'
                         )])),
        dbc.Col(html.Div([
            html.Label("Choose Season", style={"fontSize": "20px", "margin-bottom": "5px auto",
                                               "text-align": "center", "position": "relative",
                                               "left": "125px", "top": "0px", "color": "white"}),
            dcc.Dropdown(id='season_2',
                         options=[{'label': i, 'value': i} for i in seasons],
                         value='All_Seasons', style={"background-color": "#CAECD8", "width": "1"},
                         multi=False,
                         persistence=True,
                         persistence_type='session'
                         )])),

    ], style={"background-color": "#102031"}),

    dbc.Row([
        dbc.Col([html.Div([
            html.Label("Choose League", style={"fontSize": "20px", "margin-bottom": "5px auto",
                                               "text-align": "center", "position": "relative",
                                               "left": "125px", "top": "0px", "color": "white"}),
            dcc.Dropdown(id='league_choose',
                         options=[{'label': i, 'value': i} for i in leagues],
                         value='All_Leagues', style={"background-color": "#CAECD8"},
                         multi=False,
                         persistence=True,
                         persistence_type='session')])

        ]),
        dbc.Col(html.Div([
            html.Label("Choose Season", style={"fontSize": "20px", "margin-bottom": "5px auto",
                                               "text-align": "center", "position": "relative",
                                               "left": "125px", "top": "0px", "color": "white"}),
            dcc.Dropdown(id='season',
                         options=[{'label': i, 'value': i} for i in seasons],
                         value='All_Seasons', style={"background-color": "#CAECD8", "width": "1"},
                         multi=False,
                         persistence=True,
                         persistence_type='session'
                         )])),
        dbc.Col(html.Div([
            html.Label("X-axis feature", style={"fontSize": "20px", "margin-bottom": "5px auto",
                                                "text-align": "center", "position": "relative",
                                                "right": "-125px", "top": "0px", "color": "white"}),
            dcc.Dropdown(id='X-axis_feature_right',
                         options=[{'label': i, 'value': i} for i in indicators],
                         value='Line', style={"background-color": "#CAECD8"},
                         multi=False,
                         persistence=True,
                         persistence_type='session')])),

        dbc.Col(html.Div([
            html.Label("Y-axis feature", style={"fontSize": "20px", "margin-bottom": "5px auto",
                                                "text-align": "center", "position": "relative",
                                                "right": "-125px", "top": "0px", "color": "white"}),
            dcc.Dropdown(id='Y-axis_feature_right',
                         options=[{'label': i, 'value': i} for i in indicators],
                         value='Score_home', style={"background-color": "#CAECD8"},
                         multi=False,
                         persistence=True,
                         persistence_type='session'
                         )]))
    ], style={"background-color": "#102031"}),

    dbc.Row([dbc.Col([dcc.Graph(id='my_dashboard', figure={})], style={"background-color": "#102031",
                                                                       "width": "40%"}),
             dbc.Col([dcc.Graph(id='my_second_dashboard', figure={})], style={"background-color": "#102031",
                                                                              "width": "40%"})],
            style={"background-color": "#102031"}),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),

    dash_footer,

], style={"background-color": "#102031"})
