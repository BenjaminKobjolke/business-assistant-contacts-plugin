"""Tests for ContactsService."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from business_assistant_contacts.contacts_service import ContactsService
from tests.conftest import SAMPLE_PERSON, SAMPLE_PERSON_MINIMAL


class TestContactsService:
    def _make_service(self, mock_client: MagicMock) -> ContactsService:
        """Create a ContactsService with a mocked client."""
        with patch(
            "business_assistant_contacts.contacts_service.GoogleContactsClient",
            return_value=mock_client,
        ):
            from business_assistant_contacts.config import ContactsSettings

            settings = ContactsSettings(
                credentials_path="/tmp/creds.json",
                token_path="/tmp/token.json",
                oauth_port=51033,
            )
            return ContactsService(settings)

    def test_search_contacts_with_results(self) -> None:
        mock_client = MagicMock()
        mock_client.search_contacts.return_value = [SAMPLE_PERSON]
        service = self._make_service(mock_client)

        result = service.search_contacts("Alice")

        data = json.loads(result)
        assert len(data["contacts"]) == 1
        assert data["contacts"][0]["name"] == "Alice Smith"
        assert data["contacts"][0]["email"] == "alice@example.com"

    def test_search_contacts_no_results(self) -> None:
        mock_client = MagicMock()
        mock_client.search_contacts.return_value = []
        service = self._make_service(mock_client)

        result = service.search_contacts("unknown")

        assert "No contacts found" in result

    def test_list_contacts(self) -> None:
        mock_client = MagicMock()
        mock_client.list_contacts.return_value = [SAMPLE_PERSON, SAMPLE_PERSON_MINIMAL]
        service = self._make_service(mock_client)

        result = service.list_contacts()

        data = json.loads(result)
        assert len(data["contacts"]) == 2

    def test_list_contacts_empty(self) -> None:
        mock_client = MagicMock()
        mock_client.list_contacts.return_value = []
        service = self._make_service(mock_client)

        result = service.list_contacts()

        assert "No contacts found" in result

    def test_get_contact(self) -> None:
        mock_client = MagicMock()
        mock_client.get_contact.return_value = SAMPLE_PERSON
        service = self._make_service(mock_client)

        result = service.get_contact("people/c123456")

        data = json.loads(result)
        assert data["contact"]["name"] == "Alice Smith"
        assert data["contact"]["organization"] == "ACME Corp"
        assert data["contact"]["job_title"] == "Engineer"
        assert data["contact"]["notes"] == "Test notes"

    def test_get_contact_not_found(self) -> None:
        mock_client = MagicMock()
        mock_client.get_contact.return_value = None
        service = self._make_service(mock_client)

        result = service.get_contact("people/c999999")

        assert "Contact not found" in result

    def test_create_contact_success(self) -> None:
        mock_client = MagicMock()
        mock_client.create_contact.return_value = SAMPLE_PERSON
        service = self._make_service(mock_client)

        result = service.create_contact(
            "Alice", family_name="Smith", email="alice@example.com"
        )

        assert "Contact created: Alice Smith" in result

    def test_create_contact_failure(self) -> None:
        mock_client = MagicMock()
        mock_client.create_contact.return_value = None
        service = self._make_service(mock_client)

        result = service.create_contact("Test")

        assert "Failed to create contact" in result

    def test_create_contact_with_all_fields(self) -> None:
        mock_client = MagicMock()
        mock_client.create_contact.return_value = SAMPLE_PERSON
        service = self._make_service(mock_client)

        result = service.create_contact(
            "Alice",
            family_name="Smith",
            email="alice@example.com",
            phone="+49 170 1234567",
            organization="ACME Corp",
            job_title="Engineer",
            notes="Some notes",
        )

        assert "Contact created" in result
        call_args = mock_client.create_contact.call_args[0][0]
        assert "emailAddresses" in call_args
        assert "phoneNumbers" in call_args
        assert "organizations" in call_args
        assert "biographies" in call_args

    def test_update_contact_success(self) -> None:
        mock_client = MagicMock()
        mock_client.get_contact.return_value = SAMPLE_PERSON
        updated = {
            **SAMPLE_PERSON,
            "names": [{"displayName": "Alice Updated", "givenName": "Alice"}],
        }
        mock_client.update_contact.return_value = updated
        service = self._make_service(mock_client)

        result = service.update_contact("people/c123456", email="new@example.com")

        assert "Contact updated" in result

    def test_update_contact_not_found(self) -> None:
        mock_client = MagicMock()
        mock_client.get_contact.return_value = None
        service = self._make_service(mock_client)

        result = service.update_contact("people/c999999", email="new@example.com")

        assert "Contact not found" in result

    def test_update_contact_no_fields(self) -> None:
        mock_client = MagicMock()
        mock_client.get_contact.return_value = SAMPLE_PERSON
        service = self._make_service(mock_client)

        result = service.update_contact("people/c123456")

        assert "No fields to update" in result

    def test_update_contact_failure(self) -> None:
        mock_client = MagicMock()
        mock_client.get_contact.return_value = SAMPLE_PERSON
        mock_client.update_contact.return_value = None
        service = self._make_service(mock_client)

        result = service.update_contact("people/c123456", email="new@example.com")

        assert "Failed to update contact" in result

    def test_delete_contact_success(self) -> None:
        mock_client = MagicMock()
        mock_client.delete_contact.return_value = True
        service = self._make_service(mock_client)

        result = service.delete_contact("people/c123456")

        assert "Contact deleted successfully" in result

    def test_delete_contact_failure(self) -> None:
        mock_client = MagicMock()
        mock_client.delete_contact.return_value = False
        service = self._make_service(mock_client)

        result = service.delete_contact("people/c123456")

        assert "Failed to delete contact" in result

    def test_format_contact_minimal(self) -> None:
        mock_client = MagicMock()
        mock_client.search_contacts.return_value = [SAMPLE_PERSON_MINIMAL]
        service = self._make_service(mock_client)

        result = service.search_contacts("Bob")

        data = json.loads(result)
        contact = data["contacts"][0]
        assert contact["name"] == "Bob Jones"
        assert "email" not in contact
        assert "phone" not in contact
