"""Plugin registration — defines PydanticAI tools for contact operations."""

from __future__ import annotations

import logging
from pathlib import Path

from business_assistant.agent.deps import Deps
from business_assistant.plugins.registry import PluginInfo, PluginRegistry
from business_assistant_google_auth import create_complete_auth_tool, create_start_auth_tool
from pydantic_ai import RunContext, Tool

from .config import load_contacts_settings
from .constants import (
    CONTACTS_SCOPES,
    PLUGIN_CATEGORY,
    PLUGIN_DATA_CONTACTS_AUTH_STATE,
    PLUGIN_DATA_CONTACTS_SERVICE,
    PLUGIN_DATA_CONTACTS_SETTINGS,
    PLUGIN_DESCRIPTION,
    PLUGIN_NAME,
    SYSTEM_PROMPT_CONTACTS,
    SYSTEM_PROMPT_CONTACTS_SETUP,
)
from .contacts_service import ContactsService

logger = logging.getLogger(__name__)


def _get_service(ctx: RunContext[Deps]) -> ContactsService:
    """Retrieve the ContactsService from plugin_data."""
    return ctx.deps.plugin_data[PLUGIN_DATA_CONTACTS_SERVICE]


def _search_contacts(ctx: RunContext[Deps], query: str) -> str:
    """Search contacts by name, email, or phone number."""
    return _get_service(ctx).search_contacts(query)


def _list_contacts(ctx: RunContext[Deps], page_size: int = 100) -> str:
    """List all contacts. Optionally specify page_size (default 100, max 1000)."""
    return _get_service(ctx).list_contacts(page_size)


def _get_contact(ctx: RunContext[Deps], resource_name: str) -> str:
    """Get full details for a specific contact by resource_name (from search/list results)."""
    return _get_service(ctx).get_contact(resource_name)


def _create_contact(
    ctx: RunContext[Deps],
    given_name: str,
    family_name: str = "",
    email: str = "",
    phone: str = "",
    organization: str = "",
    job_title: str = "",
    notes: str = "",
) -> str:
    """Create a new contact. At minimum provide given_name."""
    return _get_service(ctx).create_contact(
        given_name, family_name=family_name, email=email, phone=phone,
        organization=organization, job_title=job_title, notes=notes,
    )


def _update_contact(
    ctx: RunContext[Deps],
    resource_name: str,
    given_name: str = "",
    family_name: str = "",
    email: str = "",
    phone: str = "",
    organization: str = "",
    job_title: str = "",
    notes: str = "",
) -> str:
    """Update an existing contact's fields. Only provided fields are changed.
    Use search_contacts or list_contacts first to find the resource_name.
    """
    return _get_service(ctx).update_contact(
        resource_name, given_name=given_name, family_name=family_name,
        email=email, phone=phone, organization=organization,
        job_title=job_title, notes=notes,
    )


def _delete_contact(ctx: RunContext[Deps], resource_name: str) -> str:
    """Delete a contact by resource_name. Use search_contacts or list_contacts first."""
    return _get_service(ctx).delete_contact(resource_name)


# --- Setup / Auth tools (created via shared factory) ---

_contacts_start_auth = create_start_auth_tool(
    service_name="Google Contacts",
    scopes=CONTACTS_SCOPES,
    settings_key=PLUGIN_DATA_CONTACTS_SETTINGS,
    auth_state_key=PLUGIN_DATA_CONTACTS_AUTH_STATE,
)

_contacts_complete_auth = create_complete_auth_tool(
    service_name="Google Contacts",
    auth_state_key=PLUGIN_DATA_CONTACTS_AUTH_STATE,
)


def register(registry: PluginRegistry) -> None:
    """Register the contacts plugin with the plugin registry.

    Reads Google Contacts settings from environment. Skips registration
    if GOOGLE_CONTACTS_CREDENTIALS_PATH is not configured.
    """
    from business_assistant.config.log_setup import add_plugin_logging

    add_plugin_logging("contacts", "business_assistant_contacts")

    settings = load_contacts_settings()
    if settings is None:
        logger.info(
            "Contacts plugin: GOOGLE_CONTACTS_CREDENTIALS_PATH not configured, "
            "skipping registration"
        )
        return

    if not Path(settings.token_path).exists():
        logger.info(
            "Contacts plugin: token not found, registering setup tools"
        )
        registry.plugin_data[PLUGIN_DATA_CONTACTS_SETTINGS] = settings
        tools = [
            Tool(_contacts_start_auth, name="contacts_start_auth"),
            Tool(_contacts_complete_auth, name="contacts_complete_auth"),
        ]
        info = PluginInfo(
            name=PLUGIN_NAME,
            description=PLUGIN_DESCRIPTION,
            system_prompt_extra=SYSTEM_PROMPT_CONTACTS_SETUP,
            category=PLUGIN_CATEGORY,
        )
        registry.register(info, tools)
        return

    service = ContactsService(settings)

    tools = [
        Tool(_search_contacts, name="search_contacts"),
        Tool(_list_contacts, name="list_contacts"),
        Tool(_get_contact, name="get_contact"),
        Tool(_create_contact, name="create_contact"),
        Tool(_update_contact, name="update_contact"),
        Tool(_delete_contact, name="delete_contact"),
    ]

    info = PluginInfo(
        name=PLUGIN_NAME,
        description=PLUGIN_DESCRIPTION,
        system_prompt_extra=SYSTEM_PROMPT_CONTACTS,
        category=PLUGIN_CATEGORY,
    )

    registry.register(info, tools)
    registry.plugin_data[PLUGIN_DATA_CONTACTS_SERVICE] = service

    logger.info("Contacts plugin registered with %d tools", len(tools))
