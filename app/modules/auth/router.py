from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.modules.security.passwords.service import get_active_password_policy
from app.modules.security.passwords.schemas import PasswordPolicyRead
from app.core.config import get_settings
from app.db.session import get_db
from fastapi import Request
from app.modules.auth.captcha import  verify_captcha
from app.logs.activity.service import registrar_evento
from app.modules.auth.schemas import (
    LoginRequest,
    MessageResponse,
    PasswordChangeRequiredRequest,
    PasswordRecoveryRequest,
    PasswordRecoveryResetRequest,
    PasswordRecoveryVerifyRequest,
    RegisterRequest,
    SecurityQuestionRequest,
    SecurityQuestionResponse,
    TokenResponse,
    EmailVerificationRequest,
    EmailVerificationConfirmRequest,
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

from app.modules.auth.email_verification import (
    send_email_verification_code,
    verify_email_code,
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
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        print("LOGIN ENDPOINT RECIBIDO =>", payload.model_dump(), flush=True)
        print("RECAPTCHA TOKEN RECIBIDO =>", payload.recaptcha_token[:30], flush=True)

        verify_captcha(
            token=payload.recaptcha_token,
            remote_ip=request.client.host if request.client else None,
        )

        print("RECAPTCHA OK", flush=True)

        resultado = login_user(
            db,
            payload.correo,
            payload.password
        )

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
        mensaje = str(e)
        print("LOGIN VALUE ERROR =>", mensaje, flush=True)

        registrar_evento(
            db=db,
            evento="LOGIN_FALLIDO",
            modulo="auth",
            accion="LOGIN",
            estado="FALLIDO",
            severidad="ALTA",
            descripcion=mensaje
        )

        status_code = (
            status.HTTP_400_BAD_REQUEST
            if "reCAPTCHA" in mensaje
            else status.HTTP_401_UNAUTHORIZED
        )

        raise HTTPException(
            status_code=status_code,
            detail=mensaje,
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
    "/reset-password",
    response_model=MessageResponse
)


@router.put(
    "/security-question",
    response_model=MessageResponse
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

@router.get("/password-policy/public")
def get_public_password_policy(db: Session = Depends(get_db)):
    policy = get_active_password_policy(db)
    return {
        "longitud_minima": policy.longitud_minima,
        "requiere_mayusculas": policy.requiere_mayusculas,
        "requiere_minusculas": policy.requiere_minusculas,
        "requiere_numeros": policy.requiere_numeros,
        "requiere_simbolos": policy.requiere_simbolos,
    }

@router.post("/email-verification/request", response_model=MessageResponse)
def request_email_verification(
    payload: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    try:
        return send_email_verification_code(db, str(payload.correo))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/email-verification/confirm", response_model=MessageResponse)
def confirm_email_verification(
    payload: EmailVerificationConfirmRequest,
    db: Session = Depends(get_db),
):
    try:
        return verify_email_code(db, str(payload.correo), payload.codigo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )