# Scaffolding Playwright from Boilerplate

If Playwright is not set up in the target project, follow this procedure:

1. Clone `git@github.com:lespaceman/playwright-typescript-e2e-boilerplate.git` into a temporary directory.
2. Copy config, fixtures, pages, and utils into the project. Do not overwrite existing files.
3. Update `baseURL` to the target URL and remove example tests.
   - **Test execution strategy:** If the project needs role-based or category-based test filtering, configure it via Playwright `--grep` tags or file naming conventions (`*.admin.spec.ts`), NOT via `testIgnore` regex patterns. A `testIgnore` regex becomes a maintenance trap — every new test file requires updating the regex. If the boilerplate includes a `testIgnore` regex, replace it with tag-based filtering.
4. Merge devDependencies into `package.json`.
5. Run `npm install && npx playwright install --with-deps chromium`.
6. Clean up the temp clone.
7. Preserve the important scaffolding decisions in your working notes.
