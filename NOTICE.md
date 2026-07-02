# NOTICE

This repository packages and redistributes upstream [Amazon Corretto](https://github.com/corretto)
JDK binaries.

The Apache-2.0 license covers the OCX pipeline files authored here. It does
**not** cover upstream-derived assets — the Corretto JDK binaries published to
`ocx.sh/corretto` (GPLv2-with-Classpath-Exception, Amazon Web Services; the
same license as OpenJDK) and the Amazon Corretto logo (Amazon trademark, used
for catalog identification under nominative-fair-use).

## Corresponding Source (GPLv2 with Classpath Exception)

The Corretto JDK binaries redistributed here are licensed
GPLv2-with-Classpath-Exception (the same license as OpenJDK). Corretto ships no
GitHub release assets — the binaries are fetched from `corretto.aws/downloads` —
but the complete Corresponding Source for every mirrored version is the OpenJDK
source in the per-major upstream repository, at the matching git tag:

- JDK 8  → <https://github.com/corretto/corretto-8>
- JDK 11 → <https://github.com/corretto/corretto-11>
- JDK 17 → <https://github.com/corretto/corretto-17>
- JDK 21 → <https://github.com/corretto/corretto-21>
- JDK 25 → <https://github.com/corretto/corretto-25>

Check out the exact release tag (see the version-scheme table in `CATALOG.md`);
e.g. OCX version `21.0.10_7001` → tag `21.0.10.7.1`:

```bash
git clone https://github.com/corretto/corretto-21
git -C corretto-21 checkout 21.0.10.7.1
```

The Classpath Exception relaxes linking terms only; the source-conveyance duty
is unchanged. As required by GPLv2 §3(b), the maintainers of this mirror also
offer, valid for three years from the distribution of any given version, to
provide the complete Corresponding Source for that version on request — open an
issue at <https://github.com/ocx-contrib/mirror-corretto>. No additional
restrictions are imposed beyond the upstream license.
