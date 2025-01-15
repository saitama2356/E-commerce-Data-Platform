from dagster import define_asset_job, ScheduleDefinition, Definitions, asset, AssetExecutionContext
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import os


@asset
def get_sales_data():
    """Load sales data from SQLite database"""
    con = sqlite3.connect('D:/FIA1471/e-com.sqlite')
    df = pd.read_sql_query("SELECT * FROM fact_sales;", con)
    con.close()
    df['scraped_timestamp'] = pd.to_datetime(df['scraped_timestamp'])
    return df

@asset(deps=[get_sales_data])
def create_plots():
    """Generate analysis plots"""
    df = get_sales_data()
    plot_files = {}
    
    # Platform distribution
    # Phân bố nền tảng
    plt.figure(figsize=(10, 7))
    platform_counts = df['platform'].value_counts()
    platform_counts.plot(kind='pie', autopct='%1.1f%%', 
                            colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'],
                            startangle=90, 
                            title="Phân Bố Sản Phẩm Theo Nền Tảng")
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig('platform_dist.png', dpi=300)
    plt.close()

    # Phân bố điểm đánh giá
    plt.figure(figsize=(10, 7))
    df['rating'].plot(kind='hist', bins=20, 
                        color='#66b3ff', 
                        edgecolor='black',
                        title="Phân Bố Điểm Đánh Giá Sản Phẩm")
    plt.xlabel('Điểm Đánh Giá')
    plt.ylabel('Số Lượng Sản Phẩm')
    plt.tight_layout()
    plt.savefig('rating_dist.png', dpi=300)
    plt.close()
    plot_files['platform_dist'] = 'platform_dist.png'

    # Phân phối giá
    plt.figure(figsize=(10, 7))
    df['salePrice'].plot(kind='hist', bins=30, 
                            color='#99ff99', 
                            edgecolor='black',
                            title="Phân Phối Giá Sản Phẩm")
    plt.xlabel('Giá Sản Phẩm (VNĐ)')
    plt.ylabel('Số Lượng Sản Phẩm')
    plt.tight_layout()
    plt.savefig('price_dist.png', dpi=300)
    plt.close()
    plot_files['rating_dist'] = 'rating_dist.png'

    # Price distribution
    plt.figure(figsize=(8, 6))
    df['salePrice'].plot(kind='hist', bins=30, title="Phân phối giá sản phẩm")
    plt.xlabel('Price')
    plt.savefig('price_dist.png')
    plt.close()
    plot_files['price_dist'] = 'price_dist.png'

    # Xu hướng giá theo thời gian
    plt.figure(figsize=(12, 8))
    trends = df.groupby(['platform', 'scraped_timestamp'])['salePrice'].mean().unstack(0)
    trends.plot(marker='o', linewidth=2, 
                title="Xu Hướng Giá Trung Bình Theo Nền Tảng")
    plt.ylabel('Giá Trung Bình (VNĐ)')
    plt.xlabel('Thời Gian')
    plt.legend(title='Nền Tảng', loc='best')
    plt.tight_layout()
    plt.savefig('price_trends.png', dpi=300)
    plt.close()
    plot_files['price_trends'] = 'price_trends.png'
    
    return plot_files

