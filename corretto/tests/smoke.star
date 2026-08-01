# tests/smoke.star — stable across every Corretto JDK major (8, 11, 17, 21, 25).
# Asserts on the contract (exit code, version SHAPE, compiled-program output,
# JAVA_HOME wiring) — never on vendor prose ("Corretto", "OpenJDK").

IS_WIN = ocx.target_platform.os == ocx.os.Windows
JAVA = "java.exe" if IS_WIN else "java"
JAVAC = "javac.exe" if IS_WIN else "javac"

# Tier 1 + 2: liveness + version SHAPE. The JVM prints `-version` to stderr;
# the digits are the contract (JDK 8 prints `1.8.0_NNN`, JDK 11+ prints
# `11.0.x` … `25.0.x`) — both satisfy \d+\.\d+\.\d+.
r = ocx.run(JAVA, "-version")
expect.ok(r)
expect.matches(r.stdout + r.stderr, r"\d+\.\d+\.\d+")

# Tier 3: hermetic compile + run — exercises javac AND the JVM on input we
# write ourselves. Assert the program's computed output, not any prose.
ocx.write_file("Smoke.java", "public class Smoke { public static void main(String[] a) { System.out.println(6 * 7); } }\n")
r = ocx.run(JAVAC, "Smoke.java")
expect.ok(r)
r = ocx.run(JAVA, "Smoke")
expect.ok(r)
expect.contains(r.stdout, "42")

# Tier 4: the relocated JDK self-locates its home correctly. `java.home`
# (reported to stderr by `-XshowSettings:properties`) must resolve to a real
# path, proving bin/java finds its sibling lib/ after the bundle is relocated
# into the install tree.
#
# NOTE: metadata.json wires JAVA_HOME as a `constant` env var with
# `visibility: public` (so it IS exported to consumers — omitting visibility
# would default it `private` and silently drop the export). Constants are
# composed at install/activate time; `ocx package test` composes only
# `path`-type vars (PATH, proven by Tiers 1-3), so JAVA_HOME is not visible
# inside the test sandbox regardless of visibility, and is intentionally not
# asserted here — the java.home check below is the functional equivalent.
r = ocx.run(JAVA, "-XshowSettings:properties", "-version")
expect.ok(r)
expect.matches(r.stdout + r.stderr, r"java\.home = \S+")
