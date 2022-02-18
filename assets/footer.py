import dash_html_components as html
import dash_bootstrap_components as dbc
from assets.functions_and_datasets import image_base

kostas_encoded_image = image_base('assets/images/kostas.png')

dash_footer = html.Div([

    dbc.Row([
        dbc.Col(html.Img(src='data:image/png;base64,{}'.format(kostas_encoded_image.decode(),
                                                               ), style={'width': '60%',
                                                                         'height': '95%', 'margin-left': '80px', })),
        dbc.Col([html.H3("Contact Details", style={'backgroundColor': 'black', 'color': 'white',
                                                   'font-family': 'cursive', 'text-align': 'center',
                                                   'font-weight': 'bold', 'margin-top': '30px',
                                                   'margin-right': '70px'}),
                 html.A(
                     html.Button('Github', style={'color': 'white', 'backgroundColor': 'black',
                                                  'width': '50%', 'height': '20%', 'text-align': 'center',
                                                  'margin-left': '80px', 'fontSize': '20', 'margin-top': '30px'
                                                  }),
                     href='https://github.com/Konstantinos-Sakellariou'),
                 html.Div(
                     [dbc.Button("E-mail", id="open", style={'color': 'white', 'backgroundColor': 'black',
                                                             'width': '50%', 'height': '40%',
                                                             'text-align': 'center',
                                                             'margin-left': '80px', 'fontSize': '20',
                                                             'margin-top': '30px'
                                                             }),
                      dbc.Modal(
                          [dbc.ModalHeader("E-mail"),
                           dbc.ModalBody("konstantinossakellariou@gmail.com"),
                           dbc.ModalFooter(
                               dbc.Button("CLOSE", id="close", className="ml-auto")
                           )], id="modal")])
                 ]),
        dbc.Col(),
        dbc.Col(),
    ])], style={"background-color": "black", "margin-bottom": "0px auto",
                "height": "280px", "margin-top": "0px",
                'justify-content': 'center'})
