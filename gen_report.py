from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import pandas as pd

# Step 1: Create a sample chart
def create_chart(output_path):
    data = {"Category": ["A", "B", "C", "D"], "Value": [120, 340, 200, 150]}
    df = pd.DataFrame(data)

    plt.figure(figsize=(6, 4))
    plt.bar(df["Category"], df["Value"], color="skyblue")
    plt.title("Category Performance")
    plt.xlabel("Category")
    plt.ylabel("Value")
    plt.savefig(output_path)
    plt.close()

# Step 2: Generate PDF Report
def generate_pdf(output_path, chart_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Page 1: Title Page
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 700, "Vanguard Report Template")
    c.setFont("Helvetica", 14)
    c.drawString(100, 650, "This is an example financial report.")
    c.drawString(100, 630, "Generated with Python.")
    c.showPage()

    # Page 2: Chart Page
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 750, "Category Performance Chart")

    # Add the chart image
    chart_image = ImageReader(chart_path)
    c.drawImage(chart_image, 100, 400, width=400, height=300)
    c.showPage()

    # Page 3: Data Table
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 750, "Category Data Table")

    data = {"Category": ["A", "B", "C", "D"], "Value": [120, 340, 200, 150]}
    df = pd.DataFrame(data)

    x = 100
    y = 700
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Category")
    c.drawString(x + 200, y, "Value")
    c.setFont("Helvetica", 12)

    for index, row in df.iterrows():
        y -= 20
        c.drawString(x, y, row["Category"])
        c.drawString(x + 200, y, str(row["Value"]))

    c.showPage()

    # Save PDF
    c.save()

# Main script
if __name__ == "__main__":
    chart_path = "chart.png"
    pdf_path = "vanguard_report.pdf"

    # Create the chart
    create_chart(chart_path)

    # Generate the PDF
    generate_pdf(pdf_path, chart_path)

    print(f"Report generated: {pdf_path}")
