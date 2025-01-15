from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import json
from typing import Dict, Any
from config import URI

app = FastAPI(
    title="Product API",
    description="API for retrieving product details from MongoDB",
    version="0.1.0"
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

def serialize_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize MongoDB document to JSON with proper handling of nested documents
    """
    if document is None:
        return None
    
    # Convert to JSON-compatible format
    serialized = json.loads(json.dumps(document, cls=JSONEncoder))
    
    # If responseBody exists, merge it carefully
    if 'responseBody' in serialized:
        response_body = serialized.pop('responseBody')
        # Avoid overwriting existing fields
        for key, value in response_body.items():
            if key not in serialized:
                serialized[key] = value
    
    return serialized

@app.get("/products")
async def get_product_list():
    try:
        product_ids = list(db['lazada'].distinct('responseBody.itemId'))
        if not product_ids:
            raise HTTPException(status_code=404, detail="No products found")
        return {"product_ids": product_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/product/{item_id}")
async def get_product_details(item_id: str):
    try:
        # Convert item_id to integer if it's numeric
        query_id = int(item_id) if item_id.isdigit() else item_id
        
        product = db['lazada'].find_one({"responseBody.itemId": query_id})
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {item_id} not found"
            )
        
        # Use the improved serialize_document function
        serialized_result = serialize_document(product)
        return serialized_result

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)