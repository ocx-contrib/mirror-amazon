# /// script
# requires-python = ">=3.13"
# dependencies = ["ocx-mirror-sdk"]
#
# [tool.uv.sources]
# ocx-mirror-sdk = { url = "https://github.com/ocx-sh/ocx-mirror-sdk/releases/download/v0.5.2/ocx_mirror_sdk-0.5.2-py3-none-any.whl" }
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 The OCX Authors
"""Generate url_index JSON for Amazon Corretto releases.

Single generator drives all mirrored JDK majors (8, 11, 17, 21, 25). The
consolidated index replaces the former per-major monorepo specs
(corretto-8 … corretto-25). Each major lives in its own upstream GitHub
repository (corretto/corretto-<major>); they are fetched independently and
their normalized OCX versions are emitted into one combined index.

Corretto releases ship **no GitHub release assets** — the download URLs
live in the release-notes body on the corretto.aws CDN. We scrape those
URLs with the SDK's ``extract_urls`` helper (same approach as the former
monorepo generator), then classify each by platform.

Per-major patch floor is hard-coded in ``MAJOR_FLOORS`` so a fresh mirror
does not bootstrap historical patches all the way back to each major's
first release. Bump those floors to retire older patches.

Cascade safety: each major's GitHub tag space is disjoint (an `8.x` tag
never collides with an `11.x`/`17.x`/`21.x`/`25.x` tag), and the OCX
version always carries the JDK major as its leading component
(`8.0.*`, `11.0.*`, …). Cascade tags (`X.Y.Z → X.Y → X → latest`) are
therefore per-major-safe: `corretto:8`, `corretto:11`, … never alias one
another, and `corretto:latest` tracks the highest JDK major.
"""

from __future__ import annotations

import re
import sys

from ocx_mirror_sdk import IndexBuilder, github
from ocx_mirror_sdk.text import extract_urls

# (jdk_major, "owner/repo")
REPOS: list[tuple[int, str]] = [
    (8, "corretto/corretto-8"),
    (11, "corretto/corretto-11"),
    (17, "corretto/corretto-17"),
    (21, "corretto/corretto-21"),
    (25, "corretto/corretto-25"),
]

# Per-major patch floor (compared against the upstream Corretto tag tuple).
# Versions below this are skipped so a fresh mirror does not bootstrap
# historical patches. Bump these when retiring older patches.
#
# Format: <jdk_major>: (tuple of leading tag components to compare, inclusive)
# JDK 8 tags are 4-part (major.update.jdkBuild.rev); 11+ are 5-part
# (major.minor.update.jdkBuild.rev). The floor tuple is compared component
# by component against the parsed tag, so it must match the tag arity.
MAJOR_FLOORS: dict[int, tuple[int, ...]] = {
    8: (8, 452, 9, 1),
    11: (11, 0, 26, 4, 1),
    17: (17, 0, 13, 11, 1),
    21: (21, 0, 5, 11, 1),
    25: (25, 0, 0, 36, 1),
}

# Sidecars and non-portable artifacts to exclude: signatures, checksums,
# OS installers (deb/rpm/pkg/msi), JRE-only, jmods, headful, and the
# `amazon-corretto-debugsymbols-*` tarballs — those share every platform suffix
# with the real JDK tarball and would otherwise classify as a JDK.
EXCLUDE_RE = re.compile(
    r"\.(deb|rpm|pkg|msi)$"
    r"|-debugsymbols-|-jre-|-headful-|-jmods-"
    r"|\.sig$|\.md5$|\.sha256$|\.sha256sum$|\.asc$|\.minisig$"
)

# Platform patterns: anchored on the asset filename suffix → platform key.
# windows-x86 (32-bit, JDK 8 only) is intentionally unmatched — no OCX
# platform for it.
#
# The Alpine (musl) tarballs are named `-alpine-linux-<arch>.tar.gz`, so the
# glibc suffix `-linux-<arch>.tar.gz` is a substring of the musl one. The
# negative lookbehind is what keeps the glibc pattern from swallowing the
# Alpine asset; without it, classification would depend on the order URLs
# happen to appear in the release-notes body.
#
# Both Linux builds are dynamically linked against their own loader (neither is
# static), so both keys carry an explicit libc feature — see the measurement
# recorded above `assets:` in mirror.yml.
PLATFORM_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?<!-alpine)-linux-x64\.tar\.gz$"), "linux/amd64+libc.glibc"),
    (re.compile(r"(?<!-alpine)-linux-aarch64\.tar\.gz$"), "linux/arm64+libc.glibc"),
    (re.compile(r"-alpine-linux-x64\.tar\.gz$"), "linux/amd64+libc.musl"),
    (re.compile(r"-alpine-linux-aarch64\.tar\.gz$"), "linux/arm64+libc.musl"),
    (re.compile(r"-macosx-x64\.tar\.gz$"), "darwin/amd64"),
    (re.compile(r"-macosx-aarch64\.tar\.gz$"), "darwin/arm64"),
    (re.compile(r"-windows-x64-jdk\.zip$"), "windows/amd64"),
]

# Every declared platform in mirror.yml. A version is mirrored only if it ships
# all of these (see the skip in main()); partial Linux-only re-release builds are
# dropped so no test leg is left without a bundle.
REQUIRED_PLATFORMS = frozenset(p for _, p in PLATFORM_PATTERNS)


def log(message: str) -> None:
    sys.stderr.write(f"generate: {message}\n")


def parse_tag(tag: str) -> tuple[int, ...] | None:
    """Parse a Corretto tag into an int tuple, or None if it doesn't parse."""
    try:
        return tuple(int(p) for p in tag.split("."))
    except ValueError:
        return None


