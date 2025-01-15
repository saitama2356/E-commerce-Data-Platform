# from dagster import Definitions, define_asset_job, schedule
from .assets import *

# # Create a job that includes all the assets in a single run
# report_job = define_asset_job(
#     name="sales_report_job", 
#     selection=["get_sales_data", "create_plots", "create_report", "send_report_email"]
# )

# # Schedule to run every 5 minutes
# @schedule(
#     # cron_schedule="*/5 * * * *",  # Runs every 5 minutes
#     cron_schedule="*/1 * * * *",  # Runs every minute
#     # cron_schedule="20 8 * * *",  # Runs at 8:20 AM every day
#     job=report_job,
#     name="five_minute_sales_report_schedule"
# )
# def five_minute_sales_report_schedule():
#     return {}

# defs = Definitions(
#     assets=[get_sales_data, create_plots, create_report, send_report_email],
#     schedules=[five_minute_sales_report_schedule]
# )


# Register assets and schedules
defs = Definitions(
    assets=[get_sales_data, create_plots, create_report, send_report_email],
    schedules=[reporting_schedule],
)
