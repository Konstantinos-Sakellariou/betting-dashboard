import dash_html_components as html
import dash_bootstrap_components as dbc
from assets.functions_and_datasets import image_base

milos_encoded_image = image_base('assets/images/milos.jpg')
spanoulis_encoded_image = image_base('assets/images/span00gg.png')
rudy_encoded_image = image_base('assets/images/rudyblack.png')
batiste_encoded_image = image_base('assets/images/batiste.jpg')
wade_encoded_image = image_base('assets/images/wade.jpg')
lebrondunk_encoded_image = image_base('assets/images/lebrondunk.jpg')

dash_header = html.Div([
        dbc.Row(
            [
                dbc.Col(html.Img(src='data:image/jpg;base64,{}'.format(milos_encoded_image.decode()),
                                 style={'height': '90%', 'width': '70%'})),

                dbc.Col(html.Img(src='data:image/png;base64,{}'.format(spanoulis_encoded_image.decode()),
                                 style={'height': '100%', 'width': '100%'})),

                dbc.Col(html.Img(src='data:image/jpg;base64,{}'.format(wade_encoded_image.decode()),
                                 style={'height': '90%', 'width': '70%'})),

                dbc.Col([html.H1("Betting and Analysis DashBoard", style={"font-family": "cursive"}),
                         html.A(
                             html.Button('Home', id='url_home', style={"color": "yellow", "background-color": "black"}),
                             href='/Home',
                             style={"fontSize": "25px", "text-align": "center", "color": "yellow",
                                    "background-color": "yellow", "margin-right": "25px"}),
                         html.A(html.Button('Data', id='url_statistics',
                                            style={"color": "yellow", "background-color": "black"}),
                                href='/Statistics',
                                style={"fontSize": "25px", "text-align": "center", "color": "yellow",
                                       "background-color": "yellow"}),
                         html.A(html.Button('Predictions', id='url_predictions',
                                            style={"color": "yellow", "background-color": "black"}),
                                href='/Predictions',
                                style={"fontSize": "25px", "text-align": "center", "color": "yellow",
                                       "background-color": "yellow", "margin-bottom": "5px auto",
                                       })
                         ], width=2, sm=2, ),

                dbc.Col(html.Img(src='data:image/jpg;base64,{}'.format(lebrondunk_encoded_image.decode()),
                                 style={'height': '90%', 'width': '70%'})),

                dbc.Col(html.Img(src='data:image/png;base64,{}'.format(rudy_encoded_image.decode()),
                                 style={'height': '100%', 'width': '100%'})),

                dbc.Col(html.Img(src='data:image/jpg;base64,{}'.format(batiste_encoded_image.decode()),
                                 style={'height': '90%', 'width': '70%'}), )]),

    ],
        style={"background-color": "black", "margin-bottom": "0px auto",
               "fontSize": "40px", "text-align": "center",
               "color": "yellow", "margin-top": "0px",
               'justify-content': 'center'})