# mirror-amazon

OCX mirrors for [Amazon](https://github.com/corretto) tooling. Each package
publishes to `ghcr.io/ocx-contrib/amazon/<package>` with cascade tags after a
smoke test per `(version, platform)`, then announces the result into the OCX
index as `ocx.sh/amazon/<package>`.

| Package | Upstream | Index name | Upstream SPDX |
|---|---|---|---|
| [`corretto/`](corretto/) | [corretto](https://github.com/corretto) | `ocx.sh/amazon/corretto` | `GPL-2.0-only WITH Classpath-exception-2.0` |

`corretto/` mirrors JDK majors **8, 11, 17, 21, 25, 26 and 27** from one spec.
Corretto ships **no GitHub release assets** — the download URLs live in the
release-notes body on the `corretto.aws` CDN, so `corretto/scripts/generate.py`
scrapes them, classifies each by platform and emits a `url_index`.

**Which majors are mirrored is decided only by `REPOS` in that script.** The
spec carries no `versions.max` on purpose: it is an *exclusive* bound, so it
would have to be bumped in lockstep, and a `url_index` version outside the
window is silently not resolved rather than reported — the drift would be
invisible. Adding a major is therefore two edits in one file:

1. a `(major, "corretto/corretto-<major>")` entry in `REPOS`, and
2. a `MAJOR_FLOORS` entry — **without one the major is skipped wholesale**,
   because `below_floor` returns `True` on a missing floor. Floor a brand-new
   major open (`(N, 0, 0, 0, 0)`); floor an existing one at its first
   non-prerelease so first-run bootstrap stays small.

Then add it to the Corresponding Source list in [`NOTICE.md`](NOTICE.md) — GPLv2
§3 requires a source pointer for every major whose binaries are conveyed.

`corretto/corretto-27` is listed but has published **no releases** upstream as
of 2026-08-03; it contributes nothing until Amazon ships it, then lands with no
further edit.

> `amazon/corretto:latest` follows the **highest** major, which is now 26 — a
> non-LTS feature release. Pin `:25`, `:21`, `:17`, `:11` or `:8` for an LTS
> line.

## Layout

One directory per package. Everything a package owns — its spec, metadata,
catalog entry, logo, generator and smoke test — lives in its own directory, so
adding a package renames nothing and editing one never triggers another's CI.

```
mirror-base.yml         repo-wide policy (see below)
<package>/
├── mirror.yml          the spec — never at the repo root
├── metadata.json       bundle interface (+ metadata-<platform>.json overrides)
├── CATALOG.md          → ocx package describe
├── logo.svg / logo.png describe assets, 512px PNG
├── scripts/            url_index generator
└── tests/smoke.star    Starlark smoke test
```

`LICENSE` and `NOTICE.md` are shared at the root. Logos are **not** — a
repo-root `logo.*` sits in no workflow's `paths:` filter, so replacing it would
publish nothing until some unrelated edit happened to fire.

### `mirror-base.yml`

Repo-wide policy: `skip_prereleases`, `cascade`, `build_timestamp`,
`concurrency`, the platform/container matrix and `notify`. It is **not a spec** —
it has no `name`/`target`/`source` and is never loaded on its own. Each package
opens with `extends: ../mirror-base.yml`.

⚠️ `extends:` is a **shallow merge** of top-level keys. A spec that restates
`platforms:` to change one runner drops every `containers:` entry with it, and
nothing reds — the legs simply stop existing, and every `os.features` claim goes
back to being asserted rather than verified. Restate a block in full or not at
all.

## Platforms

`corretto` publishes **seven** platform entries. Upstream ships a glibc Linux
build and a separate musl (Alpine) build for each Linux arch:

| Key | Asset | Requires | Container legs |
|---|---|---|---|
| `linux/{amd64,arm64}+libc.glibc` | `amazon-corretto-<ver>-linux-<arch>.tar.gz` | a glibc loader | `ubuntu:24.04`, `fedora:40` |
| `linux/{amd64,arm64}+libc.musl` | `amazon-corretto-<ver>-alpine-linux-<arch>.tar.gz` | a musl loader | `alpine:3.20` |
| `darwin/{amd64,arm64}` | `amazon-corretto-<ver>-macosx-<arch>.tar.gz` | — | — |
| `windows/amd64` | `amazon-corretto-<ver>-windows-x64-jdk.zip` | — | — |

`os.features` states what an artifact **requires of the host**, not how it was
built. **Neither** Linux build is static — each names its own loader in
`PT_INTERP` — so neither covers the other and both keys carry an explicit libc
feature. (A bare key would be right only for a fully static build.) The
container legs are what turn those claims into evidence: an alpine leg on a
glibc key would red on a correct artifact, and vice versa. The measurement
behind each key is recorded above the `assets:` block in `corretto/mirror.yml`.

There is no `windows/arm64`: upstream ships `windows-x64` and (JDK 8 only)
`windows-x86`, and nothing else.

> **Asset-naming trap.** The versioned CDN filenames put `alpine` *before*
> `linux`, so `.*-linux-x64\.tar\.gz$` matches the Alpine tarball too — as does
> `amazon-corretto-debugsymbols-<ver>-linux-x64.tar.gz`. Both the spec regexes
> (`[^-]+` pins the wildcard to the dotted version segment) and the generator
> (negative lookbehind plus an explicit `debugsymbols` exclusion) guard against
> that. `uv run scripts/generate.py --self-check` asserts it.

## Editing

| File | Edit | Regenerate after |
|------|------|------------------|
| `<package>/mirror.yml`, `mirror-base.yml` | hand | yes — see below |
| `<package>/{metadata*.json,CATALOG.md,logo.*}` | hand | — |
| `<package>/tests/smoke.star`, `<package>/scripts/*` | hand | — |
| `.github/workflows/*.yml` | **generated** | re-run when a spec changes |

```bash
ocx-mirror package pipeline generate ci --spec corretto/mirror.yml
```

**Name every spec.** `--spec` *appends* rather than replaces, so a command
naming a subset silently stops rendering the rest while staying green — and the
drift guard reds on a generated workflow the current spec set no longer
produces.

Never hand-edit `.github/workflows/`. `verify-generated.yml` exits 65 on any
drift; if a generated workflow is wrong, the spec or the template is wrong.

Run `direnv allow` once to put the pinned toolchain on `PATH`, and invoke
`ocx-mirror` directly — never `ocx run -- ocx-mirror`, which pins
`OCX_BINARY_PIN` to the bootstrap `ocx` and false-reds the nested push.

## Required secrets

| Secret | Use |
|--------|-----|
| `OCX_ANNOUNCE_TOKEN` | opens the index pull request from the `ocx-contrib/index` fork |
| `OCX_MIRROR_DISCORD_HOOK` | notify-stage Discord webhook URL |

(Inherited from the `ocx-contrib` org with visibility ALL. GHCR pushes use the
run's own `GITHUB_TOKEN` — no registry secret needed.)

## License

Apache-2.0 — see [`LICENSE`](LICENSE). Upstream assets are out of scope; each
package's redistribution license is recorded in [`NOTICE.md`](NOTICE.md).
