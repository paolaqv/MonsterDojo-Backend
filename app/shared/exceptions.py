class AppException(Exception):

    def __init__(
        self,
        status_code,
        code,
        message
    ):
        self.status_code=status_code
        self.code=code
        self.message=message


class BadRequestError(AppException):
    def __init__(self,msg="Solicitud inválida"):
        super().__init__(
           400,
           "BAD_REQUEST",
           msg
        )


class UnauthorizedError(AppException):
    def __init__(self):
        super().__init__(
           401,
           "UNAUTHORIZED",
           "Credenciales inválidas"
        )


class ForbiddenError(AppException):
    def __init__(self):
        super().__init__(
           403,
           "FORBIDDEN",
           "Acceso denegado"
        )


class NotFoundError(AppException):
    def __init__(self,msg="No encontrado"):
        super().__init__(
          404,
          "NOT_FOUND",
          msg
        )
class ConflictError(AppException):

    def __init__(
        self,
        msg="Conflicto detectado"
    ):

        super().__init__(
            409,
            "CONFLICT",
            msg
        )