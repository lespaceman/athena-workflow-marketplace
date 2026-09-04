# Changelog

## 0.1.2

- First release to reach npm. Version `0.1.1` was version-bumped and committed on
  `main` but never published: the CI npm token had no write access to the
  `@athenaflow` scope, so `npm publish` returned a 404 on PUT. With scope access
  restored and the publish pipeline hardened (resilient loop, publish-before-commit),
  this is the initial published release of the plugin.
