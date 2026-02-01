---
name: generate-test-cases
description: >
  This skill should be used when the user asks to "generate test cases", "create test cases for a website",
  "explore a web app and write test specs", "map all paths and create tests", or provides a user journey
  and URL and wants comprehensive test case specifications including failure paths and edge cases.
user-invocable: true
argument-hint: <url> <user journey description>
---

# Generate Test Cases

Generate comprehensive, structured test case specifications for a web application by exploring it live in a browser.

## Workflow

1. **Parse the input** — extract the target URL and user journey description from the arguments: $ARGUMENTS
2. **Launch the test-case-generator agent** — use the Task tool to invoke the `test-case-generator` agent with the URL and journey description
3. **The agent will**:
   - Navigate to the URL and walk through the described journey
   - Use `find_elements`, `get_form_understanding`, and `get_field_context` to catalog all interactive elements
   - Systematically probe for failures: empty required fields, invalid formats, boundary values, navigation edge cases
   - Reason about additional scenarios that cannot be directly tested (network failures, concurrency, session expiry)
4. **Output** — the agent writes structured test case specs to `test-cases/<feature-name>.md` organized by category: Happy Path, Validation, Edge Cases, Boundary Conditions, Security, Accessibility

## Example Usage

```
/generate-test-cases https://example.com/login User logs in with email and password, sees dashboard
```

```
/generate-test-cases https://shop.example.com User searches for a product, adds to cart, proceeds to checkout
```
