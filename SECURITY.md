# Security Policy

## Supported Versions

The latest released version is supported. See [`CHANGELOG.md`](CHANGELOG.md) for releases.

## Reporting a Vulnerability

This repo is a marketplace index; it contains no executable code itself, but it
directs Claude Code to **clone and install plugins** from the referenced repos. If
you find an issue — for example an entry pointing at an unexpected or malicious
source — please report it privately:

- Open a [GitHub security advisory](https://github.com/avegancafe/avegancafe-marketplace/security/advisories/new), or
- Contact the maintainer directly rather than filing a public issue.

Please do not disclose the issue publicly until it has been addressed.

## Scope notes

- Verify every `source.url` points at an expected `avegancafe/*` repo over SSH.
- The actual plugin code lives in the referenced repos — review their own
  `SECURITY.md` for plugin-level concerns.
