"""ContactsService — wraps GoogleContactsClient for all contact operations."""

from __future__ import annotations

import json
import logging

from .config import ContactsSettings
from .contacts_client import GoogleContactsClient

logger = logging.getLogger(__name__)


class ContactsService:
    """High-level contact operations returning formatted strings for LLM consumption."""

    def __init__(self, settings: ContactsSettings) -> None:
        self._client = GoogleContactsClient(settings)

    def search_contacts(self, query: str) -> str:
        """Search contacts by name, email, or phone."""
        people = self._client.search_contacts(query)
        if not people:
            return f"No contacts found matching '{query}'."

        items = [_format_contact(p) for p in people]
        return json.dumps({"contacts": items})

    def list_contacts(self, page_size: int = 100) -> str:
        """List all contacts."""
        people = self._client.list_contacts(page_size)
        if not people:
            return "No contacts found."

        items = [_format_contact(p) for p in people]
        return json.dumps({"contacts": items})

    def get_contact(self, resource_name: str) -> str:
        """Get full details for a specific contact."""
        person = self._client.get_contact(resource_name)
        if person is None:
            return f"Contact not found: {resource_name}"

        contact = _format_contact(person)
        return json.dumps({"contact": contact})

    def create_contact(
        self,
        given_name: str,
        family_name: str = "",
        email: str = "",
        phone: str = "",
        organization: str = "",
        job_title: str = "",
        notes: str = "",
    ) -> str:
        """Create a new contact."""
        person_body: dict = {
            "names": [{"givenName": given_name, "familyName": family_name}],
        }
        if email:
            person_body["emailAddresses"] = [{"value": email}]
        if phone:
            person_body["phoneNumbers"] = [{"value": phone}]
        if organization or job_title:
            org: dict = {}
            if organization:
                org["name"] = organization
            if job_title:
                org["title"] = job_title
            person_body["organizations"] = [org]
        if notes:
            person_body["biographies"] = [{"value": notes, "contentType": "TEXT_PLAIN"}]

        result = self._client.create_contact(person_body)
        if not result:
            return "Failed to create contact."

        stored = _format_contact(result)
        requested = _requested_fields(
            given_name, family_name, email, phone, organization, job_title,
        )
        mismatches = _detect_mismatches(requested, stored)

        response: dict = {"status": "created", "contact": stored}
        if mismatches:
            response["warning"] = (
                "Google may have merged this with an existing contact."
            )
            response["mismatches"] = mismatches
        return json.dumps(response)

    def update_contact(
        self,
        resource_name: str,
        given_name: str = "",
        family_name: str = "",
        email: str = "",
        phone: str = "",
        organization: str = "",
        job_title: str = "",
        notes: str = "",
    ) -> str:
        """Update an existing contact. Only provided fields are changed."""
        # First get current contact to preserve etag
        current = self._client.get_contact(resource_name)
        if current is None:
            return f"Contact not found: {resource_name}"

        person_body: dict = {"etag": current.get("etag", "")}
        update_fields: list[str] = []

        if given_name or family_name:
            name_entry: dict = {}
            if given_name:
                name_entry["givenName"] = given_name
            if family_name:
                name_entry["familyName"] = family_name
            person_body["names"] = [name_entry]
            update_fields.append("names")
        if email:
            person_body["emailAddresses"] = [{"value": email}]
            update_fields.append("emailAddresses")
        if phone:
            person_body["phoneNumbers"] = [{"value": phone}]
            update_fields.append("phoneNumbers")
        if organization or job_title:
            org: dict = {}
            if organization:
                org["name"] = organization
            if job_title:
                org["title"] = job_title
            person_body["organizations"] = [org]
            update_fields.append("organizations")
        if notes:
            person_body["biographies"] = [{"value": notes, "contentType": "TEXT_PLAIN"}]
            update_fields.append("biographies")

        if not update_fields:
            return "No fields to update."

        update_mask = ",".join(update_fields)
        result = self._client.update_contact(resource_name, person_body, update_mask)
        if result:
            name = _display_name(result)
            return f"Contact updated: {name}"
        return "Failed to update contact."

    def delete_contact(self, resource_name: str) -> str:
        """Delete a contact by resource name."""
        success = self._client.delete_contact(resource_name)
        if success:
            return "Contact deleted successfully."
        return "Failed to delete contact."


def _requested_fields(
    given_name: str,
    family_name: str,
    email: str,
    phone: str,
    organization: str,
    job_title: str,
) -> dict[str, str]:
    """Build a dict of non-empty requested fields for comparison."""
    fields: dict[str, str] = {"name": f"{given_name} {family_name}".strip()}
    if email:
        fields["email"] = email
    if phone:
        fields["phone"] = phone
    if organization:
        fields["organization"] = organization
    if job_title:
        fields["job_title"] = job_title
    return fields


def _detect_mismatches(
    requested: dict[str, str], stored: dict,
) -> list[dict[str, str]]:
    """Compare requested fields against what Google stored. Return list of diffs."""
    mismatches: list[dict[str, str]] = []
    for key, req_val in requested.items():
        stored_val = stored.get(key, "")
        if req_val and stored_val and req_val.lower() != str(stored_val).lower():
            mismatches.append({
                "field": key,
                "requested": req_val,
                "stored": str(stored_val),
            })
        elif req_val and not stored_val:
            mismatches.append({
                "field": key,
                "requested": req_val,
                "stored": "(missing)",
            })
    # Check for unexpected phone from a merged contact
    if not requested.get("phone") and stored.get("phone"):
        mismatches.append({
            "field": "phone",
            "requested": "(not provided)",
            "stored": stored["phone"],
        })
    return mismatches


def _display_name(person: dict) -> str:
    """Extract display name from a person resource."""
    names = person.get("names", [])
    if names:
        display = names[0].get("displayName", "")
        if display:
            return display
        given = names[0].get("givenName", "")
        family = names[0].get("familyName", "")
        return f"{given} {family}".strip()
    return "(unnamed)"


def _format_contact(person: dict) -> dict:
    """Format a person resource as a dict for JSON output."""
    result: dict[str, str] = {
        "_id": person.get("resourceName", ""),
        "name": _display_name(person),
    }

    emails = person.get("emailAddresses", [])
    if emails:
        result["email"] = emails[0].get("value", "")

    phones = person.get("phoneNumbers", [])
    if phones:
        result["phone"] = phones[0].get("value", "")

    orgs = person.get("organizations", [])
    if orgs:
        org_name = orgs[0].get("name", "")
        if org_name:
            result["organization"] = org_name
        title = orgs[0].get("title", "")
        if title:
            result["job_title"] = title

    bios = person.get("biographies", [])
    if bios:
        notes = bios[0].get("value", "")
        if notes:
            result["notes"] = notes

    return result
