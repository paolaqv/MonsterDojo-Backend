from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db

from app.logs.activity.service import registrar_evento

from app.modules.auth.schemas import (
    ChangeSecurityQuestionRequest,
    LoginRequest,
    MessageResponse,
    PasswordChangeRequiredRequest,
    PasswordRecoveryRequest,
    PasswordRecoveryResetRequest,
    PasswordRecoveryVerifyRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SecurityQuestionRequest,
    SecurityQuestionResponse,
    TokenResponse,
    VerifySecurityAnswerRequest,
)

from app.modules.auth.service import (
    change_password_required,
    change_security_question,
    get_security_question,
    login_user,
    request_password_recovery,
    reset_password_with_code,
    reset_password_with_security_answer,
    verify_recovery_code,
    verify_security_answer,
)

from app.modules.users.schemas import UserRead
from app.modules.users.service import create_user

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()


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


# =========================================================
# LEGACY: recuperación débil por pregunta/respuesta
# Se mantiene temporalmente para no romper el frontend actual.
# Luego, cuando el nuevo flujo esté listo, puedes retirarlo.
# =========================================================

@router.post("/security-question", response_model=SecurityQuestionResponse)
def security_question(payload: SecurityQuestionRequest, db: Session = Depends(get_db)):
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


# =========================================================
# NUEVO FLUJO: cambio obligatorio por política
# =========================================================

@router.post("/change-password-required", response_model=MessageResponse)
def change_password_required_endpoint(
    payload: PasswordChangeRequiredRequest,
    db: Session = Depends(get_db),
):
    try:
        return change_password_required(
            db,
            payload.correo,
            payload.current_password,
            payload.new_password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# =========================================================
# NUEVO FLUJO: recuperación segura por código temporal
# =========================================================

@router.post("/password-recovery/request", response_model=dict)
def password_recovery_request(
    payload: PasswordRecoveryRequest,
    db: Session = Depends(get_db),
):
    try:
        return request_password_recovery(
            db,
            payload.correo,
            settings.app_debug,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/password-recovery/verify", response_model=MessageResponse)
def password_recovery_verify(
    payload: PasswordRecoveryVerifyRequest,
    db: Session = Depends(get_db),
):
    try:
        return verify_recovery_code(
            db,
            payload.correo,
            payload.codigo,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/password-recovery/reset", response_model=MessageResponse)
def password_recovery_reset(
    payload: PasswordRecoveryResetRequest,
    db: Session = Depends(get_db),
):
    try:
        return reset_password_with_code(
            db,
            payload.correo,
            payload.codigo,
            payload.new_password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )