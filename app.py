import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output, State
import dash_table
import dash_bootstrap_components as dbc

from assets.statistics_page import stats_page
from assets.predictions_page import preds_page
from assets.home_page import home_page
from assets.functions_and_datasets import dataset


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

body = home_page

statistics_body = stats_page

predictions_body = preds_page

url_bar_and_content_div = html.Div([
                                    dcc.Location(id='url', refresh=True),
                                    html.Div(id='page-content'),
                                    ])
# index layout
app.layout = url_bar_and_content_div

# "complete" layout
app.validation_layout = html.Div([
                                    url_bar_and_content_div,
                                    body,
                                    statistics_body,
                                    predictions_body
                                  ])
# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
# Index callbacks


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == "/Predictions":
        return predictions_body
    elif pathname == "/Statistics":
        return statistics_body
    else:
        return body


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(Output('table_stats', 'children'),
              [Input('filter_1', 'value'),
               Input('filter_2', 'value'),
               Input('filter_3', 'value')
               ])
def update_graphs(filter_1, filter_2, filter_3):
    if filter_1 == 'All_Seasons':

        if filter_2 == 'All_Leagues':

            if filter_3 == 'All_Teams':

                dash_table_1 = html.Div([dash_table.DataTable(
                    id='table_stats',
                    columns=[{"name": i, "id": i}
                             for i in dataset.columns],
                    data=dataset.to_dict('records'),
                    style_cell=dict(textAlign='center'),
                    style_header=dict(backgroundColor="#CAECD8"),
                    style_data=dict(backgroundColor="lavender"),
                    style_table={"height": "500px", "width": "400", 'overflowY': 'auto'},
                    page_size=14,
                    sort_action='native',
                    filter_action='native',
                    sort_mode='single',
                    sort_by=[{'column_id': 'pop', 'direction': 'asc'}])])
            else:
                data = dataset.loc[dataset.Home_Team == filter_3]
                data = data.append(dataset.loc[dataset.Away_Team == filter_3])
                data = data.sort_values(by='Date')

                dash_table_1 = html.Div([dash_table.DataTable(
                    id='table_stats',
                    columns=[{"name": i, "id": i}
                             for i in data.columns],
                    data=data.to_dict('records'),
                    style_cell=dict(textAlign='center'),
                    style_header=dict(backgroundColor="#CAECD8"),
                    style_data=dict(backgroundColor="lavender"),
                    style_table={"height": "500px", "width": "400", 'overflowY': 'auto'},
                    page_size=14,
                    sort_action='native',
                    filter_action='native',
                    sort_mode='single',
                    sort_by=[{'column_id': 'pop', 'direction': 'asc'}])])

        elif filter_2 != 'All_Leagues':

            data = dataset.loc[dataset.League == filter_2]

            if filter_3 == 'All_Teams':

                dash_table_1 = html.Div([dash_table.DataTable(
                    id='table_stats',
                    columns=[{"name": i, "id": i}
                             for i in data.columns],
                    data=data.to_dict('records'),
                    style_cell=dict(textAlign='center'),
                    style_header=dict(backgroundColor="#CAECD8"),
                    style_data=dict(backgroundColor="lavender"),
                    style_table={"height": "500px", "width": "400", 'overflowY': 'auto'},
                    page_size=14)])
            else:
                data = dataset.loc[dataset.Home_Team == filter_3]
                data = data.append(dataset.loc[dataset.Away_Team == filter_3])
                data = data.sort_values(by='Date')

                dash_table_1 = html.Div([dash_table.DataTable(
                    id='table_stats',
                    columns=[{"name": i, "id": i}
                             for i in data.columns],
                    data=data.to_dict('records'),
                    style_cell=dict(textAlign='center'),
                    style_header=dict(backgroundColor="#CAECD8"),
                    style_data=dict(backgroundColor="lavender"),
                    style_table={"height": "500px", "width": "400", 'overflowY': 'auto'},
                    page_size=14)])

    elif filter_1 != 'All_Seasons':

        data = dataset.loc[dataset.Season == filter_1]

        if filter_2 == 'All_Leagues':

            if filter_3 == 'All_Teams':

                dash_table_1 = html.Div([dash_table.DataTable(
                    id='table_stats',
                    columns=[{"name": i, "id": i}
                             for i in data.columns],
                    data=data.to_dict('records'),
                    style_cell=dict(textAlign='center'),
                    style_header=dict(backgroundColor="#CAECD8"),
                    style_data=dict(backgroundColor="lavender"),
                    style_table={"height": "500px", "width": "400", 'overflowY': 'auto'},
                    page_size=14)])
            else:
                data = dataset.loc[dataset.Home_Team == filter_3]
                data = data.append(dataset.loc[dataset.Away_Team == filter_3])
                data = data.sort_values(by='Date')

                dash_table_1 = html.Div([dash_table.DataTable(
                    id='table_stats',
                    columns=[{"name": i, "id": i}
                             for i in data.columns],
                    data=data.to_dict('records'),
                    style_cell=dict(textAlign='center'),
                    style_header=dict(backgroundColor="#CAECD8"),
                    style_data=dict(backgroundColor="lavender"),
                    style_table={"height": "500px", "width": "400", 'overflowY': 'auto'},
                    page_size=14)])

        elif filter_2 != 'All_Leagues':

            data = dataset.loc[dataset.League == filter_2]

            if filter_3 == 'All_Teams':

                dash_table_1 = html.Div([dash_table.DataTable(
                    id='table_stats',
                    columns=[{"name": i, "id": i}
                             for i in data.columns],
                    data=data.to_dict('records'),
                    style_cell=dict(textAlign='center'),
                    style_header=dict(backgroundColor="#CAECD8"),
                    style_data=dict(backgroundColor="lavender"),
                    style_table={"height": "500px", "width": "400", 'overflowY': 'auto'},
                    page_size=14)])
            else:
                data = dataset.loc[dataset.Home_Team == filter_3]
                data = data.append(dataset.loc[dataset.Away_Team == filter_3])
                data = data.sort_values(by='Date')

                dash_table_1 = html.Div([dash_table.DataTable(
                    id='table_stats',
                    columns=[{"name": i, "id": i}
                             for i in data.columns],
                    data=data.to_dict('records'),
                    style_cell=dict(textAlign='center'),
                    style_header=dict(backgroundColor="#CAECD8"),
                    style_data=dict(backgroundColor="lavender"),
                    style_table={"height": "500px", "width": "400", 'overflowY': 'auto'},
                    page_size=14)])

    return dash_table_1


