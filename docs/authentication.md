# Contacts Plugin — In-Chat OAuth Authentication

## Prerequisites

- `GOOGLE_CONTACTS_CREDENTIALS_PATH` set in `.env`, pointing to `credentials.json`
- The `credentials.json` file downloaded from Google Cloud Console (OAuth 2.0 Client ID, Desktop app type)
- `GOOGLE_CONTACTS_OAUTH_PORT` (optional, default `51033`) — the port for the local callback server
- The Google Cloud project must have the **People API** enabled

## How Setup Mode Activates

When the bot starts, the Contacts plugin checks for credentials and token:

1. If `GOOGLE_CONTACTS_CREDENTIALS_PATH` is missing → plugin skips registration entirely
2. If credentials path is set but `contacts_token.json` doesn't exist → **setup mode**: 2 auth tools registered
3. If both exist → **normal mode**: 6 contacts tools registered

## In-Chat OAuth Flow

```
User                    Bot                     Google OAuth
  |                      |                        |
  |  "connect contacts"  |                        |
  |--------------------->|                        |
  |                      |  build auth URL        |
  |                      |  start callback server |
  |  auth URL            |                        |
  |<---------------------|                        |
  |                      |                        |
  |  opens URL in browser                         |
  |---------------------------------------------->|
  |                      |                        |
  |  Google redirects to localhost:51033           |
  |                      |<-----------------------|
  |                      |  (callback received)   |
  |                      |                        |
  |  "done"              |                        |
  |--------------------->|                        |
  |                      |  fetch_token()         |
  |                      |----------------------->|
  |                      |  <access + refresh>    |
  |                      |<-----------------------|
  |  "authorized!"       |                        |
  |<---------------------|                        |
```

### Step 1: `contacts_start_auth`

- Creates an `InstalledAppFlow` from the `credentials.json` file
- Sets `redirect_uri` to `http://localhost:{port}/`
- Generates the authorization URL with `access_type="offline"` and `prompt="consent"`
- Starts a lightweight WSGI callback server on a background thread (listens for the redirect)
- Stores the flow, callback event, and token path in `plugin_data`
- Returns the URL for the user to open

### Step 2: `contacts_complete_auth`

- Checks if the callback server received the redirect (via `threading.Event`)
- If not yet received → tells the user to complete the browser step first
- Exchanges the authorization code for credentials via `flow.fetch_token()`
- Saves credentials as JSON to the configured `token_path`
- Cleans up auth state from `plugin_data`

## Localhost Constraint

The callback server runs on `localhost:{port}`. The user must open the auth URL in a browser **on the same machine** where the bot is running, so that Google's redirect reaches the callback server. This is a standard constraint for Google's Desktop OAuth flow.

## Token Persistence

The token is saved to the path configured by `GOOGLE_CONTACTS_TOKEN_PATH` (default: `contacts_token.json`). It contains both the access token and refresh token. On subsequent starts, the `GoogleContactsClient` loads this file and refreshes the token automatically if expired.

## Post-Auth: Restart Required

After successful authorization, the bot must be **fully stopped and restarted** (`Ctrl+C`, then `uv run python -m business_assistant.main`). The `restart.flag` mechanism only reloads code changes — it does not re-run plugin registration. A full restart is needed to switch from the 2 setup tools to the 6 contacts tools.

## Error Handling

- If `contacts_complete_auth` is called before the user completes the browser flow → informative message to try again
- If `fetch_token()` fails (expired code, network error) → error forwarded to the user, auth state cleaned up
- The user can always retry by calling `contacts_start_auth` again (starts a fresh flow)
- The callback server times out after 300 seconds if no redirect is received
