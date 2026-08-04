from __future__ import annotations

from email.message import EmailMessage
from pathlib import Path
from typing import Any

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from fastapi_auth.config import BASE_DIR, get_settings


class EmailService:
    """Service for rendering and sending emails."""

    def __init__(self) -> None:
        self.settings = get_settings()

        self.jinja = Environment(
            loader=FileSystemLoader(BASE_DIR / "templates" / "email"),
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=False,
        )

    def render_template(
        self,
        template_name: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """
        Render an HTML email template.
        """
        template = self.jinja.get_template(template_name)
        return template.render(**(context or {}))

    async def send(
        self,
        *,
        to: str | list[str],
        subject: str,
        template: str,
        context: dict[str, Any] | None = None,
        text: str | None = None,
        cc: str | list[str] | None = None,
        bcc: str | list[str] | None = None,
        reply_to: str | None = None,
    ) -> None:
        """
        Render and send an email.

        Args:
            to: Recipient(s).
            subject: Email subject.
            template: HTML template filename.
            context: Template context.
            text: Optional plain-text version.
            cc: CC recipient(s).
            bcc: BCC recipient(s).
            reply_to: Optional Reply-To address.
        """

        if isinstance(to, str):
            to = [to]

        if cc is None:
            cc = []
        elif isinstance(cc, str):
            cc = [cc]

        if bcc is None:
            bcc = []
        elif isinstance(bcc, str):
            bcc = [bcc]

        html = self.render_template(template, context)

        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = (
            f"{self.settings.SMTP_FROM_NAME} " f"<{self.settings.SMTP_FROM_EMAIL}>"
        )
        message["To"] = ", ".join(to)

        if cc:
            message["Cc"] = ", ".join(cc)

        if reply_to:
            message["Reply-To"] = reply_to

        message.set_content(
            text
            or "This email contains HTML content. Please use an HTML-compatible email client."
        )

        message.add_alternative(html, subtype="html")

        recipients = [*to, *cc, *bcc]

        smtp_kwargs = {
            "hostname": self.settings.SMTP_HOST,
            "port": self.settings.SMTP_PORT,
            "start_tls": self.settings.SMTP_USE_TLS,
            "use_tls": self.settings.SMTP_USE_SSL,
            "recipients": recipients,
        }

        if self.settings.SMTP_USERNAME:
            smtp_kwargs["username"] = self.settings.SMTP_USERNAME
            smtp_kwargs["password"] = self.settings.SMTP_PASSWORD

        await aiosmtplib.send(
            message,
            **smtp_kwargs,
        )


email_service = EmailService()
