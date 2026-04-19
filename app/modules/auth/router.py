from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
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

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        return login_user(db, payload.correo, payload.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        return create_user(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/security-question", response_model=SecurityQuestionResponse)
def security_question(payload: SecurityQuestionRequest, db: Session = Depends(get_db)):
    try:
        return get_security_question(db, payload.correo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/verify-security-answer", response_model=MessageResponse)
def verify_answer(payload: VerifySecurityAnswerRequest, db: Session = Depends(get_db)):
    try:
        return verify_security_answer(db, payload.correo, payload.respuesta_seguridad)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        return reset_password_with_security_answer(
            db,
            payload.correo,
            payload.respuesta_seguridad,
            payload.new_password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/security-question", response_model=MessageResponse)
def update_security_question(
    payload: ChangeSecurityQuestionRequest,
    db: Session = Depends(get_db),
):
    try:
        return change_security_question(
            db,
            payload.correo,
            payload.password,
            payload.nueva_pregunta_seguridad,
            payload.nueva_respuesta_seguridad,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )