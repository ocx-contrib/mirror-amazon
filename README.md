# mirror-corretto

OCX mirror for [Amazon Corretto](https://github.com/corretto) JDK 8, 11, 17, 21, and 25. Publishes the upstream Corretto JDK archives to `ocx.sh/corretto` with cascade tags after a smoke test per `(version, platform)`.

This repository consolidates the former monorepo `corretto-{8,11,17,21,25}` specs into a single spec. One `generate.py` emits a `url_index` covering every JDK major; a per-major patch floor (`MAJOR_FLOORS`) keeps first-run bootstrap small.

Corretto ships **no GitHub release assets** — the download URLs live in the release-notes body on the `corretto.aws` CDN, so `generate.py` scrapes them and classifies each by platform.

## Editing

| File | Edit | Regenerate after |
|------|------|------------------|
| `mirror.yml` | hand | `ocx-mirror pipeline generate ci` |
| `generate.py` | hand | — |
| `tests/smoke.star` | hand | — |
| `metadata.json`, `metadata-darwin.json`, `CATALOG.md`, `logo.*` | hand | — |
| `.github/workflows/*.yml` | generated | re-run when `mirror.yml` changes |

`generate.py` queries the GitHub releases API for each `corretto/corretto-<major>` repository (via the `ocx-mirror-sdk`) and emits a `url_index` JSON document filtered against `MAJOR_FLOORS`. Bump that map to retire older patches, or add a `(major, "corretto/corretto-<major>")` entry to `REPOS` plus a floor to mirror a new JDK major.

CI fails on drift via `ocx-mirror pipeline generate ci --check`.

## Required secrets

| Secret | Use |
|--------|-----|
| `OCX_MIRROR_REGISTRY_TOKEN` + `OCX_MIRROR_REGISTRY_USER` | `ocx package push` to `ocx.sh` |
| `OCX_MIRROR_DISCORD_HOOK` | notify-stage Discord webhook URL |

(Inherited from the `ocx-contrib` org with visibility ALL.)

## License

Apache-2.0 — see [`LICENSE`](LICENSE). Upstream assets (Amazon Corretto logo, mirrored JDK binaries) are out of scope; see [`NOTICE.md`](NOTICE.md).
