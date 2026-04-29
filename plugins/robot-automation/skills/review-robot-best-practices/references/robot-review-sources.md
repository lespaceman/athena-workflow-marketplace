# Robot Review Source Notes

Use these notes when reviewing Robot Framework and Python automation best practices.

## Primary Sources

- Robot Framework User Guide 7.4: https://robotframework.org/robotframework/7.4/RobotFrameworkUserGuide.html
- Robot Framework Style Guide: https://docs.robotframework.org/docs/style_guide
- Robocop documentation: https://robocop.dev/stable/
- Robot Framework Browser library: https://github.com/MarketSquare/robotframework-browser

## Source-Backed Review Anchors

- Robot Framework is keyword-driven and supports reusable higher-level keywords, variables, tagging, setup/teardown, data-driven tests, and Python-native custom libraries. Review whether suites use these mechanisms to keep tests readable and modular.
- Resource files should normally use the `.resource` extension. `.robot`, `.txt`, and `.tsv` can work for compatibility, but `.resource` communicates intent more clearly.
- Keyword name resolution is case, space, and underscore insensitive for the keyword part. Review for near-duplicate keyword or variable names that look different but resolve the same or create ambiguity.
- Timeouts can stop a hanging keyword, but Robot documentation warns that forcefully stopping keywords can leave the library, environment, or system under test unstable. Prefer library-level timeouts, readiness checks, and bounded waits over broad timeouts as the primary stability strategy.
- The Python library API supports static, dynamic, and hybrid libraries. Static libraries are usually simplest. Dynamic or hybrid APIs should have a clear reason.
- The `robot.api.deco.library` decorator disables automatic keyword discovery by default, requiring `@keyword` on exposed methods. This is useful for preventing helper methods from accidentally becoming Robot keywords.
- The style guide recommends clear section order, left-aligned section headers, 4-space token separation, limited nesting, 120-character line length, no trailing whitespace, and scope-aware variable casing.

## Common Review Smells

- `.robot` suites with a large `*** Keywords ***` section instead of shared `.resource` files.
- Tests that interact with the UI but never assert the resulting state.
- Keywords that hide failures with `Run Keyword And Ignore Error`, broad retry wrappers, or boolean return values that callers do not assert.
- `Sleep` or arbitrary polling where Browser/Selenium/API libraries provide condition-based waits.
- Global variables or Python module-level state used as cross-test scratch space.
- Hardcoded credentials, domains, tokens, timestamps, generated IDs, or environment-specific paths.
- Python custom libraries exposing helper methods as keywords accidentally.
- Python keywords that catch all exceptions and return status strings instead of failing clearly.
- Excessive abstraction: keywords that read like generic programming helpers instead of domain actions.
- Under-abstraction: repeated login/setup/navigation steps in every test.
