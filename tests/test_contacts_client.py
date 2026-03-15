"""Tests for GoogleContactsClient with mocked Google API."""

from __future__ import annotations

from unittest.mock import MagicMock

from business_assistant_contacts.config import ContactsSettings
from business_assistant_contacts.contacts_client import GoogleContactsClient
from tests.conftest import SAMPLE_PERSON


class TestGoogleContactsClient:
    def _make_client(
        self, settings: ContactsSettings, mock_service: MagicMock
    ) -> GoogleContactsClient:
        """Create a client with a pre-injected mock service."""
        client = GoogleContactsClient(settings)
        client._service = mock_service
        return client

    def test_test_connection_success(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().get().execute.return_value = {"resourceName": "people/me"}
        client = self._make_client(contacts_settings, mock_service)

        assert client.test_connection() is True

    def test_test_connection_failure(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().get().execute.side_effect = Exception("API error")
        client = self._make_client(contacts_settings, mock_service)

        assert client.test_connection() is False

    def test_search_contacts(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().searchContacts().execute.return_value = {
            "results": [{"person": SAMPLE_PERSON}]
        }
        client = self._make_client(contacts_settings, mock_service)

        result = client.search_contacts("Alice")

        assert len(result) == 1
        assert result[0]["names"][0]["givenName"] == "Alice"

    def test_search_contacts_empty(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().searchContacts().execute.return_value = {"results": []}
        client = self._make_client(contacts_settings, mock_service)

        result = client.search_contacts("unknown")

        assert result == []

    def test_search_contacts_failure(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().searchContacts().execute.side_effect = Exception("API error")
        client = self._make_client(contacts_settings, mock_service)

        result = client.search_contacts("Alice")

        assert result == []

    def test_list_contacts(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().connections().list().execute.return_value = {
            "connections": [SAMPLE_PERSON]
        }
        client = self._make_client(contacts_settings, mock_service)

        result = client.list_contacts()

        assert len(result) == 1

    def test_list_contacts_empty(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().connections().list().execute.return_value = {}
        client = self._make_client(contacts_settings, mock_service)

        result = client.list_contacts()

        assert result == []

    def test_get_contact(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().get().execute.return_value = SAMPLE_PERSON
        client = self._make_client(contacts_settings, mock_service)

        result = client.get_contact("people/c123456")

        assert result is not None
        assert result["names"][0]["givenName"] == "Alice"

    def test_get_contact_failure(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().get().execute.side_effect = Exception("Not found")
        client = self._make_client(contacts_settings, mock_service)

        result = client.get_contact("people/c999999")

        assert result is None

    def test_create_contact(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().createContact().execute.return_value = SAMPLE_PERSON
        client = self._make_client(contacts_settings, mock_service)

        body = {"names": [{"givenName": "Alice", "familyName": "Smith"}]}
        result = client.create_contact(body)

        assert result is not None
        assert result["names"][0]["givenName"] == "Alice"

    def test_create_contact_failure(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().createContact().execute.side_effect = Exception("API error")
        client = self._make_client(contacts_settings, mock_service)

        result = client.create_contact({"names": [{"givenName": "Test"}]})

        assert result is None

    def test_update_contact(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        updated = {**SAMPLE_PERSON, "names": [{"givenName": "Alice", "familyName": "Updated"}]}
        mock_service.people().updateContact().execute.return_value = updated
        client = self._make_client(contacts_settings, mock_service)

        body = {"names": [{"familyName": "Updated"}], "etag": "abc"}
        result = client.update_contact("people/c123456", body, "names")

        assert result is not None
        assert result["names"][0]["familyName"] == "Updated"

    def test_update_contact_failure(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().updateContact().execute.side_effect = Exception("API error")
        client = self._make_client(contacts_settings, mock_service)

        result = client.update_contact("people/c123456", {}, "names")

        assert result is None

    def test_delete_contact(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().deleteContact().execute.return_value = None
        client = self._make_client(contacts_settings, mock_service)

        assert client.delete_contact("people/c123456") is True

    def test_delete_contact_failure(self, contacts_settings: ContactsSettings) -> None:
        mock_service = MagicMock()
        mock_service.people().deleteContact().execute.side_effect = Exception("Not found")
        client = self._make_client(contacts_settings, mock_service)

        assert client.delete_contact("people/c999999") is False
