import os

from requests import Response, post
from typing import List

from libs.strings import gettext


# Custom named exceptions for Mailgun specific issues.
class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")

    SENDER_TITLE = "Shopping List API"
    SENDER_EMAIL = "postmaster@sandboxb941247fbceb417297ca3799c9803886.mailgun.org"

    @classmethod
    def send_email(
        cls,
        email: List[str],
        subject: str,
        text: str,
        html: str,  # email is list in case of multiple recipients
    ) -> Response:
        if cls.MAILGUN_API_KEY is None:
            raise MailGunException(gettext("Failed to load Mailgun API Key."))
        if cls.MAILGUN_DOMAIN is None:
            raise MailGunException(gettext("Failed to load Mailgun domain."))

        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{cls.SENDER_TITLE} <{cls.SENDER_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html,
            },
        )
        if response.status_code != 200:  # If post response fails
            raise MailGunException(gettext("mailgun_error_sending_email"))

        return response
