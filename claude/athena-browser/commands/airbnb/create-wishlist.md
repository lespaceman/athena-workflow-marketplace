---
name: create-wishlist
description: Create and manage Airbnb wishlists - create new lists, add properties, organize saved stays.
---

# Create Airbnb Wishlist

Create a new wishlist and optionally add properties to it.

## Usage

```
/athena-browser:airbnb/create-wishlist [--name <wishlist-name>] [--add-current]
```

## Options

- `--name <wishlist-name>`: Name for the new wishlist
- `--add-current`: Add the currently viewed property to the wishlist

## Prerequisites

- Browser must be launched (`/athena-browser:common/launch`)
- User must be logged in (`/athena-browser:airbnb/login`)

## Workflow Steps

1. **Verify Login State**
   - Capture snapshot
   - Confirm user is authenticated (profile menu visible)

2. **Navigate to Wishlists** (if creating from scratch)
   - Find profile menu in header
   - Click to open dropdown
   - Find and click "Wishlists" option

3. **Create New Wishlist**
   - Find "Create new wishlist" button
   - Click to open creation modal
   - Find name input field: `kind: "textbox"`
   - Type the wishlist name
   - Click "Create" button

4. **Add Property to Wishlist** (if on a listing page)
   - Find the heart/save icon on the listing
   - Click to open wishlist selector
   - Select the target wishlist or create new
   - Confirm addition

5. **Verify Wishlist Created**
   - Navigate to wishlists page
   - Confirm new wishlist appears
   - Report success to user

## Element Patterns

- **Save/Heart Icon**: `kind: "button"`, look for heart icon or "Save" label
- **Wishlist Modal**: Modal overlay with list options
- **Create Button**: `kind: "button"`, `label: "Create"`
- **Wishlist Name Input**: `kind: "textbox"` in modal

## MCP Tools Used

- `mcp__athena-browser-mcp-local__navigate`
- `mcp__athena-browser-mcp-local__find_elements`
- `mcp__athena-browser-mcp-local__click`
- `mcp__athena-browser-mcp-local__type`
- `mcp__athena-browser-mcp-local__capture_snapshot`

## Example Workflow

```
Assistant: I'll create a new wishlist called "Beach Getaways".

[Navigate to wishlists section]
[Click "Create new wishlist"]
[Type "Beach Getaways" in name field]
[Click "Create"]

Wishlist "Beach Getaways" created successfully!
```

## Notes

- Wishlists require authentication
- Maximum wishlist name length may be limited
- Properties can belong to multiple wishlists
