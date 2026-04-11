# Anti-Patterns: Detailed Explanations and Fix Strategies

## 1. Raw CSS / XPath selectors
Use semantic Browser library locators (`role=`, `label=`, `text=`, `[data-testid=]`) instead of raw CSS or XPath. CSS and XPath selectors are brittle and break when markup changes.

**Why:** A class rename, component refactor, or CSS-in-JS migration breaks every CSS-based selector overnight. Semantic locators survive these changes because they target accessible roles and labels, not implementation details.

**Fix:** Replace `css=.submit-btn` with `role=button[name="Submit"]`. Follow the locator strategy hierarchy in the main skill.

## 2. `Sleep`
Use proper assertions and event-driven waits. `Sleep` adds arbitrary delays that slow tests and mask timing issues.

**Why:** A 2-second `Sleep` that works locally may be too short in CI (slower machines) or too long everywhere (wasting time). It also hides the real question: "what am I actually waiting for?"

**Fix:** Replace with `Wait For Response    matcher=**/api/data` for API-dependent UI, `Wait For Elements State    <locator>    visible` for element appearance, or `Wait For Elements State    role=progressbar    hidden` for loading states.

## 3. Fragile `>> nth=0` / positional selectors
Scope locators to a parent with `>>` chaining instead of relying on position. If position is unavoidable, add a comment explaining why.

**Why:** Element order can change when the page adds a banner, reorders a list, or renders asynchronously. `>> nth=0` silently picks the wrong element, causing false passes or mysterious failures.

**Fix:** Use `[data-testid="cart"] >> role=button[name="Remove"]` or chain to a container with unique text: `role=listitem >> text=Specific Item`.

## 4. Exact long text matches
Use `text=/regex/i` with key words instead of matching entire strings. Marketing copy and UI text change frequently.

**Why:** A copywriter changes "Sign up for free today!" to "Create your free account" and every test matching the full string breaks, even though the feature works fine.

**Fix:** Use `text=/sign up/i` or `role=button[name="/free/i"]` — match the stable semantic keywords.

## 5. Unscoped locators
Scope locators to `main`, `nav`, `dialog`, or another container when possible. Global locators match unintended elements.

**Why:** A page-wide `role=button[name="Submit"]` may match a submit button in the header, footer, or a hidden modal — not just the one in your form. This causes the wrong click or ambiguous locator errors.

**Fix:** Scope first: `main >> role=button[name="Submit"]` or `[role="dialog"] >> role=button[name="Save"]`.

## 6. Login via UI in every test
Reuse persisted browser state or API-based auth setup. UI login in every test wastes time and creates coupling to the login flow.

**Why:** If every test clicks through the login form, a single login page change breaks the entire suite. It also adds 3-10 seconds per test — multiplied across hundreds of tests, this becomes significant CI time.

**Fix:** Log in once in `Suite Setup` or a shared resource, save the context state via `Save Storage State    auth.json`, and reuse it with `New Context    storageState=auth.json`. See `references/auth-patterns.md` for the four auth strategies.

## 7. UI clicks to set up test data
Use `RequestsLibrary` for data seeding. UI setup is 10-50x slower and more fragile than API calls.

**Why:** Creating a product via the admin UI takes 15+ seconds and 10+ keyword calls. An API call takes 200ms and one line. UI setup also couples your test to two features instead of one — if the admin form breaks, your unrelated cart test fails too.

**Fix:** Use `Create Session` + `POST On Session` from RequestsLibrary. See `references/api-setup-teardown.md`.

## 8. No error path tests
Every feature needs at least one failure scenario test. Cover server errors (500), network timeouts, and empty states.

**Why:** Happy-path-only suites give false confidence. The app may crash on a 500, show a blank screen on empty data, or hang on a timeout — none of which are caught without explicit error path tests.

**Fix:** Use Browser library's `Route` keyword to mock failures. At minimum: one 500 response, one aborted route (`Abort Route`), one empty state. See `references/network-interception.md`.

## 9. Hardcoded test data
NEVER embed real entity IDs (`ACC-SUB-2026-00025`), real user names (`Anas Client 73`), real monetary amounts, or environment-specific strings in test code. Instead:
- Create data via `RequestsLibrary` in `[Setup]` / `Test Setup` and capture the returned ID
- Use `Evaluate    time.time_ns()` or `Generate Random String` for uniqueness
- Read values from `%{ENV_VAR}` or a `variables.py` file
- For read-only assertions on existing data, use pattern matchers (`Get Text    ${locator}    matches    ACC-SUB-\\d{4}-\\d{5}`) instead of exact values

If you find yourself typing a specific ID or name into test code, STOP — that is a hardcoded value.

## 10. Tests depending on execution order
Each test must be independently runnable. Never rely on state left by a previous test. Robot defaults to running tests in file order within a suite — do not exploit that.

## 11. `Run Keyword And Ignore Error` hiding assertion failures
`Run Keyword And Ignore Error    Some Assertion` swallows the failure and returns `FAIL` silently, letting the test pass anyway.

**Why it's wrong:** The test reports green but never verifies anything. This is the Robot equivalent of `try/except: pass` around an assertion.

**Fix:** Only use `Run Keyword And Ignore Error` for genuine cleanup (`Run Keyword And Ignore Error    Delete Cookie    session`). Never wrap an assertion in it. If you need conditional logic, use `Run Keyword If` on a state query, not on an assertion.

## 12. `force=True` on actions without justification
`Click    <locator>    force=${True}` bypasses actionability checks and hides real problems: overlapping elements, not scrolled into view, disabled state, unmounted components.

**Fix:** Diagnose the root cause. Use `Scroll To Element`, wait for the overlay to disappear (`Wait For Elements State    role=dialog    hidden`), or wait for the target to become enabled. Only acceptable when interacting with a custom widget that the Browser library cannot natively trigger (document why in a comment next to the call).

## 13. `Sleep` after navigation instead of `Wait For Elements State` / `Wait For Response`
`Go To` triggers a page load, but subsequent keywords race with framework hydration. A common "fix" is `Sleep    3s` — this is brittle and arbitrary.

**Fix:** Wait for a concrete readiness signal. Either `Wait For Elements State    role=heading[name="Dashboard"]    visible` or `Wait For Response    matcher=**/api/bootstrap    timeout=10s`. Pick the thing you actually need to be ready.

## 14. Utility-class selectors (Tailwind, Bootstrap, etc.)
`css=.btn-primary`, `css=.rounded-lg`, `css=.flex.items-center` are styling concerns that change during refactors. Treat ALL utility framework classes as volatile — never use them as selectors. If no semantic locator works, request a `data-testid` from the dev team.

## 15. Asserting exact server-computed values
`Get Text    role=text[name="Revenue"]    ==    $12,450` will break when data changes. For dashboard counters, totals, and aggregates:
- Assert the element exists and contains a number (`Get Text    ${loc}    matches    \\$[\\d,]+`)
- Assert non-zero or within a range (`Should Be True    ${value} > 0`)
- Assert format correctness (`matches    ^\\d{1,3}(,\\d{3})*$`)
- If exact value matters, seed the data via `RequestsLibrary` first so you control the expected value
