---
title: Amazon Corretto
description: No-cost, production-ready OpenJDK distribution by Amazon
keywords: java,jdk,openjdk,corretto,amazon,runtime
---

# Amazon Corretto

Amazon Corretto is a no-cost, multiplatform, production-ready distribution of OpenJDK. It includes long-term support with performance enhancements and security fixes from Amazon.

## What's included

- **java** — JVM runtime
- **javac** — Java compiler
- **jar** — archive tool
- **jshell** — interactive REPL (JDK 11+)

## Available versions

- **Corretto 25** — JDK 25 (latest)
- **Corretto 21** — JDK 21 LTS
- **Corretto 17** — JDK 17 LTS
- **Corretto 11** — JDK 11 LTS
- **Corretto 8** — JDK 8 LTS

## Version scheme

Corretto tags are mapped to OCX versions as `major.minor.update_build`, where build = `jdkBuild × 1000 + correttoRevision`.

| JDK | GitHub tag format | Example tag | OCX version |
|---|---|---|---|
| 21, 25 | `major.minor.update.jdkBuild.rev` | `21.0.10.7.1` | `21.0.10_7001` |
| 17 | `major.minor.update.jdkBuild.rev` | `17.0.14.7.1` | `17.0.14_7001` |
| 11 | `major.minor.update.jdkBuild.rev` | `11.0.25.9.1` | `11.0.25_9001` |
| 8 | `major.update.jdkBuild.rev` | `8.442.06.1` | `8.0.442_6001` |

JDK 8 tags have no minor version — `minor=0` is inserted during conversion.

Use `amazon/corretto:21` for the latest JDK 21 release, or `amazon/corretto:latest` for the newest release of the highest JDK major.

## Platforms

Linux, macOS and Windows on x86-64, plus arm64 everywhere upstream ships it. Both Linux libc flavours are carried: the glibc build (`+libc.glibc`) and Amazon's separate Alpine build (`+libc.musl`). Neither is static, so the right one is selected for the host automatically.

| Platform | libc |
|---|---|
| `linux/amd64`, `linux/arm64` | `+libc.glibc` (glibc hosts) and `+libc.musl` (Alpine/musl hosts) |
| `darwin/amd64`, `darwin/arm64` | — |
| `windows/amd64` | — |

## Links

- [Amazon Corretto Documentation](https://docs.aws.amazon.com/corretto/)
- [Corretto on GitHub](https://github.com/corretto)
- [Corretto Downloads](https://aws.amazon.com/corretto/)

## License & source

The Corretto JDK binaries redistributed here are licensed
**`GPL-2.0-only WITH Classpath-exception-2.0`** (© Amazon Web Services; same
license as OpenJDK). The complete Corresponding Source for each mirrored version is the
OpenJDK source in the per-major upstream repo at the matching git tag —
`corretto/corretto-{8,11,17,21,25}` — e.g. OCX `21.0.10_7001` → `git clone
https://github.com/corretto/corretto-21 && git checkout 21.0.10.7.1` (see the
version-scheme table above for the tag mapping). A 3-year written offer for the
source is in the repository's `NOTICE.md`. The OCX mirror pipeline files are
Apache-2.0.
