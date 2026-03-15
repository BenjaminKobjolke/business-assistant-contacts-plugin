"""Google Contacts settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from business_assistant_google_auth import GoogleAuthSettings

from .constants import (
    DEFAULT_OAUTH_PORT,
    DEFAULT_TOKEN_PATH,
    ENV_GOOGLE_CONTACTS_CREDENTIALS_PATH,
    ENV_GOOGLE_CONTACTS_OAUTH_PORT,
    ENV_GOOGLE_CONTACTS_TOKEN_PATH,
)


@dataclass(frozen=True)
class ContactsSettings(GoogleAuthSettings):
    """Google Contacts connection settings."""


def load_contacts_settings() -> ContactsSettings | None:
    """Load contacts settings from environment variables.

    Returns None if GOOGLE_CONTACTS_CREDENTIALS_PATH is not configured.
    """
    credentials_path = os.environ.get(ENV_GOOGLE_CONTACTS_CREDENTIALS_PATH, "")
    if not credentials_path:
        return None

    return ContactsSettings(
        credentials_path=credentials_path,
        token_path=os.environ.get(ENV_GOOGLE_CONTACTS_TOKEN_PATH, DEFAULT_TOKEN_PATH),
        oauth_port=int(
            os.environ.get(ENV_GOOGLE_CONTACTS_OAUTH_PORT, str(DEFAULT_OAUTH_PORT))
        ),
    )
