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

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.email_verification import (
    send_email_verification_code,
    verify_email_code,
)

from app.modules.users.model import Usuario
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
        verify_captcha(
            token=payload.recaptcha_token,
            remote_ip=request.client.host if request.client else None,
        )

        resultado = login_user(
            db,
            payload.correo,
            payload.password
        )

        user_obj = resultado.get("user") if isinstance(resultado, dict) else None
        user_id_login = (
            user_obj.get("id_usuario") if isinstance(user_obj, dict) else None
        )

        registrar_evento(
            db=db,
            usuario_id=user_id_login,
            evento="LOGIN_EXITOSO",
            modulo="auth",
            accion="LOGIN",
            estado="OK",
            severidad="MEDIA",
            descripcion=f"Usuario {payload.correo} inicio sesion correctamente.",
            entidad_afectada="sesion",
        )

        return resultado

    except ValueError as e:
        mensaje = str(e)

        registrar_evento(
            db=db,
            evento="LOGIN_FALLIDO",
            modulo="auth",
            accion="LOGIN",
            estado="FALLIDO",
            severidad="ALTA",
            descripcion=f"Intento fallido para correo '{payload.correo}': {mensaje}",
            entidad_afectada="sesion",
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
# LEGACY: recuperación débil por pregunta/respuesta-no se usa
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


# =========================================================
# NUEVO FLUJO: cambio obligatorio por política
# =========================================================

@router.post("/change-password-required", response_model=MessageResponse)
def change_password_required_endpoint(
    payload: PasswordChangeRequiredRequest,
    db: Session = Depends(get_db),
):
    try:
        resultado = change_password_required(
            db,
            payload.correo,
            payload.current_password,
            payload.new_password,
        )

        registrar_evento(
            db=db,
            evento="PASSWORD_CAMBIADA",
            modulo="auth",
            accion="UPDATE",
            estado="OK",
            severidad="ALTA",
            descripcion=f"El usuario {payload.correo} cambió su contraseña por cambio obligatorio.",
            entidad_afectada="usuario",
        )

        return resultado
    except ValueError as e:
        registrar_evento(
            db=db,
            evento="PASSWORD_CAMBIO_FALLIDO",
            modulo="auth",
            accion="UPDATE",
            estado="FALLIDO",
            severidad="ALTA",
            descripcion=f"Intento fallido de cambio obligatorio para {payload.correo}: {str(e)}",
            entidad_afectada="usuario",
        )
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
        resultado = request_password_recovery(
            db,
            payload.correo,
            settings.app_debug,
        )

        registrar_evento(
            db=db,
            evento="RECUPERACION_SOLICITADA",
            modulo="auth",
            accion="REQUEST",
            estado="OK",
            severidad="MEDIA",
            descripcion=f"Se envió código de recuperación al correo de contacto '{payload.correo}'.",
            entidad_afectada="usuario",
        )

        return resultado
    except ValueError as e:
        registrar_evento(
            db=db,
            evento="RECUPERACION_SOLICITUD_FALLIDA",
            modulo="auth",
            accion="REQUEST",
            estado="FALLIDO",
            severidad="MEDIA",
            descripcion=f"Solicitud de recuperación para '{payload.correo}' falló: {str(e)}",
            entidad_afectada="usuario",
        )
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
        resultado = verify_recovery_code(
            db,
            payload.correo,
            payload.codigo,
        )

        registrar_evento(
            db=db,
            evento="RECUPERACION_VERIFICADA",
            modulo="auth",
            accion="VERIFY",
            estado="OK",
            severidad="MEDIA",
            descripcion=f"Código de recuperación verificado correctamente para '{payload.correo}'.",
            entidad_afectada="usuario",
        )

        return resultado
    except ValueError as e:
        registrar_evento(
            db=db,
            evento="RECUPERACION_VERIFICACION_FALLIDA",
            modulo="auth",
            accion="VERIFY",
            estado="FALLIDO",
            severidad="ALTA",
            descripcion=f"Verificación de código para '{payload.correo}' falló: {str(e)}",
            entidad_afectada="usuario",
        )
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
        resultado = reset_password_with_code(
            db,
            payload.correo,
            payload.codigo,
            payload.new_password,
        )

        registrar_evento(
            db=db,
            evento="PASSWORD_RECUPERADA",
            modulo="auth",
            accion="UPDATE",
            estado="OK",
            severidad="ALTA",
            descripcion=f"El usuario con correo de contacto '{payload.correo}' restableció su contraseña con código de recuperación.",
            entidad_afectada="usuario",
        )

        return resultado
    except ValueError as e:
        registrar_evento(
            db=db,
            evento="PASSWORD_RECUPERACION_FALLIDA",
            modulo="auth",
            accion="UPDATE",
            estado="FALLIDO",
            severidad="ALTA",
            descripcion=f"Intento fallido de restablecer contraseña para '{payload.correo}': {str(e)}",
            entidad_afectada="usuario",
        )
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
    correo = str(payload.correo)
    try:
        resultado = send_email_verification_code(db, correo)

        registrar_evento(
            db=db,
            evento="EMAIL_VERIFICACION_SOLICITADA",
            modulo="auth",
            accion="REQUEST",
            estado="OK",
            severidad="MEDIA",
            descripcion=f"Se envió código de verificación al correo '{correo}'.",
            entidad_afectada="usuario",
        )

        return resultado
    except ValueError as e:
        registrar_evento(
            db=db,
            evento="EMAIL_VERIFICACION_FALLIDA",
            modulo="auth",
            accion="REQUEST",
            estado="FALLIDO",
            severidad="MEDIA",
            descripcion=f"Solicitud de verificación para '{correo}' falló: {str(e)}",
            entidad_afectada="usuario",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/email-verification/confirm", response_model=MessageResponse)
def confirm_email_verification(
    payload: EmailVerificationConfirmRequest,
    db: Session = Depends(get_db),
):
    correo = str(payload.correo)
    try:
        resultado = verify_email_code(db, correo, payload.codigo)

        registrar_evento(
            db=db,
            evento="EMAIL_VERIFICADO",
            modulo="auth",
            accion="VERIFY",
            estado="OK",
            severidad="MEDIA",
            descripcion=f"Correo '{correo}' verificado correctamente.",
            entidad_afectada="usuario",
        )

        return resultado
    except ValueError as e:
        registrar_evento(
            db=db,
            evento="EMAIL_VERIFICACION_CODIGO_FALLIDO",
            modulo="auth",
            accion="VERIFY",
            estado="FALLIDO",
            severidad="ALTA",
            descripcion=f"Verificación de código para '{correo}' falló: {str(e)}",
            entidad_afectada="usuario",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/logout", response_model=MessageResponse)
def logout(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    registrar_evento(
        db=db,
        usuario_id=current_user.id_usuario,
        rol_id=current_user.rol_id_rol,
        evento="CIERRE_SESION",
        modulo="auth",
        accion="LOGOUT",
        estado="OK",
        severidad="MEDIA",
        descripcion=f"Usuario {current_user.correo} cerró sesión.",
        entidad_afectada="sesion",
        entidad_id=current_user.id_usuario,
    )

    return {"message": "Sesión cerrada correctamente."}