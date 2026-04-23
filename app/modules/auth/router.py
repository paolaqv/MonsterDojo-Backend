from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.logs.activity.service import registrar_evento

from app.modules.auth.schemas import (
    ChangeSecurityQuestionRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    SecurityQuestionRequest,
    SecurityQuestionResponse,
    TokenResponse,
    VerifySecurityAnswerRequest,
)

from app.modules.auth.service import (
    change_security_question,
    get_security_question,
    login_user,
    reset_password_with_security_answer,
    verify_security_answer,
)

from app.modules.users.schemas import UserRead
from app.modules.users.service import create_user


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    try:

        resultado = login_user(
            db,
            payload.correo,
            payload.password
        )

        # AUDITORIA LOGIN EXITOSO
        registrar_evento(
            db=db,
            evento="LOGIN_EXITOSO",
            modulo="auth",
            accion="LOGIN",
            estado="OK",
            severidad="MEDIA",
            descripcion="Inicio de sesión correcto"
        )

        return resultado

    except ValueError as e:

        # AUDITORIA LOGIN FALLIDO
        registrar_evento(
            db=db,
            evento="LOGIN_FALLIDO",
            modulo="auth",
            accion="LOGIN",
            estado="FALLIDO",
            severidad="ALTA",
            descripcion="Credenciales inválidas"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db)
):
    try:

        user = create_user(
            db,
            payload
        )

        # AUDITORIA CREACION USUARIO
        registrar_evento(
            db=db,
            evento="USUARIO_CREADO",
            modulo="auth",
            accion="CREATE",
            estado="OK",
            severidad="MEDIA",
            descripcion="Nuevo usuario registrado",
            entidad_afectada="usuario"
        )

        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/security-question",
    response_model=SecurityQuestionResponse
)
def security_question(
    payload: SecurityQuestionRequest,
    db: Session = Depends(get_db)
):
    try:
        return get_security_question(
            db,
            payload.correo
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/verify-security-answer",
    response_model=MessageResponse
)
def verify_answer(
    payload: VerifySecurityAnswerRequest,
    db: Session = Depends(get_db)
):
    try:
        return verify_security_answer(
            db,
            payload.correo,
            payload.respuesta_seguridad
        )

    except ValueError as e:

        registrar_evento(
            db=db,
            evento="RESPUESTA_SEGURIDAD_INVALIDA",
            modulo="auth",
            accion="VERIFY",
            estado="FALLIDO",
            severidad="ALTA",
            descripcion="Respuesta de seguridad incorrecta"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/reset-password",
    response_model=MessageResponse
)
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    try:

        result = reset_password_with_security_answer(
            db,
            payload.correo,
            payload.respuesta_seguridad,
            payload.new_password,
        )

        # AUDITORIA PASSWORD RESET
        registrar_evento(
            db=db,
            evento="PASSWORD_RESET",
            modulo="auth",
            accion="UPDATE",
            estado="OK",
            severidad="ALTA",
            descripcion="Restablecimiento de contraseña"
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/security-question",
    response_model=MessageResponse
)
def update_security_question(
    payload: ChangeSecurityQuestionRequest,
    db: Session = Depends(get_db),
):
    try:

        result = change_security_question(
            db,
            payload.correo,
            payload.password,
            payload.nueva_pregunta_seguridad,
            payload.nueva_respuesta_seguridad,
        )

        # AUDITORIA CAMBIO PREGUNTA SEGURIDAD
        registrar_evento(
            db=db,
            evento="PREGUNTA_SEGURIDAD_CAMBIADA",
            modulo="auth",
            accion="UPDATE",
            estado="OK",
            severidad="MEDIA",
            descripcion="Cambio de pregunta y respuesta de seguridad"
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )