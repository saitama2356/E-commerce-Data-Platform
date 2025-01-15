
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
from pathlib import Path

from config import *

uri = URI

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)


# # ----- Check collections in the Database -----
# print(client['datashop'].list_collection_names())
db = client['datashop']
collection = db['shopee']
# Loading or Opening the json file
# with open('./data/shopee/5873954476_2024-11-14.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)


data_dir = Path(r'D:\FIA1471\data\shopee')

for json_file in data_dir.glob('*.json'):
    if json_file.is_file():
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            collection.insert_one(data)
            print(f'Inserted data from {json_file.name} into MongoDB.')
    else:
        print(f'Tệp {json_file.name} không tồn tại hoặc không phải là tệp thông thường.')


#     # Insert data and get the result
# result = collection.insert_one(data)
    
#     # Print confirmation messages
# print("Document uploaded successfully!")
# print(f"Inserted document ID: {result.inserted_id}")


# print(collection.find({
#   "scraped_timestamp": {
#     "$gte": "2024-11-14 00:00:00",
#     "$lte": "2024-11-14 23:59:59"
#   }
# }))


# ###########################
# # SHOPEE
# ###########################

# data_dir = Path(r'D:\FIA1471\data\shopee')

# # Duyệt qua từng tệp JSON trong thư mục
# for json_file in data_dir.glob('*.json'):
#     if json_file.is_file():
#         try:
#             with open(json_file, 'r', encoding='utf-8') as f:
#                 # Đọc dữ liệu JSON
#                 json_data = json.load(f)

#                 # Lấy root data (trừ responseBody)
#                 root_data = {key: json_data[key] for key in json_data if key != "responseBody"}

#                 # Lấy responseBody data
#                 response_body = json_data.get("responseBody", {}).get("data", {})

#                 # Lấy các phần `item` và `shop_detailed`
#                 item_data = response_body.get("item", {})
#                 shop_detailed_data = response_body.get("shop_detailed", {})

#                 # Kết hợp tất cả dữ liệu
#                 final_data = {
#                     **root_data,
#                     "item": item_data,
#                     "shop_detailed": shop_detailed_data,
#                 }

#                 # Tải dữ liệu lên MongoDB
#                 collection.insert_one(final_data)
#                 print(f"Inserted data from {json_file.name} into MongoDB.")
#         except Exception as e:
#             print(f"Error processing file {json_file.name}: {e}")
#     else:
#         print(f"Tệp {json_file.name} không tồn tại hoặc không phải là tệp thông thường.")

# print("Hoàn tất tải dữ liệu.")