# Tracker Template: e2e-tracker.md

Use this as a starting template when creating the tracker file. Adapt sections as needed.

---

```markdown
# E2E Test Tracker

## Goal

- **URL:** https://myapp.com/checkout
- **Feature:** Checkout flow with cart, shipping, and payment
- **Slug:** checkout

## Progress

### Session 1 — 2026-04-01

- Analyzed codebase: Playwright 1.42, TypeScript, existing auth fixture in `tests/fixtures/auth.ts`
- Browsed checkout flow: 4-step wizard (cart review, shipping, payment, confirmation)
- Discovered 3 form validation states per step
- Generated test spec: `test-cases/checkout.md` with TC-CHECKOUT-001 through TC-CHECKOUT-012
- Review gate passed with warnings (TC-CHECKOUT-008 needs clarification on coupon edge case)

### Session 2 — 2026-04-02

- Wrote `tests/checkout.spec.ts` covering TC-CHECKOUT-001 through TC-CHECKOUT-012
- Code review gate passed
- Ran tests: 10/12 passing, 2 failing (TC-CHECKOUT-006: selector stale, TC-CHECKOUT-011: timeout)
- Fixed TC-CHECKOUT-006: updated selector from `.price` to `[data-testid="cart-total"]`
- Fixed TC-CHECKOUT-011: added `waitForResponse` before assertion

## Remaining

- Re-run full suite to confirm fixes
- Verify TC-ID coverage: all 12 specs should map to test code

## Next Steps

- Run `npx playwright test tests/checkout.spec.ts --reporter=list` and record output
- If all green, mark complete
- If failures remain, diagnose with `fix-flaky-tests` skill

<!-- E2E_COMPLETE -->
```

---

**Terminal markers** (write as the last line of the tracker when appropriate):

- `<!-- E2E_COMPLETE -->` — all tests pass, all TC-IDs covered, work is done
- `<!-- E2E_BLOCKED: reason -->` — unrecoverable blocker prevents further progress (e.g., `<!-- E2E_BLOCKED: login requires 2FA token we cannot automate -->`)
