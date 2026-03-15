"""Shared test fixtures for the contacts plugin."""

from __future__ import annotations

import pytest

from business_assistant_contacts.config import ContactsSettings

SAMPLE_PERSON = {
    "resourceName": "people/c123456",
    "etag": "%EgUBAi43OBoEAQIFByIMR1ZmQ3hsNW5VVTA9",
    "names": [
        {
            "displayName": "Alice Smith",
            "givenName": "Alice",
            "familyName": "Smith",
        }
    ],
    "emailAddresses": [{"value": "alice@example.com"}],
    "phoneNumbers": [{"value": "+49 170 1234567"}],
    "organizations": [{"name": "ACME Corp", "title": "Engineer"}],
    "biographies": [{"value": "Test notes", "contentType": "TEXT_PLAIN"}],
}

SAMPLE_PERSON_MINIMAL = {
    "resourceName": "people/c789012",
    "etag": "%EgUBAi43OBoEAQIFByIMR1ZmQ3hsNW5VVTA=",
    "names": [
        {
            "displayName": "Bob Jones",
            "givenName": "Bob",
            "familyName": "Jones",
        }
    ],
}


@pytest.fixture()
def contacts_settings() -> ContactsSettings:
    return ContactsSettings(
        credentials_path="/tmp/test_credentials.json",
        token_path="/tmp/test_contacts_token.json",
        oauth_port=51033,
    )
