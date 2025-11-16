import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="YOTS TECH-SHOP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "YOTS TECH-SHOP backend running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# ---- Products ----
@app.post("/api/products", response_model=dict)
def create_product(product: Product):
    try:
        inserted_id = create_document("product", product)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products", response_model=List[dict])
def list_products(category: Optional[str] = None):
    try:
        flt = {"category": category} if category else {}
        docs = get_documents("product", flt)
        for d in docs:
            d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products/{product_id}", response_model=dict)
def get_product(product_id: str):
    try:
        doc = db["product"].find_one({"_id": ObjectId(product_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Product not found")
        doc["id"] = str(doc.pop("_id"))
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/products/seed", response_model=dict)
def seed_products():
    """Seed a minimal catalog of iPhones and accessories if database is empty."""
    try:
        count = db["product"].count_documents({}) if db else 0
        if count > 0:
            return {"status": "ok", "message": "Products already exist", "count": count}

        items = [
            {
                "name": "iPhone 15 Pro",
                "description": "Titanium. A17 Pro chip. Pro camera system.",
                "price": 999.0,
                "category": "new",
                "is_new": True,
                "condition": None,
                "grade": None,
                "storage": "128GB",
                "color": "Natural Titanium",
                "images": [
                    "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/iphone-15-pro-finish-select-202309-6-7inch-naturaltitanium?wid=512&hei=512&fmt=jpeg&qlt=90&.v=1692893201418"
                ],
                "stock": 10,
            },
            {
                "name": "iPhone 15",
                "description": "Dynamic Island. 48MP Main camera.",
                "price": 799.0,
                "category": "new",
                "is_new": True,
                "storage": "128GB",
                "color": "Blue",
                "images": [
                    "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/iphone-15-finish-select-202309-6-1inch-blue?wid=512&hei=512&fmt=jpeg&qlt=90&.v=1693087732363"
                ],
                "stock": 12,
            },
            {
                "name": "iPhone 14 Pro (Pre‑Owned)",
                "description": "Excellent condition. Fully tested. 85% battery health.",
                "price": 699.0,
                "category": "preowned",
                "is_new": False,
                "condition": "Excellent",
                "grade": "A",
                "storage": "256GB",
                "color": "Space Black",
                "images": [
                    "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/iphone-14-pro-finish-select-202209-6-7inch-spaceblack?wid=512&hei=512&fmt=jpeg&qlt=90&.v=1660754106034"
                ],
                "stock": 5,
            },
            {
                "name": "MagSafe Charger",
                "description": "Snap on wireless charging.",
                "price": 39.0,
                "category": "accessories",
                "is_new": True,
                "images": [
                    "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/MHXH3?wid=572&hei=572&fmt=jpeg&qlt=95&.v=1694014870996"
                ],
                "stock": 30,
            },
        ]
        result = db["product"].insert_many(items)
        return {"status": "ok", "inserted": len(result.inserted_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Orders (Checkout) ----
@app.post("/api/orders", response_model=dict)
def create_order(order: Order):
    try:
        inserted_id = create_document("order", order)
        return {"id": inserted_id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
