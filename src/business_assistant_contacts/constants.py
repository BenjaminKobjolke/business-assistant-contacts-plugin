"""Plugin-specific string constants."""

# Environment variable names
ENV_GOOGLE_CONTACTS_CREDENTIALS_PATH = "GOOGLE_CONTACTS_CREDENTIALS_PATH"
ENV_GOOGLE_CONTACTS_TOKEN_PATH = "GOOGLE_CONTACTS_TOKEN_PATH"
ENV_GOOGLE_CONTACTS_OAUTH_PORT = "GOOGLE_CONTACTS_OAUTH_PORT"

# Defaults
DEFAULT_TOKEN_PATH = "contacts_token.json"
DEFAULT_OAUTH_PORT = 51032

# Plugin name and category
PLUGIN_NAME = "contacts"
PLUGIN_CATEGORY = "contacts"
PLUGIN_DESCRIPTION = "Google Contacts operations"

# Plugin data keys
PLUGIN_DATA_CONTACTS_SERVICE = "contacts_service"
PLUGIN_DATA_CONTACTS_SETTINGS = "contacts_settings"
PLUGIN_DATA_CONTACTS_AUTH_STATE = "contacts_auth_state"

# Google People API
CONTACTS_SCOPES = ["https://www.googleapis.com/auth/contacts"]
PERSON_FIELDS = (
    "names,emailAddresses,phoneNumbers,organizations,"
    "addresses,biographies,urls,birthdays"
)

# System prompt extra
SYSTEM_PROMPT_CONTACTS = """You have access to Google Contacts tools:
- search_contacts: Search contacts by name, email, or phone
- get_contact: Get full details for a specific contact (by resource_name from search/list results)
- list_contacts: List all contacts
- create_contact: Create a new contact
- update_contact: Update an existing contact's fields (only provided fields changed)
- delete_contact: Delete a contact

## Formatting — CRITICAL
- The `_id` field in results is for internal use only — NEVER include it in responses.
- Compose natural-language summaries from the other fields.
- NEVER include any internal IDs (resource names like "people/c123456") in your responses.

## Creating contacts — IMPORTANT
Show preview of what will be created, ask for confirmation before calling create_contact.
After creating, check the response for a "mismatches" field. If present, Google may have \
merged the new contact with an existing one. Warn the user and show what differs. \
Suggest reviewing or updating the contact to correct merged data.

## Deleting contacts
Search or list first, confirm the correct contact, then delete.

## Updating contacts
Use search_contacts or list_contacts first to find the resource_name, then update.
Only provide fields that need to change."""

SYSTEM_PROMPT_CONTACTS_SETUP = """Google Contacts integration is available \
but not yet authenticated.

You have two setup tools:
- contacts_start_auth: Starts Google OAuth and returns the authorization URL.
- contacts_complete_auth: Completes authorization after the user approves in \
their browser.

When the user asks about contacts or people:
1. Tell them Google Contacts is available but needs a one-time authorization.
2. Offer to start — call contacts_start_auth and share the returned URL.
3. The user must open the URL in a browser that can reach this server's localhost.
4. After they confirm they authorized, call contacts_complete_auth.
5. Tell them the bot needs a full process restart to activate Contacts tools."""
