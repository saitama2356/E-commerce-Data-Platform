import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import sqlite3

# Create Dash app
app = dash.Dash(__name__)

# Sample data for the chart and table
df = pd.DataFrame({
    'Name': ['A', 'B', 'C'],
    'Value': [10, 20, 30]
})

# Create bar chart with better styling
figure = go.Figure(data=[
    go.Bar(
        x=df['Name'], 
        y=df['Value'],
        marker_color='#4CAF50'  # Material Design green
    )
])
figure.update_layout(
    title="Simple Bar Chart",
    paper_bgcolor='white',
    plot_bgcolor='white',
    margin=dict(t=40, l=20, r=20, b=20)
)

# Common styles
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '8px',
    'padding': '20px',
    'margin': '10px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
}

HEADER_STYLE = {
    'color': '#2196F3',  # Material Design blue
    'marginBottom': '15px',
    'fontSize': '18px'
}

# Overview Page layout
overview = html.Div([
    html.H1('Tổng quan', style={
        'textAlign': 'center',
        'color': '#1976D2',
        'marginBottom': '30px',
        'marginTop': '20px'
    }),
    
    html.Div([
        # Left Column (Text and Table)
        html.Div([
            # Text section
            html.Div([
                html.H3("Tóm tắt", style=HEADER_STYLE),
                html.P(f"""\
                        Báo cáo lúc {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}. \
                        Nền tảng dữ liệu thương mại điện tử cung cấp cái nhìn toàn diện về thị trường sản phẩm điện tử trên Shopee, Tiki, và Lazada., Báo cáo tập trung vào việc phân tích hiệu suất của các sản phẩm thuộc ngành hàng điện tử, bao gồm doanh thu, số lượng bán ra, đánh giá từ khách hàng, và mức độ cạnh tranh giữa các thương hiệu. Các sản phẩm điện tử chủ đạo được khảo sát bao gồm điện thoại di động, máy tính bảng, tai nghe, và phụ kiện công nghệ \
                        Nhờ khả năng tổng hợp và phân tích dữ liệu từ nhiều nguồn, nền tảng này mang đến góc nhìn đa chiều về sự biến động của thị trường, bao gồm sự tăng trưởng của các thương hiệu lớn, xu hướng tiêu dùng, và các yếu tố ảnh hưởng đến quyết định mua sắm của khách hàng. Tuy nhiên, rủi ro chính trong việc phân tích dữ liệu này là sự biến động mạnh của thị trường do yếu tố cạnh tranh, khuyến mãi, và nhu cầu người tiêu dùng thay đổi liên tục. \
Báo cáo này không chỉ giúp các nhà kinh doanh và nhà đầu tư hiểu rõ hơn về thị trường mà còn hỗ trợ xây dựng chiến lược kinh doanh hiệu quả, đồng thời cung cấp cơ sở dữ liệu giá trị để đánh giá tiềm năng tăng trưởng dài hạn của ngành hàng điện tử.""", 
                       style={
                        'lineHeight': '1.5',
                        'color': '#666'
                    })
            ], style=CARD_STYLE),
            
            # Table section
            html.Div([
                html.H3("Table Section", style=HEADER_STYLE),
                html.Table([
                    # Header
                    html.Thead(html.Tr([
                        html.Th(col, style={
                            'backgroundColor': '#f5f5f5',
                            'padding': '12px',
                            'textAlign': 'left'
                        }) for col in df.columns
                    ])),
                    # Body
                    html.Tbody([
                        html.Tr([
                            html.Td(df.iloc[i][col], style={
                                'padding': '12px',
                                'borderTop': '1px solid #eee'
                            }) for col in df.columns
                        ]) for i in range(len(df))
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse'})
            ], style=CARD_STYLE)
        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        # Right Column (Chart and Image)
        html.Div([
            # Chart section
            html.Div([
                html.H3("Chart Section", style=HEADER_STYLE),
                dcc.Graph(figure=figure, config={'displayModeBar': False})
            ], style=CARD_STYLE),
            
            # Image section (placeholder image)
            html.Div([
                html.H3("Image Section", style=HEADER_STYLE),
                html.Img(
                    src='https://i.ytimg.com/vi/UxIjodEnYBc/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLAl-yNcvD7i-Pfij6xv0qez-_xymQ',  # Placeholder image URL
                    style={'width': '100%', 'borderRadius': '4px'}
                )
            ], style=CARD_STYLE)
        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'maxWidth': '1200px', 'margin': '0 auto'})
])

# Product Detail Page layout
product_detail = html.Div([
    html.H1("Product Detail Page"),
    html.P("Detailed information about the product."),
    html.Div([
        html.H3("Product Specifications"),
        html.P("Here we will describe the product specifications.")
    ]),
    html.Div([
        html.A("Go to Overview", href="/overview")
    ])
])

# Define layout for navigation (this could be a menu or a sidebar)
def get_menu():
    return html.Div([
        dcc.Link('Overview', href='/overview', className="tab"),
        dcc.Link('Product Detail', href='/product-detail', className="tab")
    ], className="row")

# Main app layout with dynamic page-content
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    get_menu(),  # Navigation Menu
    html.Div(id='page-content')  # This will hold the content based on the current URL
])

# Callback to switch between pages based on URL
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/' or pathname == '/overview':
        return overview
    elif pathname == '/product-detail':
        return product_detail
    else:
        return html.Div("404 Page Not Found")

if __name__ == '__main__':
    app.run_server(debug=True, host='localhost', port=8050)
