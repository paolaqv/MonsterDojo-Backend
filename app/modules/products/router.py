from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.products.schemas import (
    ProductCategoryCreate,
    ProductCategoryRead,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from app.modules.products.service import (
    create_product,
    create_product_category,
    get_product_by_id,
    get_product_categories,
    get_products,
    update_product,
)


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/categories", response_model=list[ProductCategoryRead])
def read_product_categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_product_categories(db, skip=skip, limit=limit)


@router.post(
    "/categories",
    response_model=ProductCategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_product_category(
    payload: ProductCategoryCreate,
    db: Session = Depends(get_db),
):
    return create_product_category(db, payload)


@router.get("/", response_model=list[ProductRead])
def read_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductRead)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado.",
        )

    return product


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_new_product(payload: ProductCreate, db: Session = Depends(get_db)):
    try:
        return create_product(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{product_id}", response_model=ProductRead)
def update_existing_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_product(db, product_id, payload)
    except ValueError as e:
        detail = str(e)
        status_code = (
            status.HTTP_404_NOT_FOUND
            if detail == "Producto no encontrado."
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code,
            detail=detail,
        )