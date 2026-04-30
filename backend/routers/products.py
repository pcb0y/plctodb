from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models import Product, ProcessRecord
from schemas import ProductCreate, ProductResponse, ProductUpdate
from dependencies import verify_token
from utils.logger import log_product_create, log_product_update, log_product_delete

router = APIRouter(prefix="/api")

@router.get("/products")
def get_products(page: int = 1, limit: int = 10, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    total = db.query(Product).count()
    offset = (page - 1) * limit
    products = db.query(Product).offset(offset).limit(limit).all()
    return {"items": products, "total": total, "page": page, "limit": limit}

@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    user_id = token_payload.get("user_id")
    
    existing = db.query(Product).filter(Product.product_code == product.product_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="产品编号已存在")
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    log_product_create(db, user_id, db_product.id, db_product.product_name)
    return db_product

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    user_id = token_payload.get("user_id")
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)
    
    db_product.version = db_product.version + 1
    db.commit()
    db.refresh(db_product)
    
    log_product_update(db, user_id, db_product.id, db_product.product_name)
    return db_product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    user_id = token_payload.get("user_id")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    has_records = db.query(ProcessRecord).filter(ProcessRecord.product_id == product_id).first() is not None
    
    if has_records:
        raise HTTPException(status_code=400, detail="该产品有相关的生产记录，不允许删除")
    
    product_name = product.product_name
    db.delete(product)
    db.commit()
    
    log_product_delete(db, user_id, product_id, product_name)
    return {"message": "产品删除成功"}