# NOTICE

This repository packages and redistributes upstream software published by
[Amazon](https://github.com/corretto). The Apache-2.0 license in
[`LICENSE`](LICENSE) covers the OCX pipeline files authored here. It does
**not** cover any upstream-derived asset — each package's redistributed bytes
carry their own license, recorded below.

Each package's logo is reproduced for catalog identification only, under
nominative fair use. The marks remain the property of their respective owners
and no endorsement is implied.

| Package | GHCR path | Upstream SPDX |
|---|---|---|
| `corretto` | `ghcr.io/ocx-contrib/amazon/corretto` | `GPL-2.0-only WITH Classpath-exception-2.0` |

---

## `corretto`

Upstream: <https://github.com/corretto>
Published to `ghcr.io/ocx-contrib/amazon/corretto`.

| Component | SPDX | Holder |
|---|---|---|
| Amazon Corretto JDK (OpenJDK build) | **GPL-2.0-only WITH Classpath-exception-2.0** | Amazon Web Services / Oracle and the OpenJDK contributors |

The Amazon Corretto logo shipped with this package is an Amazon trademark.

No modifications are made to the upstream artifacts; they are republished
byte-for-byte inside an OCX bundle.

### Corresponding Source (GPLv2 with Classpath Exception)

Corretto ships no GitHub release assets — the binaries are fetched from
`corretto.aws/downloads` — but the complete Corresponding Source for every
mirrored version is the OpenJDK source in the per-major upstream repository, at
the matching git tag:

- JDK 8  → <https://github.com/corretto/corretto-8>
- JDK 11 → <https://github.com/corretto/corretto-11>
- JDK 17 → <https://github.com/corretto/corretto-17>
- JDK 21 → <https://github.com/corretto/corretto-21>
- JDK 25 → <https://github.com/corretto/corretto-25>

Check out the exact release tag (see the version-scheme table in
[`corretto/CATALOG.md`](corretto/CATALOG.md)); e.g. OCX version `21.0.10_7001`
→ tag `21.0.10.7.1`:

```bash
git clone https://github.com/corretto/corretto-21
git -C corretto-21 checkout 21.0.10.7.1
```

The Classpath Exception relaxes linking terms only; the source-conveyance duty
is unchanged. As required by GPLv2 §3(b), the maintainers of this mirror also
offer, valid for three years from the distribution of any given version, to
provide the complete Corresponding Source for that version on request — open an
issue at <https://github.com/ocx-contrib/mirror-amazon>. No additional
restrictions are imposed beyond the upstream license.