@asset(deps=[get_sales_data])
def create_report():
    """Generate HTML report content"""
    df = get_sales_data()
    
    # Tính toán các chỉ số quan trọng
    total_products = len(df)
    platform_breakdown = df['platform'].value_counts(normalize=True) * 100
    avg_rating = df['rating'].mean()
    median_rating = df['rating'].median()
    avg_price = df['salePrice'].mean()
    median_price = df['salePrice'].median()
    price_range = df['salePrice'].max() - df['salePrice'].min()

    # Phân tích chi tiết
    top_platforms = platform_breakdown.head(3)
    rating_distribution = df['rating'].value_counts(normalize=True).sort_index() * 100

    html_content = f"""
    <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                     max-width: 800px; 
                     margin: 0 auto; 
                     padding: 20px; 
                     line-height: 1.6; 
                     color: #333;">
            <div style="background-color: #f0f4f8; 
                        padding: 20px; 
                        border-radius: 10px; 
                        text-align: center; 
                        margin-bottom: 20px;">
                <h1 style="color: #1a5f7a; 
                           border-bottom: 3px solid #1a5f7a; 
                           padding-bottom: 10px;">
                    BÁO CÁO PHÂN TÍCH THƯƠNG MẠI ĐIỆN TỬ
                </h1>
                <p style="font-style: italic; color: #666;">
                    Báo cáo chi tiết về xu hướng và hiệu suất sản phẩm
                </p>
            </div>

            <div style="background-color: #e9f5f9; 
                        padding: 15px; 
                        border-radius: 8px; 
                        margin-bottom: 20px;">
                <h2 style="color: #2c3e50;">Tổng Quan Báo Cáo</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td><strong>⏰ Thời Gian Báo Cáo:</strong></td>
                        <td>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</td>
                    </tr>
                    <tr>
                        <td><strong>🔢 Tổng Sản Phẩm:</strong></td>
                        <td>{total_products:,}</td>
                    </tr>
                    <tr>
                        <td><strong>⭐ Điểm Đánh Giá Trung Bình:</strong></td>
                        <td>{avg_rating:.2f}/5.00 (Trung vị: {median_rating:.2f})</td>
                    </tr>
                    <tr>
                        <td><strong>📊 Giá Sản Phẩm Trung Bình:</strong></td>
                        <td>{avg_price:,.0f} VNĐ (Trung vị: {median_price:,.0f} VNĐ)</td>
                    </tr>
                </table>
            </div>

            <div style="margin-bottom: 20px;">
                <h2 style="color: #2c3e50;">Phân Tích Chi Tiết</h2>
                
                <h3>Phân Bố Nền Tảng</h3>
                <p>Top 3 nền tảng hàng đầu:</p>
                {''.join([f'<p>• <strong>{platform}</strong>: {percentage:.2f}%</p>' for platform, percentage in top_platforms.items()])}
                <img src="cid:platform_dist" alt="Phân Bố Nền Tảng" style="max-width: 100%; height: auto;">
                
                <h3>Phân Bố Điểm Đánh Giá</h3>
                <p>Chi tiết điểm đánh giá của sản phẩm:</p>
                {''.join([f'<p>• <strong>{rating} Sao</strong>: {percentage:.2f}%</p>' for rating, percentage in rating_distribution.items()])}
                <img src="cid:rating_dist" alt="Phân Bố Điểm Đánh Giá" style="max-width: 100%; height: auto;">
                
                <h3>Phân Phối Giá</h3>
                <p>Phân tích chi tiết về giá sản phẩm:</p>
                <p>• Khoảng giá: {price_range:,.0f} VNĐ</p>
                <img src="cid:price_dist" alt="Phân Phối Giá" style="max-width: 100%; height: auto;">
                
                <h3>Xu Hướng Giá Theo Thời Gian</h3>
                <p>Theo dõi sự biến động giá trung bình trên các nền tảng:</p>
                <img src="cid:price_trends" alt="Xu Hướng Giá" style="max-width: 100%; height: auto;">
            </div>

            <div style="background-color: #f0f4f8; 
                        padding: 15px; 
                        border-radius: 8px; 
                        text-align: center;">
                <p style="color: #666; font-style: italic;">
                    Báo cáo được tạo tự động - Để biết thêm chi tiết, vui lòng liên hệ bộ phận phân tích
                </p>
            </div>
        </body>
    </html>
    """
    return html_content

@asset(deps=[create_report, create_plots])
def send_report_email(context: AssetExecutionContext):
    """Send email with report and plots"""
    sender = "aduc21012@gmail.com"
    # Note: Be cautious about hardcoding passwords. Consider using environment variables.
    app_password = "bpsd paie opyf siwr"
    recipient = "aduc21012@gmail.com"

    # Retrieve the report and plots from the previous assets
    report_content = create_report()
    plot_files = create_plots()

    msg = MIMEMultipart('related')
    msg['Subject'] = f'Báo cáo phân tích bán hàng - {datetime.now().strftime("%Y-%m-%d")}'
    msg['From'] = sender
    msg['To'] = recipient

    msg.attach(MIMEText(report_content, 'html'))

    # Attach images
    for img_id, img_path in plot_files.items():
        with open(img_path, 'rb') as f:
            img = MIMEBase('application', 'octet-stream')
            img.set_payload(f.read())
            encoders.encode_base64(img)
            img.add_header('Content-Disposition', f'inline; filename={img_path}')
            img.add_header('Content-ID', f'<{img_id}>')
            msg.attach(img)

    # Send email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, app_password)
            server.sendmail(sender, recipient, msg.as_string())
        context.log.info("Đã gửi email thành công!")
    except Exception as e:
        context.log.error(f"Lỗi khi gửi email: {str(e)}")
        raise


reporting_job = define_asset_job(name="reporting_job", selection=["get_sales_data", "create_plots", "create_report", "send_report_email"])

reporting_schedule = ScheduleDefinition(
    job=reporting_job,
    cron_schedule="* * * * *",  # Runs every minute
    execution_timezone="Asia/Ho_Chi_Minh",
    name="sales_report_schedule"
)