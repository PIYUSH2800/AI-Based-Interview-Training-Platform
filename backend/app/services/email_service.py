"""
email_service.py

Reusable backend email delivery service for the AI Interview Platform.
Handles secure password reset link transmission via SMTP with TLS,
bounded timeouts, and graceful offline fallback.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger("email_service")


class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "").strip()
        self.smtp_port = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT", "587").isdigit() else 587
        self.smtp_username = os.getenv("SMTP_USERNAME", "").strip()
        self.smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
        self.smtp_from_email = os.getenv("SMTP_FROM_EMAIL", "").strip() or self.smtp_username
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
        self.frontend_base_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")

        # Testing hook to capture sent emails in automated tests without real SMTP network calls
        self._test_sent_emails = []

    def is_configured(self) -> bool:
        """Returns True only if valid SMTP connection credentials are provided."""
        dummy_placeholders = (
            "your_email@gmail.com",
            "your_app_password",
            "smtp.example.com",
            "REPLACE_WITH_YOUR_SMTP_HOST",
            "",
        )
        if not self.smtp_host or self.smtp_host in dummy_placeholders:
            return False
        if not self.smtp_username or self.smtp_username in dummy_placeholders:
            return False
        if not self.smtp_password or self.smtp_password in dummy_placeholders:
            return False
        return True

    def get_email_status(self) -> dict:
        """Returns configuration status without exposing credentials."""
        configured = self.is_configured()
        return {
            "configured": configured,
            "smtp_host": self.smtp_host if configured else None,
            "smtp_port": self.smtp_port if configured else None,
            "from_email": self.smtp_from_email if configured else None,
            "tls_enabled": self.smtp_use_tls,
            "frontend_base_url": self.frontend_base_url,
        }

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """
        Sends a secure password reset link to the recipient email address.
        Returns True if delivery succeeded, False if SMTP is unconfigured or fails.
        """
        reset_link = f"{self.frontend_base_url}/reset-password?token={reset_token}"

        # If in-memory testing hook has been installed or active in test environment:
        self._test_sent_emails.append({
            "to": to_email,
            "token": reset_token,
            "link": reset_link
        })

        if not self.is_configured():
            logger.warning(
                f"[EmailService] SMTP not configured. Password reset link generated for {to_email} "
                "was not sent via external mail server."
            )
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Reset Your AI Interview Platform Password"
            msg["From"] = f"AI Interview Platform <{self.smtp_from_email}>"
            msg["To"] = to_email

            text_content = (
                f"Hello,\n\n"
                f"We received a request to reset the password for your AI Interview Platform account.\n\n"
                f"Please open the following link in your browser to choose a new password:\n"
                f"{reset_link}\n\n"
                f"This link will expire in 20 minutes and can only be used once.\n\n"
                f"If you did not request a password reset, you can safely ignore this email.\n\n"
                f"— The AI Interview Platform Team"
            )

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #020617; color: #f8fafc; margin: 0; padding: 24px; }}
                    .card {{ max-width: 540px; margin: 0 auto; background-color: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 32px; }}
                    .logo {{ font-size: 20px; font-weight: bold; color: #6366f1; margin-bottom: 24px; display: inline-block; }}
                    h1 {{ font-size: 22px; font-weight: bold; color: #ffffff; margin-top: 0; }}
                    p {{ font-size: 14px; line-height: 1.6; color: #94a3b8; }}
                    .btn {{ display: inline-block; background-color: #4f46e5; color: #ffffff !important; padding: 12px 24px; text-decoration: none; font-weight: 600; font-size: 14px; border-radius: 10px; margin: 20px 0; }}
                    .footer {{ font-size: 12px; color: #64748b; margin-top: 32px; border-top: 1px solid #1e293b; padding-top: 16px; }}
                    .link-break {{ word-break: break-all; color: #818cf8; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <div class="logo">⚡ AI Interview Platform</div>
                    <h1>Password Reset Request</h1>
                    <p>Hello,</p>
                    <p>We received a request to reset your password for the <strong>AI Interview Platform</strong>. Click the button below to set a new password:</p>
                    <p><a href="{reset_link}" class="btn" target="_blank">Reset Password</a></p>
                    <p>Or paste this link into your browser:</p>
                    <p class="link-break">{reset_link}</p>
                    <p><strong>Note:</strong> This link is valid for <strong>20 minutes</strong> and can only be used once.</p>
                    <p>If you did not request this, please disregard this email.</p>
                    <div class="footer">
                        AI Interview Training Platform &bull; Localhost Demonstration System
                    </div>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            # Bounded network timeout of 10.0 seconds
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10.0)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10.0)
                if self.smtp_use_tls:
                    server.starttls()

            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            server.send_message(msg)
            server.quit()
            logger.info(f"[EmailService] Password reset email delivered successfully to {to_email}.")
            return True

        except (smtplib.SMTPException, OSError) as e:
            logger.error(f"[EmailService] SMTP delivery failed for {to_email}: {e.__class__.__name__}: {e}")
            return False
        except Exception as e:
            logger.error(f"[EmailService] Unexpected error sending email: {e.__class__.__name__}")
            return False


# Singleton instance
email_service = EmailService()
