"""Google Contacts (People API) client with OAuth2 authentication."""

from __future__ import annotations

import logging
from typing import ClassVar

from business_assistant_google_auth import GoogleAuthClient

from .config import ContactsSettings
from .constants import CONTACTS_SCOPES, PERSON_FIELDS

logger = logging.getLogger(__name__)


class GoogleContactsClient(GoogleAuthClient):
    """Wraps the Google People API with OAuth2 auth and contact operations."""

    SCOPES: ClassVar[list[str]] = CONTACTS_SCOPES

    def __init__(self, settings: ContactsSettings) -> None:
        """Initialize with ContactsSettings."""
        super().__init__(
            settings, scopes=self.SCOPES, api_name="people", api_version="v1"
        )

    def test_connection(self) -> bool:
        """Test the Google People API connection."""
        try:
            service = self._get_service()
            service.people().get(
                resourceName="people/me", personFields="names"
            ).execute()
            logger.info("Google Contacts connection test successful")
            return True
        except Exception as e:
            logger.error("Google Contacts connection test failed: %s", e)
            return False

    def search_contacts(self, query: str) -> list[dict]:
        """Search contacts by name, email, or phone number."""
        try:
            service = self._get_service()
            result = service.people().searchContacts(
                query=query,
                readMask=PERSON_FIELDS,
                pageSize=30,
            ).execute()
            results = result.get("results", [])
            return [r["person"] for r in results if "person" in r]
        except Exception as e:
            logger.error("Failed to search contacts: %s", e)
            return []

    def list_contacts(self, page_size: int = 100) -> list[dict]:
        """List all contacts."""
        try:
            service = self._get_service()
            result = service.people().connections().list(
                resourceName="people/me",
                personFields=PERSON_FIELDS,
                pageSize=min(page_size, 1000),
                sortOrder="FIRST_NAME_ASCENDING",
            ).execute()
            return result.get("connections", [])
        except Exception as e:
            logger.error("Failed to list contacts: %s", e)
            return []

    def get_contact(self, resource_name: str) -> dict | None:
        """Get full details for a specific contact."""
        try:
            service = self._get_service()
            return service.people().get(
                resourceName=resource_name,
                personFields=PERSON_FIELDS,
            ).execute()
        except Exception as e:
            logger.error("Failed to get contact %s: %s", resource_name, e)
            return None

    def create_contact(self, person_body: dict) -> dict | None:
        """Create a new contact. Returns the created person resource."""
        try:
            service = self._get_service()
            return service.people().createContact(
                body=person_body,
                personFields=PERSON_FIELDS,
            ).execute()
        except Exception as e:
            logger.error("Failed to create contact: %s", e)
            return None

    def update_contact(
        self, resource_name: str, person_body: dict, update_mask: str
    ) -> dict | None:
        """Update an existing contact. Returns the updated person resource."""
        try:
            service = self._get_service()
            return service.people().updateContact(
                resourceName=resource_name,
                body=person_body,
                updatePersonFields=update_mask,
                personFields=PERSON_FIELDS,
            ).execute()
        except Exception as e:
            logger.error("Failed to update contact %s: %s", resource_name, e)
            return None

    def delete_contact(self, resource_name: str) -> bool:
        """Delete a contact by resource name."""
        try:
            service = self._get_service()
            service.people().deleteContact(
                resourceName=resource_name,
            ).execute()
            logger.info("Deleted contact %s", resource_name)
            return True
        except Exception as e:
            logger.error("Failed to delete contact %s: %s", resource_name, e)
            return False
