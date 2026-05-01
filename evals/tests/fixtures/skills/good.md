---
name: define-regression-scope
description: >
  Use to define impact-based regression scope for a release, hotfix, changed area, or risky
  feature: decide what should be rerun beyond smoke, why it belongs in regression, and how deep
  each area should go. Triggers include "regression scope for...", "what should we rerun after
  this change", "what belongs in release regression", "impact-based rerun plan", "high-risk
  regression plan", "what's beyond smoke", or "pre-release regression checklist". This skill owns
  regression intent, included areas, and rerun depth; it does NOT own live exploration, shared
  coverage planning, detailed TC-ID specs, or framework-specific automation.
license: MIT
---

# Define Regression Scope

Define a practical rerunnable regression charter from change, risk, and business criticality.

## Boundaries

This skill does:

- define rerunnable regression areas
- explain why each area is included
- recommend rerun depth

This skill does not:

- explore live apps
- write coverage plans
- generate test case specs
