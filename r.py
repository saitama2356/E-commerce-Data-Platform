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

# Common styles
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '8px',
    'padding': '20px',
    'margin': '10px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
}

HEADER_STYLE = {
    'color': '#2196F3',
    'marginBottom': '15px',
    'fontSize': '18px'
}

def create_tab1_layout():
    """Create layout for Overview tab"""
    return html.Div([
        html.H1('Tổng quan', style={
            'textAlign': 'center',
            'color': '#1976D2',
            'marginBottom': '30px',
            'marginTop': '20px'
        }),
        
        html.Div([
            # Left Column
            html.Div([
                # Summary section
                html.Div([
                    html.H3("Tóm tắt", style=HEADER_STYLE),
                    html.P(f"""\
                        Báo cáo lúc {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}. 
                        Nền tảng dữ liệu thương mại điện tử cung cấp cái nhìn toàn diện về thị trường sản phẩm điện tử 
                        trên {', '.join(df['platform'].unique())}. 
                        
                        Báo cáo tập trung vào việc phân tích hiệu suất của các sản phẩm thuộc ngành hàng điện tử, 
                        bao gồm doanh thu, đánh giá từ khách hàng, và mức độ cạnh tranh giữa các nền tảng.""",
                        style={'lineHeight': '1.5', 'color': '#666'}
                    )
                ], style=CARD_STYLE),
                
                # Key metrics
                html.Div([
                    html.H3("Chỉ số chính", style=HEADER_STYLE),
                    html.Div([
                        html.Div([
                            html.H4("Số sản phẩm"),
                            html.P(f"{len(df['itemId'].unique()):,}")
                        ], style={'textAlign': 'center', 'flex': '1'}),
                        html.Div([
                            html.H4("Số nền tảng"),
                            html.P(f"{len(df['platform'].unique())}")
                        ], style={'textAlign': 'center', 'flex': '1'}),
                        html.Div([
                            html.H4("Đánh giá TB"),
                            html.P(f"{df['rating'].mean():.2f}")
                        ], style={'textAlign': 'center', 'flex': '1'})
                    ], style={'display': 'flex', 'justifyContent': 'space-around'})
                ], style=CARD_STYLE)
            ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            
            # Right Column
            html.Div([
                # Platform distribution
                html.Div([
                    html.H3("Phân bố theo nền tảng", style=HEADER_STYLE),
                    dcc.Graph(
                        figure=px.pie(
                            df, 
                            names='platform', 
                            title="Phân bố sản phẩm theo nền tảng"
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
                        ),
                        config={'displayModeBar': False}
                    )
                ], style=CARD_STYLE)
            ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ], style={'maxWidth': '1200px', 'margin': '0 auto'})
    ])

def create_tab2_layout():
    """Create layout for Price Analysis tab"""
    # Create price trend figure
    price_trend = go.Figure()
    for item in df['itemId'].unique():
        item_data = df[df['itemId'] == item]
        price_trend.add_trace(go.Scatter(
            x=item_data['scraped_timestamp'],
            y=item_data['salePrice']/1000000,
            name=f'Item {item}',
            mode='lines+markers'
        ))
    price_trend.update_layout(
        title="Diễn biến giá theo thời gian",
        xaxis_title="Thời gian",
        yaxis_title="Giá (Triệu VND)",
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    # Calculate summary statistics
    summary_stats = df.groupby('platform').agg({
        'salePrice': ['count', 'mean', 'std', 'min', 'max'],
        'total_reviews': ['mean', 'max'],
        'rating': 'mean'
    }).round(2)

    return html.Div([
        html.H1('Phân tích giá', style={
            'textAlign': 'center',
            'color': '#1976D2',
            'marginBottom': '30px',
            'marginTop': '20px'
        }),
        
        html.Div([
            # Left Column
            html.Div([
                # Statistics table
                html.Div([
                    html.H3("Thống kê theo nền tảng", style=HEADER_STYLE),
                    html.Table([
                        # Header
                        html.Thead(html.Tr([
                            html.Th('Nền tảng'),
                            html.Th('Số mẫu'),
                            html.Th('Giá TB (VND)'),
                            html.Th('Đánh giá TB')
                        ], style={'backgroundColor': '#f5f5f5'})),
                        # Body
                        html.Tbody([
                            html.Tr([
                                html.Td(platform),
                                html.Td(f"{summary_stats.loc[platform, ('salePrice', 'count')]:,.0f}"),
                                html.Td(f"{summary_stats.loc[platform, ('salePrice', 'mean')]:,.0f}"),
                                html.Td(f"{summary_stats.loc[platform, ('rating', 'mean')]:.2f}")
                            ]) for platform in df['platform'].unique()
                        ])
                    ], style={
                        'width': '100%',
                        'borderCollapse': 'collapse',
                        'border': '1px solid #ddd'
                    })
                ], style=CARD_STYLE),
                
                # Price range distribution
                html.Div([
                    html.H3("Phân phối khoảng giá", style=HEADER_STYLE),
                    dcc.Graph(
                        figure=px.histogram(
                            df,
                            x='salePrice',
                            nbins=20,
                            title="Phân phối giá sản phẩm"
                        ),
                        config={'displayModeBar': False}
                    )
                ], style=CARD_STYLE)
            ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            
            # Right Column
            html.Div([
                # Price trend chart
                html.Div([
                    html.H3("Biến động giá", style=HEADER_STYLE),
                    dcc.Graph(figure=price_trend, config={'displayModeBar': False})
                ], style=CARD_STYLE),
                
                # Platform box plot
                html.Div([
                    html.H3("So sánh giá theo nền tảng", style=HEADER_STYLE),
                    dcc.Graph(
                        figure=px.box(
                            df,
                            x='platform',
                            y='salePrice',
                            title="Phân phối giá theo nền tảng"
                        ),
                        config={'displayModeBar': False}
                    )
                ], style=CARD_STYLE)
            ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ], style={'maxWidth': '1200px', 'margin': '0 auto'})
    ])

def create_tab3_layout():
    """Create layout for Review Analysis tab"""
    return html.Div([
        html.H1('Phân tích đánh giá', style={
            'textAlign': 'center',
            'color': '#1976D2',
            'marginBottom': '30px',
            'marginTop': '20px'
        }),
        
        html.Div([
            # Left Column
            html.Div([
                # Review summary
                html.Div([
                    html.H3("Tổng quan đánh giá", style=HEADER_STYLE),
                    html.P([
                        html.Strong("Tổng số đánh giá: "),
                        f"{df['total_reviews'].sum():,}",
                        html.Br(),
                        html.Strong("Điểm đánh giá trung bình: "),
                        f"{df['rating'].mean():.2f}/5"
                    ])
                ], style=CARD_STYLE),
                
                # Reviews by platform
                html.Div([
                    html.H3("Đánh giá theo nền tảng", style=HEADER_STYLE),
                    dcc.Graph(
                        figure=px.bar(
                            df.groupby('platform')['rating'].mean().reset_index(),
                            x='platform',
                            y='rating',
                            title="Điểm đánh giá trung bình theo nền tảng"
                        ),
                        config={'displayModeBar': False}
                    )
                ], style=CARD_STYLE)
            ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            
            # Right Column
            html.Div([
                # Rating vs Price
                html.Div([
                    html.H3("Mối quan hệ giữa giá và đánh giá", style=HEADER_STYLE),
                    dcc.Graph(
                        figure=px.scatter(
                            df,
                            x='salePrice',
                            y='rating',
                            color='platform',
                            title="Tương quan giữa giá và đánh giá"
                        ),
                        config={'displayModeBar': False}
                    )
                ], style=CARD_STYLE),
                
                # Reviews distribution
                html.Div([
                    html.H3("Phân bố số lượng đánh giá", style=HEADER_STYLE),
                    dcc.Graph(
                        figure=px.histogram(
                            df,
                            x='total_reviews',
                            nbins=20,
                            title="Phân bố số lượng đánh giá"
                        ),
                        config={'displayModeBar': False}
                    )
                ], style=CARD_STYLE)
            ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ], style={'maxWidth': '1200px', 'margin': '0 auto'})
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