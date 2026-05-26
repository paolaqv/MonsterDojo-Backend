from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.logs.application.service import registrar_aplicacion
from app.modules.auth.permissions import require_permissions
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
    soft_delete_product,
    update_product,
)
from app.modules.users.model import Usuario

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/categories", response_model=list[ProductCategoryRead])
def read_product_categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_productos")),
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
    current_user: Usuario = Depends(require_permissions("gestionar_productos")),
):
    category = create_product_category(db, payload)

    registrar_aplicacion(
        db,
        modulo="productos",
        evento="CATEGORIA_PRODUCTO_CREADA",
        descripcion=f"Usuario {current_user.id_usuario} creo categoria de producto '{category.nombre}'.",
        severidad="INFO",
        estado="OK",
        usuario_id=current_user.id_usuario,
        entidad_afectada="categoria_producto",
        entidad_id=category.id_catProducto,
    )

    return category


@router.get("/", response_model=list[ProductRead])
def read_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_productos")),
):
    return get_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductRead)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_productos")),
):
    product = get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado.",
        )

    return product


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_new_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permissions("gestionar_productos")),
):
    try:
        product = create_product(db, payload)

        registrar_aplicacion(
            db,
            modulo="productos",
            evento="PRODUCTO_CREADO",
            descripcion=f"Usuario {current_user.id_usuario} creo producto '{product.nombre}' (precio {product.precio}, max {product.max_personas} personas).",
            severidad="INFO",
            estado="OK",
            usuario_id=current_user.id_usuario,
            entidad_afectada="producto",
            entidad_id=product.id_producto,
        )

        return product
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
    current_user: Usuario = Depends(require_permissions("gestionar_productos")),
):
    try:
        product = update_product(db, product_id, payload)

        registrar_aplicacion(
            db,
            modulo="productos",
            evento="PRODUCTO_ACTUALIZADO",
            descripcion=f"Usuario {current_user.id_usuario} actualizo producto '{product.nombre}' (id {product_id}).",
            severidad="INFO",
            estado="OK",
            usuario_id=current_user.id_usuario,
            entidad_afectada="producto",
            entidad_id=product_id,
        )

        return product
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


@router.delete("/{product_id}", response_model=ProductRead)
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permissions("gestionar_productos")),
):
    try:
        product = soft_delete_product(db, product_id)

        registrar_aplicacion(
            db,
            modulo="productos",
            evento="PRODUCTO_ARCHIVADO",
            descripcion=f"Usuario {current_user.id_usuario} archivo (desactivo) producto '{product.nombre}' (id {product_id}).",
            severidad="WARN",
            estado="OK",
            usuario_id=current_user.id_usuario,
            entidad_afectada="producto",
            entidad_id=product_id,
        )

        return product
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
