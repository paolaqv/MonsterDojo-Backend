from pydantic import BaseModel, ConfigDict, Field


class ProductCategoryBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryRead(ProductCategoryBase):
    id_catProducto: int

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    descripcion: str = Field(..., min_length=1, max_length=500)
    precio: float = Field(..., gt=0)
    max_personas: int = Field(..., ge=1)
    imagen: str = Field(..., min_length=1, max_length=255)
    activo: bool = True
    categoria_producto_id_catProducto: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    descripcion: str | None = Field(default=None, min_length=1, max_length=500)
    precio: float | None = Field(default=None, gt=0)
    max_personas: int | None = Field(default=None, ge=1)
    imagen: str | None = Field(default=None, min_length=1, max_length=255)
    activo: bool | None = None
    categoria_producto_id_catProducto: int | None = None


class ProductRead(ProductBase):
    id_producto: int

    model_config = ConfigDict(from_attributes=True)