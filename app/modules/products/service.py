from sqlalchemy.orm import Session

from app.modules.products import repository
from app.modules.products.model import CategoriaProducto, Producto
from app.modules.products.schemas import (
    ProductCategoryCreate,
    ProductCreate,
    ProductUpdate,
)


def get_product_category_by_id(db: Session, category_id: int) -> CategoriaProducto | None:
    return repository.get_product_category_by_id(db, category_id)


def get_product_categories(db: Session, skip: int = 0, limit: int = 100) -> list[CategoriaProducto]:
    return repository.get_product_categories(db, skip=skip, limit=limit)


def create_product_category(db: Session, category_data: ProductCategoryCreate) -> CategoriaProducto:
    return repository.create_product_category(db, category_data)


def get_product_by_id(db: Session, product_id: int) -> Producto | None:
    return repository.get_product_by_id(db, product_id)


def get_products(db: Session, skip: int = 0, limit: int = 100) -> list[Producto]:
    return repository.get_products(db, skip=skip, limit=limit)


def create_product(db: Session, product_data: ProductCreate) -> Producto:
    category = repository.get_product_category_by_id(
        db, product_data.categoria_producto_id_catProducto
    )
    if not category:
        raise ValueError("La categoría del producto no existe.")

    return repository.create_product(db, product_data)


def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Producto:
    product = repository.get_product_by_id(db, product_id)
    if not product:
        raise ValueError("Producto no encontrado.")

    if product_data.categoria_producto_id_catProducto is not None:
        category = repository.get_product_category_by_id(
            db, product_data.categoria_producto_id_catProducto
        )
        if not category:
            raise ValueError("La categoría del producto no existe.")

    return repository.update_product(db, product, product_data)