def below_floor(major: int, nums: tuple[int, ...]) -> bool:
    """Return True when the parsed tag is below this major's configured floor."""
    floor = MAJOR_FLOORS.get(major)
    if floor is None:
        return True
    return nums < floor


def corretto_to_ocx(nums: tuple[int, ...], major: int) -> str | None:
    """Convert a parsed Corretto tag to an OCX version string.

    All JDK versions normalize to 5 parts
    (major.minor.update.jdkBuild.correttoRev) then map to
    ``major.minor.update_jdkBuild*1000+correttoRev``.

    JDK 8 tags have 4 parts (no minor) — minor is inserted as 0.
    """
    if major == 8 and len(nums) == 4:
        nums = (nums[0], 0, nums[1], nums[2], nums[3])

    if len(nums) != 5:
        return None

    maj, minor, update, jdk_build, corretto_rev = nums
    build = jdk_build * 1000 + corretto_rev
    return f"{maj}.{minor}.{update}_{build}"


def classify_url(url: str) -> str | None:
    """Return the platform key for a URL, or None if it should be skipped."""
    if EXCLUDE_RE.search(url):
        return None
    for pattern, platform in PLATFORM_PATTERNS:
        if pattern.search(url):
            return platform
    return None


def self_check() -> int:
    """Assert the asset classification against real 21.0.12.8.1 filenames.

    Run with `uv run scripts/generate.py --self-check`. Guards the two things
    that silently mis-mirror rather than red: the alpine/glibc suffix overlap,
    and the debugsymbols tarballs that share every platform suffix.
    """
    base = "https://corretto.aws/downloads/resources/21.0.12.8.1/amazon-corretto-"
    expected = {
        "21.0.12.8.1-linux-x64.tar.gz": "linux/amd64+libc.glibc",
        "21.0.12.8.1-linux-aarch64.tar.gz": "linux/arm64+libc.glibc",
        "21.0.12.8.1-alpine-linux-x64.tar.gz": "linux/amd64+libc.musl",
        "21.0.12.8.1-alpine-linux-aarch64.tar.gz": "linux/arm64+libc.musl",
        "21.0.12.8.1-macosx-x64.tar.gz": "darwin/amd64",
        "21.0.12.8.1-macosx-aarch64.tar.gz": "darwin/arm64",
        "21.0.12.8.1-windows-x64-jdk.zip": "windows/amd64",
        # Everything below must classify as None.
        "debugsymbols-21.0.12.8.1-linux-x64.tar.gz": None,
        "debugsymbols-21.0.12.8.1-alpine-linux-aarch64.tar.gz": None,
        "21.0.12.8.1-linux-x64.tar.gz.sig": None,
        "21.0.12.8.1-windows-x64.msi": None,
        "8.502.07.1-windows-x86-jdk.zip": None,
        "8.502.07.1-windows-x64-jre.zip": None,
    }
    for name, want in expected.items():
        got = classify_url(base + name)
        assert got == want, f"{name}: expected {want}, got {got}"

    assert set(expected.values()) - {None} == REQUIRED_PLATFORMS
    assert corretto_to_ocx((21, 0, 12, 8, 1), 21) == "21.0.12_8001"
    assert corretto_to_ocx((8, 502, 7, 1), 8) == "8.0.502_7001"
    log(f"self-check ok — {len(expected)} filenames")
    return 0


def main() -> int:
    index = IndexBuilder()
    skipped_below_floor = 0

    for major, repo in REPOS:
        log(f"fetching releases for {repo} (JDK {major})")
        releases = list(
            github.list_releases(
                repo,
                include_prereleases=False,
                include_drafts=False,
            )
        )
        log(f"  got {len(releases)} releases")

        for release in releases:
            nums = parse_tag(release.tag_name)
            if nums is None:
                log(f"  skip {release.tag_name} (unparseable tag)")
                continue
            if below_floor(major, nums):
                skipped_below_floor += 1
                continue

            ocx_version = corretto_to_ocx(nums, major)
            if ocx_version is None:
                log(f"  skip {release.tag_name} (unexpected tag arity)")
                continue

            # Corretto ships no GitHub release assets; the download URLs are
            # in the release-notes body on the corretto.aws CDN.
            urls = extract_urls(release.body, pattern=r"corretto\.aws/downloads")

            by_platform: dict[str, str] = {}
            for url in urls:
                platform = classify_url(url)
                if platform is None:
                    continue
                by_platform.setdefault(platform, url)

            # Mirror a version only when it ships EVERY declared platform. Corretto
            # occasionally publishes Linux-only re-release builds (e.g. 21.0.9.11.1
            # alongside the full 21.0.9.10.1) whose macOS/Windows tarballs simply do
            # not exist on the CDN. Mirroring such a partial version would leave the
            # darwin/windows test legs with no bundle (exit 74) and red the run. The
            # full build of each (major.minor.update) is retained; only the partial
            # re-release is skipped.
            missing = REQUIRED_PLATFORMS - set(by_platform)
            if missing:
                log(
                    f"  skip {release.tag_name} -> {ocx_version} "
                    f"(incomplete coverage; missing {sorted(missing)})"
                )
                continue

            assets = {url.rsplit("/", 1)[-1]: url for url in by_platform.values()}

            log(f"  {release.tag_name} -> {ocx_version} ({len(assets)} assets)")
            index.add_version(ocx_version, assets=assets, prerelease=False)

    if skipped_below_floor:
        log(f"skipped {skipped_below_floor} releases below per-major floor")

    if len(index) == 0:
        log("no versions generated — check tag format or GitHub API response")
        return 1

    log(f"done — {len(index)} versions total")
    index.emit()
    return 0


if __name__ == "__main__":
    sys.exit(self_check() if "--self-check" in sys.argv[1:] else main())
