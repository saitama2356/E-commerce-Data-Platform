from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from math import ceil
from fastapi import Query

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import json
from typing import Dict, Any, List, Union
from config import URI

app = FastAPI(
    title="Multi-Platform Product API",
    description="API for retrieving product details from multiple e-commerce platforms",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8050"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(URI, server_api=ServerApi('1'))
db = client['datashop']

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def serialize_document(document: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """
    Serialize MongoDB document to JSON with platform-specific handling
    """
    if document is None:
        return None
    
    serialized = json.loads(json.dumps(document, cls=JSONEncoder))
    
    if platform == 'lazada':
        if 'responseBody' in serialized:
            response_body = serialized.pop('responseBody')
            serialized.update(response_body)
    elif platform == 'shopee':
        if 'responseBody' in serialized and 'data' in serialized['responseBody']:
            serialized.update(serialized['responseBody']['data'])
    
    return serialized

def get_lazada_pdp(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Lazada PDP data structure
    """
    if not product or 'responseBody' not in product:
        return None
    
    response_body = product['responseBody']
    result = {**product, **response_body}
    result['_id'] = str(result['_id'])
    del result['responseBody']
    return result

def get_tiki_pdp(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Tiki PDP data structure
    """
    if not product:
        return None
    
    product['_id'] = str(product['_id'])
    return product

def get_shopee_pdp(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Shopee PDP data structure
    """
    if not product or 'responseBody' not in product:
        return None
    
    response_body = product['responseBody']
    data = response_body.get('data', {}).get('item', {})
    del product['responseBody']
    product['_id'] = str(product['_id'])
    return {**product, **data}

def get_platform_product_id(platform: str, document: Dict[str, Any]) -> Union[str, int]:
    """
    Extract product ID based on platform-specific structure
    """
    if platform == 'lazada':
        return document.get('responseBody', {}).get('itemId')
    elif platform == 'shopee':
        return document.get('responseBody', {}).get('data', {}).get('item', {}).get('item_id')
    elif platform == 'tiki':
        return document.get('id')
    return None

@app.get("/products/all", response_model=Dict[str, List[Union[str, int]]])
async def get_all_products():
    """
    Retrieve product IDs from all platforms
    """
    try:
        result = {
            'lazada': list(db['lazada'].distinct('responseBody.itemId')),
            'shopee': list(db['shopee'].distinct('responseBody.data.item.item_id')),
            'tiki': list(db['tiki'].distinct('id'))
        }
        
        # Check if any platform has products
        if not any(result.values()):
            raise HTTPException(status_code=404, detail="No products found in any platform")
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/products/{platform}")
async def get_platform_products(platform: str):
    """
    Retrieve product IDs for a specific platform
    """
    if platform not in ['lazada', 'shopee', 'tiki']:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    try:
        if platform == 'lazada':
            products = list(db['lazada'].distinct('responseBody.itemId'))
        elif platform == 'shopee':
            products = list(db['shopee'].distinct('responseBody.data.item.item_id'))
        else:  # tiki
            products = list(db['tiki'].distinct('id'))
            
        if not products:
            raise HTTPException(
                status_code=404,
                detail=f"No products found for {platform}"
            )
            
        return {"platform": platform, "product_ids": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/product/{platform}/{item_id}")
async def get_product_details(platform: str, item_id: str):
    """
    Retrieve detailed product information with platform-specific PDP handling
    """
    if platform not in ['lazada', 'shopee', 'tiki']:
        raise HTTPException(status_code=400, detail="Invalid platform")
        
    try:
        query_id = int(item_id) if item_id.isdigit() else item_id
        
        # Platform-specific queries and PDP processing
        if platform == 'lazada':
            product = db['lazada'].find_one({"responseBody.itemId": query_id})
            if product:
                return get_lazada_pdp(product)
                
        elif platform == 'shopee':
            product = db['shopee'].find_one({'responseBody.data.item.item_id': query_id})
            if product:
                return get_shopee_pdp(product)
                
        else:  # tiki
            product = db['tiki'].find_one({'id': query_id})
            if product:
                return get_tiki_pdp(product)
        
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {item_id} not found on {platform}"
        )
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

def get_shopee_price_history(item_id: Union[str, int]):
    """
    Retrieve price history for Shopee products with corrected query structure
    """
    query_id = int(item_id) if isinstance(item_id, str) and item_id.isdigit() else item_id
    
    pipeline = [
        {
            "$match": {
                "responseBody.data.item.item_id": query_id
            }
        },
        {
            "$project": {
                "_id": 0,
                "itemId": "$responseBody.data.item.item_id",
                "title": "$responseBody.data.item.title",
                "salePrice": {
                    "$divide": ["$responseBody.data.item.price", 100000]
                },
                "scraped_timestamp": {
                    "$toDate": "$scraped_timestamp"
                }
            }
        },
        {
            "$project": {
                "itemId": 1,
                "title": 1,
                "salePrice": 1,
                "scraped_timestamp": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$scraped_timestamp"
                    }
                }
            }
        },
        {
            "$sort": {
                "scraped_timestamp": 1
            }
        },
        {
            "$group": {
                "_id": {
                    "itemId": "$itemId",
                    "scraped_timestamp": "$scraped_timestamp"
                },
                "title": {"$first": "$title"},
                "salePrice": {"$first": "$salePrice"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "itemId": "$_id.itemId",
                "scraped_timestamp": "$_id.scraped_timestamp",
                "title": 1,
                "salePrice": 1
            }
        }
    ]
    
    return list(db['shopee'].aggregate(pipeline))

def get_lazada_price_history(item_id: Union[str, int]):
    """
    Retrieve price history for Lazada products
    """
    query_id = int(item_id) if isinstance(item_id, str) and item_id.isdigit() else item_id
    
    pipeline = [
        {
            "$match": {
                "responseBody.itemId": query_id
            }
        },
        {
            "$unwind": "$responseBody.skus"
        },
        {
            "$project": {
                "_id": 0,
                "itemId": "$responseBody.itemId",
                "skuId": "$responseBody.skus.skuId",
                "salePrice": "$responseBody.skus.salePrice",
                "scraped_timestamp": {
                    "$toDate": "$scraped_timestamp"
                },
                "title": "$responseBody.title"
            }
        },
        {
            "$project": {
                "itemId": 1,
                "skuId": 1,
                "salePrice": 1,
                "scraped_timestamp": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$scraped_timestamp"
                    }
                },
                "title": 1
            }
        },
        {
            "$sort": {
                "scraped_timestamp": 1
            }
        },
        {
            "$group": {
                "_id": {
                    "itemId": "$itemId",
                    "scraped_timestamp": "$scraped_timestamp"
                },
                "title": {"$first": "$title"},
                "prices": {
                    "$push": {
                        "skuId": "$skuId",
                        "salePrice": "$salePrice"
                    }
                }
            }
        },
        {
            "$unwind": "$prices"
        },
        {
            "$group": {
                "_id": {
                    "itemId": "$_id.itemId",
                    "scraped_timestamp": "$_id.scraped_timestamp"
                },
                "title": {"$first": "$title"},
                "skuId": {"$first": "$prices.skuId"},
                "salePrice": {"$first": "$prices.salePrice"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "itemId": "$_id.itemId",
                "scraped_timestamp": "$_id.scraped_timestamp",
                "title": 1,
                "skuId": 1,
                "salePrice": 1
            }
        }
    ]
    
    return list(db['lazada'].aggregate(pipeline))

def get_tiki_price_history(item_id: Union[str, int]):
    """
    Retrieve price history for Tiki products
    """
    query_id = int(item_id) if isinstance(item_id, str) and item_id.isdigit() else item_id
    
    pipeline = [
        {
            "$match": {
                "id": query_id
            }
        },
        {
            "$unwind": "$stock_item"
        },
        {
            "$project": {
                "_id": 0,
                "itemId": "$id",
                "title": "$name",
                "salePrice": "$price",
                "stock_qty": "$stock_item.qty",
                "scraped_timestamp": {
                    "$toDate": "$scraped_timestamp"
                }
            }
        },
        {
            "$project": {
                "itemId": 1,
                "title": 1,
                "salePrice": 1,
                "stock_qty": 1,
                "scraped_timestamp": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$scraped_timestamp"
                    }
                }
            }
        },
        {
            "$sort": {
                "scraped_timestamp": 1
            }
        },
        {
            "$group": {
                "_id": {
                    "itemId": "$itemId",
                    "scraped_timestamp": "$scraped_timestamp"
                },
                "title": {"$first": "$title"},
                "salePrice": {"$first": "$salePrice"},
                "stock_qty": {"$first": "$stock_qty"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "itemId": "$_id.itemId",
                "scraped_timestamp": "$_id.scraped_timestamp",
                "title": 1,
                "salePrice": 1,
                "stock_qty": 1
            }
        }
    ]
    
    return list(db['tiki'].aggregate(pipeline))

@app.get("/price-history/{platform}/{item_id}")
async def get_price_history(platform: str, item_id: str):
    """
    Retrieve price history for a specific product from the specified platform
    """
    if platform not in ['lazada', 'shopee', 'tiki']:
        raise HTTPException(status_code=400, detail="Invalid platform or platform not supported")
        
    try:
        if platform == 'lazada':
            history = get_lazada_price_history(item_id)
        elif platform == 'shopee':
            history = get_shopee_price_history(item_id)
        else:  # tiki
            history = get_tiki_price_history(item_id)

            
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"No price history found for product {item_id} on {platform}"
            )
            
        # Process the results to include additional statistics
        result = {
            "product_info": {
                "itemId": history[0]["itemId"],
                "title": history[0]["title"],
                "platform": platform
            },
            "price_history": history,
            "statistics": {
                "lowest_price": min(entry["salePrice"] for entry in history),
                "highest_price": max(entry["salePrice"] for entry in history),
                "latest_price": history[-1]["salePrice"],
                "first_recorded_date": history[0]["scraped_timestamp"],
                "last_recorded_date": history[-1]["scraped_timestamp"],
                "total_records": len(history)
            }
        }
                # Add stock information for Tiki products
        if platform == 'tiki':
            result["statistics"]["current_stock"] = history[-1]["stock_qty"]
        
        return result
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Custom JSON encoder for MongoDB ObjectId
def serialize_mongo_document(doc):
    """
    Convert MongoDB document with ObjectId to a JSON-serializable dictionary
    """
    if doc is None:
        return None
    
    # Create a copy of the document to avoid modifying the original
    serialized_doc = doc.copy()
    
    # Convert ObjectId to string
    for key, value in serialized_doc.items():
        if isinstance(value, ObjectId):
            serialized_doc[key] = str(value)
        
        # If the value is a list or dict, recursively convert ObjectIds
        elif isinstance(value, list):
            serialized_doc[key] = [
                str(item) if isinstance(item, ObjectId) else item 
                for item in value
            ]
        elif isinstance(value, dict):
            serialized_doc[key] = {
                k: str(v) if isinstance(v, ObjectId) else v 
                for k, v in value.items()
            }
    
    return serialized_doc

def get_shopee_tiki_reviews(product_id: str):
    """
    Retrieve reviews for Shopee or Tiki products from the reviews collection
    """
    # First try with the original ID format
    result = db['review'].find_one({'id': str(product_id)})
    
    # If not found, try with zero-padded format (common for Tiki products)
    
    if not result:
        return None
        
    return result

def get_lazada_reviews(product_id: Union[str, int]):
    """
    Retrieve reviews for Lazada products using aggregation pipeline
    """
    query_id = int(product_id) if isinstance(product_id, str) and product_id.isdigit() else product_id
    
    pipeline = [
        {
            "$unwind": "$responseBody.reviews"
        },
        {
            "$group": {
                "_id": "$responseBody.itemId",
                "reviews": {
                    "$push": "$responseBody.reviews"
                },
                "total_reviews": {
                    "$sum": 1
                },
                "rating_summary": {
                    "$first": "$responseBody.ratingCountByScore"
                }
            }
        },
        {
            "$match": {
                "_id": query_id
            }
        },
        {
            "$sort": {
                "total_reviews": -1
            }
        }
    ]
    
    result = list(db['lazada'].aggregate(pipeline))
    return result[0] if result else None

@app.get("/product-reviews/{platform}/{product_id}")
async def get_product_reviews(platform: str, product_id: str):
    """
    Retrieve product reviews from specified platform
    
    Parameters:
    - platform: str - The e-commerce platform (lazada, shopee, or tiki)
    - product_id: str - The product ID to lookup
    """
    platform = platform.lower().strip()
    supported_platforms = {'lazada', 'shopee', 'tiki'}
    
    if platform not in supported_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Supported platforms are: {', '.join(supported_platforms)}"
        )
        
    try:
        if platform == 'lazada':
            review_data = get_lazada_reviews(product_id)
        else:  # shopee or tiki
            review_data = get_shopee_tiki_reviews(product_id)
            
        if not review_data:
            raise HTTPException(
                status_code=404,
                detail=f"No reviews found for product {product_id} on {platform}"
            )
        
        # Serialize the document to handle ObjectId
        serialized_review_data = serialize_mongo_document(review_data)
            
        result = {
            "product_id": product_id,
            "platform": platform,
            "review": serialized_review_data
        }
        
        return result
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid product ID format. Please provide a valid product ID."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
