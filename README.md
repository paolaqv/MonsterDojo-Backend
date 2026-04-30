# MonsterDojo Backend

Backend de **Monster Dojo** desarrollado con **FastAPI**, **SQLAlchemy**, **PostgreSQL** y **Alembic**.

## Requisitos previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- Python 3.11 o superior
- PostgreSQL
- Git

## Clonar el repositorio

~~~bash
git clone https://github.com/paolaqv/MonsterDojo-Backend.git
cd MonsterDojo-Backend
~~~

## Crear y activar entorno virtual

### En Windows PowerShell

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
~~~

### En Linux / macOS

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

## Instalar dependencias

~~~bash
pip install -r requirements.txt
~~~

## Configuración de variables de entorno

Crear un archivo `.env` en la raíz del proyecto con una configuración similar a esta:

~~~env
APP_NAME=Monster Dojo API
APP_VERSION=1.0.0
APP_ENV=development
APP_DEBUG=true
API_V1_PREFIX=/api/v1

DB_HOST=localhost
DB_PORT=5432
DB_NAME=monsterdojo
DB_USER=postgres
DB_PASSWORD=tu_password

SECRET_KEY=cambia_esta_clave_por_una_mas_segura
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256
~~~

## Crear la base de datos

Primero crea una base de datos en PostgreSQL.

Ejemplo:

~~~sql
CREATE DATABASE monsterdojo;
~~~

## Ejecutar migraciones

El proyecto usa **Alembic** para gestionar migraciones.

Para aplicar las migraciones existentes:

~~~bash
alembic upgrade head
~~~

## Levantar el servidor

### Modo normal

~~~bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
~~~

### Modo desarrollo con recarga automática

~~~bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
~~~

Si el puerto `8000` está ocupado, puedes usar otro, por ejemplo:

~~~bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
~~~

## Documentación de la API

Con el backend corriendo, puedes acceder a:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Si usas otro puerto, reemplaza `8000` por el que corresponda.

## Estructura general del proyecto

~~~text
MonsterDojo-Backend/
├── app/
├── tests/
├── alembic.ini
├── requirements.txt
└── README.md
~~~

## Dependencias principales

Entre las librerías principales del proyecto se encuentran:

- fastapi
- uvicorn[standard]
- sqlalchemy
- psycopg[binary]
- pydantic
- pydantic-settings
- python-dotenv
- alembic
- python-jose[cryptography]
- passlib[bcrypt]
- python-multipart
- email-validator

## Revision de dependencias

Las dependencias del backend quedan fijadas con versiones exactas en
`requirements.txt`. Antes de entregar cambios de seguridad se debe ejecutar:

~~~bash
python -m pip_audit -r requirements.txt
python -m pip check
~~~

La auditoria OWASP documentada para este trabajo queda en:

~~~text
OWASP_IMPLEMENTACION.txt
~~~

## Flujo recomendado para ejecutar el proyecto

1. Clonar el repositorio
2. Crear y activar entorno virtual
3. Instalar dependencias
4. Crear el archivo `.env`
5. Crear la base de datos en PostgreSQL
6. Ejecutar migraciones con Alembic
7. Levantar el servidor con Uvicorn
8. Verificar acceso en `/docs`

## Problemas comunes

### El backend no levanta

Verifica que el entorno virtual esté activado y que todas las dependencias estén instaladas.

### Error de conexión a base de datos

Revisa las variables del `.env` y confirma que PostgreSQL esté corriendo.

### No abre `/docs`

Asegúrate de que el servidor esté ejecutándose en el puerto correcto.

### El puerto 8000 ya está ocupado

Levanta el backend en otro puerto, por ejemplo `8001`.

## Nota importante

Si el frontend consume este backend, debe apuntar al mismo puerto donde se esté ejecutando la API.

## Autor

Paola Quispe
