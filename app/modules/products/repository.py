from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.products.model import CategoriaProducto, Producto
from app.modules.products.schemas import (
    ProductCategoryCreate,
    ProductCreate,
    ProductUpdate,
)


def get_product_category_by_id(db: Session, category_id: int) -> CategoriaProducto | None:
    stmt = select(CategoriaProducto).where(
        CategoriaProducto.id_catProducto == category_id
    )
    return db.scalar(stmt)


def get_product_categories(db: Session, skip: int = 0, limit: int = 100) -> list[CategoriaProducto]:
    stmt = select(CategoriaProducto).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_product_category(db: Session, category_data: ProductCategoryCreate) -> CategoriaProducto:
    category = CategoriaProducto(nombre=category_data.nombre)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_product_by_id(db: Session, product_id: int) -> Producto | None:
    stmt = select(Producto).where(Producto.id_producto == product_id)
    return db.scalar(stmt)


def get_products(db: Session, skip: int = 0, limit: int = 100) -> list[Producto]:
    stmt = select(Producto).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_product(db: Session, product_data: ProductCreate) -> Producto:
    product = Producto(
        nombre=product_data.nombre,
        descripcion=product_data.descripcion,
        precio=product_data.precio,
        max_personas=product_data.max_personas,
        imagen=product_data.imagen,
        activo=product_data.activo,
        categoria_producto_id_catProducto=product_data.categoria_producto_id_catProducto,
    )

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Producto, product_data: ProductUpdate) -> Producto:
    update_data = product_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product