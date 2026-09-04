# Changelog

## 0.1.4

- Re-release. Version `0.1.3` was version-bumped and committed on `main` but never
  reached npm: the release run's publish step aborted on an unrelated new package
  (`@athenaflow/plugin-sentry`) that the CI token could not create, and this plugin,
  queued behind it in the same loop, was never attempted. The publish loop is now
  resilient to a single plugin's failure, so this version publishes on its own.
