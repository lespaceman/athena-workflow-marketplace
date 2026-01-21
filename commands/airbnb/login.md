---
description: Authenticate to Airbnb with email/phone and password or OAuth providers.
---

# Airbnb Login

Authenticate to Airbnb using credentials or OAuth providers.

## Usage

```
/athena-browser:airbnb/login [--email <email>] [--phone <phone>]
```

## Options

- `--email <email>`: Login using email address
- `--phone <phone>`: Login using phone number

## Prerequisites

- Browser must be launched first (`/athena-browser:common/launch`)
- User credentials (will be requested securely if not provided)

## Workflow Steps

1. **Navigate to Airbnb**
   - Use `navigate` tool to go to `https://www.airbnb.com`
   - Wait for page load

2. **Handle Cookie Consent**
   - Use `find_elements` with `label: "Accept"` or `label: "Accept all"`
   - Click the consent button if present

3. **Open Login Modal**
   - Use `find_elements` to find login/signup button (usually in header)
   - Look for: `kind: "button"`, label contains "Log in" or profile icon
   - Click to open login modal

4. **Select Login Method**
   - Find "Continue with email" or phone option
   - Click the appropriate option

5. **Enter Credentials**
   - Find email/phone input field: `kind: "textbox"`
   - Type the credential using `type` tool
   - Click "Continue" button

6. **Enter Password**
   - Wait for password field to appear
   - Find password input: `kind: "textbox"`, type "password"
   - Type the password
   - Click "Log in" button

7. **Verify Login Success**
   - Capture snapshot
   - Look for profile menu or user avatar
   - Confirm authentication state

## MCP Tools Used

- `mcp__athena-browser-mcp-local__navigate`
- `mcp__athena-browser-mcp-local__find_elements`
- `mcp__athena-browser-mcp-local__click`
- `mcp__athena-browser-mcp-local__type`
- `mcp__athena-browser-mcp-local__capture_snapshot`

## Security Notes

- Never store credentials in plain text
- Prompt user securely for password input
- Support OAuth options (Google, Facebook, Apple) when available
- Handle 2FA/MFA if enabled on the account
