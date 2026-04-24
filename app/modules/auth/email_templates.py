def build_password_recovery_email(user_name: str, code: str) -> tuple[str, str]:
    subject = "Recuperación de contraseña - Monster Dojo"

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background: #f7f9fc; padding: 24px; color: #1f2937;">
        <div style="max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 12px; padding: 32px; border: 1px solid #e5e7eb;">
          <h2 style="margin-top: 0; color: #192847;">Recuperación de contraseña</h2>

          <p>Hola {user_name},</p>

          <p>Recibimos una solicitud para restablecer tu contraseña.</p>

          <p>Tu código temporal es:</p>

          <div style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #192847; margin: 24px 0;">
            {code}
          </div>

          <p>Este código expira en <strong>10 minutos</strong> y solo puede usarse una vez.</p>

          <p>Si no solicitaste este cambio, ignora este mensaje.</p>

          <hr style="margin: 24px 0; border: none; border-top: 1px solid #e5e7eb;" />

          <p style="font-size: 13px; color: #6b7280;">
            Monster Dojo - Sistema de recuperación segura de contraseñas
          </p>
        </div>
      </body>
    </html>
    """

    text_body = (
        f"Hola {user_name},\n\n"
        f"Recibimos una solicitud para restablecer tu contraseña.\n"
        f"Tu código temporal es: {code}\n\n"
        f"Este código expira en 10 minutos y solo puede usarse una vez.\n"
        f"Si no solicitaste este cambio, ignora este mensaje.\n\n"
        f"Monster Dojo"
    )

    return subject, html_body, text_body