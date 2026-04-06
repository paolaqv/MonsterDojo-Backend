from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine


def test_connection() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("Conexion a la base de datos exitosa.")


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente.")


if __name__ == "__main__":
    test_connection()
    create_tables()