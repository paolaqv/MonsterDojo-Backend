from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.router import api_router

from app.core.config import get_settings

from app.shared.exceptions import AppException
from app.shared.responses import error_response


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.app_debug,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
)


# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=settings.trusted_hosts_list,
# )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(
    request:Request,
    call_next
):

    response=await call_next(
        request
    )

    if settings.security_headers_enabled:

        response.headers[
            "X-Content-Type-Options"
        ]="nosniff"

        response.headers[
            "X-Frame-Options"
        ]="DENY"

        response.headers[
            "Referrer-Policy"
        ]="strict-origin-when-cross-origin"

        response.headers[
            "Permissions-Policy"
        ]="camera=(), microphone=(), geolocation=()"

        response.headers[
            "Cache-Control"
        ]="no-store"


        if not settings.app_debug:

            response.headers[
              "Content-Security-Policy"
            ]="default-src 'self'"

    return response


# ----------------------------------
# A10 MANEJO CENTRALIZADO DE ERRORES
# ----------------------------------

@app.exception_handler(AppException)
async def app_exception_handler(
    request:Request,
    exc:AppException
):

    return JSONResponse(
        status_code=exc.status_code,

        content=error_response(
            exc.code,
            exc.message
        )
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request:Request,
    exc:Exception
):

    # nunca devolver errores internos reales

    return JSONResponse(
        status_code=500,

        content=error_response(
            "INTERNAL_ERROR",
            "Error inesperado del sistema"
        )
    )


@app.get("/",tags=["Root"])
def root():

    return {
        "message":f"Welcome to {settings.app_name}",
        "environment":settings.app_env
    }


app.include_router(
    api_router,
    prefix=settings.api_v1_prefix
)


if settings.app_debug:

    print("RUTAS CARGADAS:")

    for route in app.routes:

        methods=getattr(
            route,
            "methods",
            []
        )

        print(
            route.path,
            route.name,
            methods
        )