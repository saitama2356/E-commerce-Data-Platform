import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import sqlite3
import numpy as np

# Create Dash app
app = dash.Dash(__name__)

# Connect to database and get data
con = sqlite3.connect('e-com.sqlite')
df = pd.read_sql_query("SELECT * FROM fact_sales;", con)
con.close()

# Convert timestamp to datetime
df['scraped_timestamp'] = pd.to_datetime(df['scraped_timestamp'])

# Updated styles with more responsive design
CONTAINER_STYLE = {
    'maxWidth': '98%',
    'margin': '0 auto',
    'padding': '10px'
}

CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '8px',
    'padding': '15px',
    'margin': '8px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'height': '100%'  # Make all cards same height in a row
}

HEADER_STYLE = {
    'color': '#2196F3',
    'marginBottom': '15px',
    'fontSize': '18px',
    'fontWeight': 'bold'
}

GRID_CONTAINER = {
    'display': 'grid',
    'gridTemplateColumns': 'repeat(auto-fit, minmax(450px, 1fr))',
    'gap': '16px',
    'padding': '10px'
}

def create_tab1_layout():
    """Create layout for Overview tab"""
    return html.Div([
        html.H1('Tổng quan', style={
            'textAlign': 'center',
            'color': '#1976D2',
            'margin': '20px 0'
        }),
        
        html.Div([
            # Summary section
            html.Div([
                html.H3("Tóm tắt", style=HEADER_STYLE),
                html.P(f"""\
                    Báo cáo lúc {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}. 
                    Nền tảng dữ liệu thương mại điện tử cung cấp cái nhìn toàn diện về thị trường sản phẩm điện tử 
                    trên {', '.join(df['platform'].unique())}.""",
                    style={'lineHeight': '1.5', 'color': '#666'}
                )
            ], style=CARD_STYLE),

            # Grid container for metrics and charts
            html.Div([
                # Key metrics card
                html.Div([
                    html.H3("Chỉ số chính", style=HEADER_STYLE),
                    html.Div([
                        html.Div([
                            html.H4("Số sản phẩm", style={'fontSize': '16px'}),
                            html.P(f"{len(df['itemId'].unique()):,}", style={'fontSize': '24px', 'fontWeight': 'bold'})
                        ], style={'flex': '1', 'textAlign': 'center'}),
                        html.Div([
                            html.H4("Số nền tảng", style={'fontSize': '16px'}),
                            html.P(f"{len(df['platform'].unique())}", style={'fontSize': '24px', 'fontWeight': 'bold'})
                        ], style={'flex': '1', 'textAlign': 'center'}),
                        html.Div([
                            html.H4("Đánh giá TB", style={'fontSize': '16px'}),
                            html.P(f"{df['rating'].mean():.2f}", style={'fontSize': '24px', 'fontWeight': 'bold'})
                        ], style={'flex': '1', 'textAlign': 'center'})
                    ], style={'display': 'flex', 'justifyContent': 'space-around', 'gap': '10px'})
                ], style=CARD_STYLE),

                # Platform distribution
                html.Div([
                    html.H3("Phân bố theo nền tảng", style=HEADER_STYLE),
                    dcc.Graph(
                        figure=px.pie(
                            df, 
                            names='platform',
                            title="Phân bố sản phẩm theo nền tảng"
                        ).update_layout(
                            margin=dict(l=20, r=20, t=30, b=20),
                            height=300
                        ),
                        config={'displayModeBar': False}
                    )
                ], style=CARD_STYLE),

                # Rating distribution
                html.Div([
                    html.H3("Phân bố đánh giá", style=HEADER_STYLE),
                    dcc.Graph(
                        figure=px.histogram(
                            df, 
                            x='rating',
                            nbins=20,
                            title="Phân bố điểm đánh giá"
                        ).update_layout(
                            margin=dict(l=20, r=20, t=30, b=20),
                            height=300
                        ),
                        config={'displayModeBar': False}
                    )
                ], style=CARD_STYLE)
            ], style=GRID_CONTAINER)
        ], style=CONTAINER_STYLE)
    ])