@app.callback(
    [Output(component_id='my_dashboard', component_property='figure'),
     Output(component_id='my_second_dashboard', component_property='figure')],
    [Input(component_id='X-axis_feature', component_property='value'),
     Input(component_id='Y-axis_feature', component_property='value'),
     Input(component_id='league_choose', component_property='value'),
     Input(component_id='season', component_property='value'),
     Input(component_id='X-axis_feature_right', component_property='value'),
     Input(component_id='Y-axis_feature_right', component_property='value'),
     Input(component_id='team', component_property='value'),
     Input(component_id='season_2', component_property='value')]
)
def update_graph(x_axis, y_axis, league, season, x_axis_right, y_axis_right, team, season_2):
    if league == 'All_Leagues':

        if season == 'All_Seasons':

            fig = px.scatter(data_frame=dataset, x=x_axis, y=y_axis, title='My dataset Analysis',
                             hover_data=['League', 'Date', 'Home_Team', 'Away_Team'], template='plotly_dark', )

            fig.update_layout(title_xanchor="center",
                              title_font=dict(size=24),
                              title_x=0.5, )
        else:
            data = dataset.copy()
            data = data.loc[data.Season == season]

            fig = px.scatter(data_frame=data, x=x_axis, y=y_axis, title='My dataset Analysis',
                             hover_data=['Date', 'Home_Team', 'Away_Team'], template='plotly_dark')

            fig.update_layout(title_xanchor="center",
                              title_font=dict(size=24),
                              title_x=0.5, )

    else:
        data_else = dataset.loc[dataset.League == league]

        if season == 'All_Seasons':

            fig = px.scatter(data_frame=data_else, x=x_axis, y=y_axis, title='My dataset Analysis',
                             hover_data=['Date', 'Home_Team', 'Away_Team'], template='plotly_dark')

            fig.update_layout(title_xanchor="center",
                              title_font=dict(size=24),
                              title_x=0.5)

        else:
            data_else_season = data_else.copy()
            data_else_season = data_else_season.loc[data_else_season.Season == season]

            fig = px.scatter(data_frame=data_else_season, x=x_axis, y=y_axis, title='My dataset Analysis',
                             hover_data=['Date', 'Home_Team', 'Away_Team'], template='plotly_dark')

            fig.update_layout(title_xanchor="center",
                              title_font=dict(size=24),
                              title_x=0.5)

    if season_2 == 'All_Seasons':

        team_data = dataset.copy()
        team_data = (team_data.loc[team_data.Home_Team == team]).append(team_data.loc[team_data.Away_Team == team])
        team_data['hue'] = ['Home' if i == team else 'Away' for i in team_data.Home_Team]

        fig2 = px.scatter(data_frame=team_data, x=x_axis_right, y=y_axis_right, title='My Team Analysis',
                          hover_data=['League', 'Date', 'Score_home', 'Score_away',
                                      'Home_Team', 'Away_Team'], template='plotly_dark', color=team_data['hue'])

        fig2.update_layout(title_xanchor="center",
                           title_font=dict(size=24),
                           title_x=0.5)

    else:
        team_data = dataset.copy()
        team_data = (team_data.loc[team_data.Home_Team == team]).append(team_data.loc[team_data.Away_Team == team])
        team_data = team_data.loc[team_data.Season == season_2]
        team_data['hue'] = ['Home' if i == team else 'Away' for i in team_data.Home_Team]

        fig2 = px.scatter(data_frame=team_data, x=x_axis_right, y=y_axis_right, title='My dataset Analysis',
                          hover_data=['Date', 'Home_Team', 'Away_Team'], template='plotly_dark', color=team_data['hue'])

        fig2.update_layout(title_xanchor="center",
                           title_font=dict(size=24),
                           title_x=0.5)

    return fig, fig2


if __name__ == "__main__":
    app.run_server(debug=True)
