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

# Styles
REPORT_CONTAINER = {
    'maxWidth': '1200px',
    'margin': '0 auto',
    'padding': '20px',
    'backgroundColor': '#f5f5f5'
}

SECTION_CONTAINER = {
    'backgroundColor': 'white',
    'borderRadius': '8px',
    'padding': '20px',
    'marginBottom': '20px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
}

HEADER_STYLE = {
    'color': '#2196F3',
    'marginBottom': '15px',
    'fontSize': '24px',
    'borderBottom': '2px solid #2196F3',
    'paddingBottom': '10px'
}

SUBHEADER_STYLE = {
    'color': '#1976D2',
    'marginBottom': '15px',
    'fontSize': '20px',
    'paddingBottom': '5px'
}

CHART_STYLE = {
    'marginTop': '20px',
    'marginBottom': '20px'
}

def create_overview_section():
    return html.Div([
        html.H2("1. Tổng quan", style=HEADER_STYLE),
        
        # Executive Summary
        html.Div([
            html.H3("1.1 Tóm tắt điều hành", style=SUBHEADER_STYLE),
            html.P([
                f"Báo cáo được tạo lúc {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}.",
                html.Br(),
                f"Phân tích dữ liệu từ {len(df['platform'].unique())} nền tảng thương mại điện tử: {', '.join(df['platform'].unique())}.",
                html.Br(),
                "Báo cáo tập trung vào việc phân tích hiệu suất của các sản phẩm điện tử, bao gồm:",
                html.Ul([
                    html.Li("Phân tích giá và biến động giá theo thời gian"),
                    html.Li("Đánh giá và phản hồi của khách hàng"),
                    html.Li("So sánh hiệu suất giữa các nền tảng")
                ])
            ])
        ], style=SECTION_CONTAINER),
        
        # Key Metrics
        html.Div([
            html.H3("1.2 Chỉ số chính", style=SUBHEADER_STYLE),
            html.Div([
                html.Div([
                    html.Div(className='metric-card', children=[
                        html.H4("Tổng số sản phẩm", style={'textAlign': 'center'}),
                        html.P(f"{len(df['itemId'].unique()):,}", 
                              style={'fontSize': '24px', 'textAlign': 'center', 'color': '#2196F3', 'fontWeight': 'bold'})
                    ], style={'flex': '1', 'padding': '15px', 'border': '1px solid #ddd', 'borderRadius': '8px', 'margin': '5px'}),
                    html.Div(className='metric-card', children=[
                        html.H4("Số nền tảng", style={'textAlign': 'center'}),
                        html.P(f"{len(df['platform'].unique())}", 
                              style={'fontSize': '24px', 'textAlign': 'center', 'color': '#2196F3', 'fontWeight': 'bold'})
                    ], style={'flex': '1', 'padding': '15px', 'border': '1px solid #ddd', 'borderRadius': '8px', 'margin': '5px'}),
                    html.Div(className='metric-card', children=[
                        html.H4("Đánh giá trung bình", style={'textAlign': 'center'}),
                        html.P(f"{df['rating'].mean():.2f}/5", 
                              style={'fontSize': '24px', 'textAlign': 'center', 'color': '#2196F3', 'fontWeight': 'bold'})
                    ], style={'flex': '1', 'padding': '15px', 'border': '1px solid #ddd', 'borderRadius': '8px', 'margin': '5px'}),
                    html.Div(className='metric-card', children=[
                        html.H4("Tổng lượt đánh giá", style={'textAlign': 'center'}),
                        html.P(f"{df['total_reviews'].sum():,}", 
                              style={'fontSize': '24px', 'textAlign': 'center', 'color': '#2196F3', 'fontWeight': 'bold'})
                    ], style={'flex': '1', 'padding': '15px', 'border': '1px solid #ddd', 'borderRadius': '8px', 'margin': '5px'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'})
            ])
        ], style=SECTION_CONTAINER),
        
        # Distribution Charts
        html.Div([
            html.H3("1.3 Phân bố dữ liệu", style=SUBHEADER_STYLE),
            html.Div([
                dcc.Graph(
                    figure=px.pie(
                        df, 
                        names='platform',
                        title="Phân bố sản phẩm theo nền tảng"
                    ).update_layout(height=400),
                    style=CHART_STYLE
                ),
                dcc.Graph(
                    figure=px.histogram(
                        df,
                        x='rating',
                        nbins=20,
                        title="Phân bố điểm đánh giá"
                    ).update_layout(height=400),
                    style=CHART_STYLE
                )
            ])
        ], style=SECTION_CONTAINER)
    ])

def create_price_analysis_section():
    return html.Div([
        html.H2("2. Phân tích giá", style=HEADER_STYLE),
        
        # Price Statistics
        html.Div([
            html.H3("2.1 Thống kê giá theo nền tảng", style=SUBHEADER_STYLE),
            html.Div(style={'overflowX': 'auto'}, children=[
                html.Table([
                    html.Thead(html.Tr([
                        html.Th(col, style={'padding': '12px', 'backgroundColor': '#f8f9fa', 'border': '1px solid #dee2e6'})
                        for col in ['Nền tảng', 'Số mẫu', 'Giá TB (VND)', 'Giá thấp nhất', 'Giá cao nhất', 'Độ lệch chuẩn']
                    ])),
                    html.Tbody([
                        html.Tr([
                            html.Td(platform, style={'padding': '12px', 'border': '1px solid #dee2e6'}),
                            html.Td(f"{len(df[df['platform'] == platform]):,}", style={'padding': '12px', 'border': '1px solid #dee2e6'}),
                            html.Td(f"{df[df['platform'] == platform]['salePrice'].mean():,.0f}", style={'padding': '12px', 'border': '1px solid #dee2e6'}),
                            html.Td(f"{df[df['platform'] == platform]['salePrice'].min():,.0f}", style={'padding': '12px', 'border': '1px solid #dee2e6'}),
                            html.Td(f"{df[df['platform'] == platform]['salePrice'].max():,.0f}", style={'padding': '12px', 'border': '1px solid #dee2e6'}),
                            html.Td(f"{df[df['platform'] == platform]['salePrice'].std():,.0f}", style={'padding': '12px', 'border': '1px solid #dee2e6'})
                        ]) for platform in df['platform'].unique()
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginTop': '10px'})
            ])
        ], style=SECTION_CONTAINER),
        
        # Price Distribution
        html.Div([
            html.H3("2.2 Phân phối giá", style=SUBHEADER_STYLE),
            dcc.Graph(
                figure=px.histogram(
                    df,
                    x='salePrice',
                    nbins=30,
                    title="Phân phối giá sản phẩm"
                ).update_layout(height=400),
                style=CHART_STYLE
            ),
            dcc.Graph(
                figure=px.box(
                    df,
                    x='platform',
                    y='salePrice',
                    title="Phân phối giá theo nền tảng"
                ).update_layout(height=400),
                style=CHART_STYLE
            )
        ], style=SECTION_CONTAINER),
        
        # Price Trends
        html.Div([
            html.H3("2.3 Xu hướng giá", style=SUBHEADER_STYLE),
            dcc.Graph(
                figure=px.line(
                    df.groupby(['platform', 'scraped_timestamp'])['salePrice'].mean().reset_index(),
                    x='scraped_timestamp',
                    y='salePrice',
                    color='platform',
                    title="Xu hướng giá theo thời gian"
                ).update_layout(height=400),
                style=CHART_STYLE
            )
        ], style=SECTION_CONTAINER)
    ])

def create_review_analysis_section():
    return html.Div([
        html.H2("3. Phân tích đánh giá", style=HEADER_STYLE),
        
        # Review Summary
        html.Div([
            html.H3("3.1 Tổng quan đánh giá", style=SUBHEADER_STYLE),
            html.Div([
                html.Div(className='metric-card', children=[
                    html.H4("Tổng số đánh giá", style={'textAlign': 'center'}),
                    html.P(f"{df['total_reviews'].sum():,}", 
                          style={'fontSize': '24px', 'textAlign': 'center', 'color': '#2196F3', 'fontWeight': 'bold'})
                ], style={'flex': '1', 'padding': '15px', 'border': '1px solid #ddd', 'borderRadius': '8px', 'margin': '5px'}),
                html.Div(className='metric-card', children=[
                    html.H4("Đánh giá trung bình", style={'textAlign': 'center'}),
                    html.P(f"{df['rating'].mean():.2f}/5", 
                          style={'fontSize': '24px', 'textAlign': 'center', 'color': '#2196F3', 'fontWeight': 'bold'})
                ], style={'flex': '1', 'padding': '15px', 'border': '1px solid #ddd', 'borderRadius': '8px', 'margin': '5px'})
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'})
        ], style=SECTION_CONTAINER),
        
        # Review Distribution
        html.Div([
            html.H3("3.2 Phân tích đánh giá chi tiết", style=SUBHEADER_STYLE),
            dcc.Graph(
                figure=px.bar(
                    df.groupby('platform')['rating'].mean().reset_index(),
                    x='platform',
                    y='rating',
                    title="Điểm đánh giá trung bình theo nền tảng"
                ).update_layout(height=400),
                style=CHART_STYLE
            ),
            dcc.Graph(
                figure=px.scatter(
                    df,
                    x='salePrice',
                    y='rating',
                    color='platform',
                    title="Tương quan giữa giá và đánh giá"
                ).update_layout(height=400),
                style=CHART_STYLE
            ),
            dcc.Graph(
                figure=px.box(
                    df,
                    x='platform',
                    y='total_reviews',
                    title="Phân phối số lượng đánh giá theo nền tảng"
                ).update_layout(height=400),
                style=CHART_STYLE
            )
        ], style=SECTION_CONTAINER)
    ])

# Create the app layout
app.layout = html.Div([
    html.H1('Báo cáo phân tích thương mại điện tử', style={
        'textAlign': 'center',
        'color': '#1976D2',
        'padding': '20px 0',
        'marginBottom': '20px',
        'borderBottom': '3px solid #1976D2'
    }),
    
    html.Div([
        create_overview_section(),
        create_price_analysis_section(),
        create_review_analysis_section()
    ], style=REPORT_CONTAINER)
])

if __name__ == '__main__':
    app.run_server(debug=True, host='localhost', port=8050)