def create_tab2_layout():
    """Create layout for Price Analysis tab"""
    return html.Div([
        html.H1('Phân tích giá', style={
            'textAlign': 'center',
            'color': '#1976D2',
            'margin': '20px 0'
        }),
        
        html.Div([
            html.Div([
                # Statistics card
                html.Div([
                    html.H3("Thống kê theo nền tảng", style=HEADER_STYLE),
                    html.Div(style={'overflowX': 'auto'}, children=[
                        html.Table([
                            html.Thead(html.Tr([
                                html.Th(col, style={'padding': '8px', 'backgroundColor': '#f5f5f5'})
                                for col in ['Nền tảng', 'Số mẫu', 'Giá TB (VND)', 'Đánh giá TB']
                            ])),
                            html.Tbody([
                                html.Tr([
                                    html.Td(platform, style={'padding': '8px'}),
                                    html.Td(f"{len(df[df['platform'] == platform]):,}", style={'padding': '8px'}),
                                    html.Td(f"{df[df['platform'] == platform]['salePrice'].mean():,.0f}", style={'padding': '8px'}),
                                    html.Td(f"{df[df['platform'] == platform]['rating'].mean():.2f}", style={'padding': '8px'})
                                ]) for platform in df['platform'].unique()
                            ])
                        ], style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'})
                    ])
                ], style=CARD_STYLE),

                # Charts grid
                html.Div([
                    # Price distribution
                    html.Div([
                        html.H3("Phân phối giá", style=HEADER_STYLE),
                        dcc.Graph(
                            figure=px.histogram(
                                df,
                                x='salePrice',
                                nbins=20,
                                title="Phân phối giá sản phẩm"
                            ).update_layout(
                                margin=dict(l=20, r=20, t=30, b=20),
                                height=300
                            ),
                            config={'displayModeBar': False}
                        )
                    ], style=CARD_STYLE),

                    # Platform comparison
                    html.Div([
                        html.H3("So sánh giá theo nền tảng", style=HEADER_STYLE),
                        dcc.Graph(
                            figure=px.box(
                                df,
                                x='platform',
                                y='salePrice',
                                title="Phân phối giá theo nền tảng"
                            ).update_layout(
                                margin=dict(l=20, r=20, t=30, b=20),
                                height=300
                            ),
                            config={'displayModeBar': False}
                        )
                    ], style=CARD_STYLE)
                ], style=GRID_CONTAINER)
            ], style=CONTAINER_STYLE)
        ])
    ])

def create_tab3_layout():
    """Create layout for Review Analysis tab"""
    return html.Div([
        html.H1('Phân tích đánh giá', style={
            'textAlign': 'center',
            'color': '#1976D2',
            'margin': '20px 0'
        }),
        
        html.Div([
            # Summary card
            html.Div([
                html.H3("Tổng quan đánh giá", style=HEADER_STYLE),
                html.Div([
                    html.Div([
                        html.Strong("Tổng số đánh giá: "),
                        html.Span(f"{df['total_reviews'].sum():,}", style={'fontSize': '20px', 'color': '#2196F3'})
                    ], style={'marginBottom': '10px'}),
                    html.Div([
                        html.Strong("Điểm đánh giá trung bình: "),
                        html.Span(f"{df['rating'].mean():.2f}/5", style={'fontSize': '20px', 'color': '#2196F3'})
                    ])
                ])
            ], style=CARD_STYLE),

            # Charts grid
            html.Div([
                # Reviews by platform
                html.Div([
                    html.H3("Đánh giá theo nền tảng", style=HEADER_STYLE),
                    dcc.Graph(
                        figure=px.bar(
                            df.groupby('platform')['rating'].mean().reset_index(),
                            x='platform',
                            y='rating',
                            title="Điểm đánh giá trung bình theo nền tảng"
                        ).update_layout(
                            margin=dict(l=20, r=20, t=30, b=20),
                            height=300
                        ),
                        config={'displayModeBar': False}
                    )
                ], style=CARD_STYLE),

                # Rating vs Price
                html.Div([
                    html.H3("Tương quan giá - đánh giá", style=HEADER_STYLE),
                    dcc.Graph(
                        figure=px.scatter(
                            df,
                            x='salePrice',
                            y='rating',
                            color='platform',
                            title="Tương quan giữa giá và đánh giá"
                        ).update_layout(
                            margin=dict(l=20, r=20, t=30, b=20),
                            height=300
                        ),
                        config={'displayModeBar': False}
                    )
                ], style=CARD_STYLE)
            ], style=GRID_CONTAINER)
        ], style=CONTAINER_STYLE)
    ])

# Create the app layout with tabs
app.layout = html.Div([
    html.H1('Báo cáo phân tích E-commerce', style={
        'textAlign': 'center',
        'color': '#1976D2',
        'marginTop': '20px'
    }),
    
    dcc.Tabs([
        dcc.Tab(label='Tổng quan', children=create_tab1_layout()),
        dcc.Tab(label='Phân tích giá', children=create_tab2_layout()),
        dcc.Tab(label='Phân tích đánh giá', children=create_tab3_layout())
    ], style={
        'margin': '20px',
        'fontFamily': 'Arial'
    })
])

if __name__ == '__main__':
    app.run_server(debug=True, host='localhost', port=8050)