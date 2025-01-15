import dash
from dash import dcc, html

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(
    children=[
        dcc.Tabs(
            id='tabs',
            children=[
                dcc.Tab(
                    label='Shopee',
                    children=[
                        html.Div(
                            children=[
                                html.Img(
                                    src='https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Shopee.svg/1200px-Shopee.svg.png',
                                    style={'height': '50px', 'width': 'auto', 'margin': 'auto', 'display': 'block'}
                                ),
                                html.Div("Shopee Content Here", style={'textAlign': 'center'})
                            ],
                            style={'textAlign': 'center', 'padding': '20px'}
                        ),
                    ],
                    style={
                        'fontSize': '18px', 
                        'fontWeight': 'bold', 
                        'backgroundColor': '#FF5722',  # Shopee brand color
                        'color': 'white',
                        'textAlign': 'center'
                    },
                    selected_style={
                        'fontSize': '18px', 
                        'fontWeight': 'bold', 
                        'backgroundColor': '#FF5722', 
                        'color': 'white',
                        'textAlign': 'center'
                    }
                ),
                dcc.Tab(
                    label='Tiki',
                    children=[
                        html.Div(
                            children=[
                                html.Img(
                                    src='https://upload.wikimedia.org/wikipedia/commons/4/43/Logo_Tiki_2023.png',
                                    style={'height': '50px', 'width': 'auto', 'margin': 'auto', 'display': 'block'}
                                ),
                                html.Div("Tiki Content Here", style={'textAlign': 'center'})
                            ],
                            style={'textAlign': 'center', 'padding': '20px'}
                        ),
                    ],
                    style={
                        'fontSize': '18px', 
                        'fontWeight': 'bold', 
                        'backgroundColor': '#00A0E9',  # Tiki brand color
                        'color': 'white',
                        'textAlign': 'center'
                    },
                    selected_style={
                        'fontSize': '18px', 
                        'fontWeight': 'bold', 
                        'backgroundColor': '#00A0E9', 
                        'color': 'white',
                        'textAlign': 'center'
                    }
                ),
                dcc.Tab(
                    label='Lazada',
                    children=[
                        html.Div(
                            children=[
                                html.Img(
                                    src='https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Lazada_%282019%29.svg/1200px-Lazada_%282019%29.svg.png',
                                    style={'height': '50px', 'width': 'auto', 'margin': 'auto', 'display': 'block'}
                                ),
                                html.Div("Lazada Content Here", style={'textAlign': 'center'})
                            ],
                            style={'textAlign': 'center', 'padding': '20px'}
                        ),
                    ],
                    style={
                        'fontSize': '18px', 
                        'fontWeight': 'bold', 
                        'backgroundColor': '#FF6A00',  # Lazada brand color
                        'color': 'white',
                        'textAlign': 'center'
                    },
                    selected_style={
                        'fontSize': '18px', 
                        'fontWeight': 'bold', 
                        'backgroundColor': '#FF6A00', 
                        'color': 'white',
                        'textAlign': 'center'
                    }
                ),
            ],
            style={'width': '100%', 'margin': '0 auto'}
        ),
    ],
    style={'padding': '20px'}
)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
