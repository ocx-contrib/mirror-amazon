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

# Tier 4: JAVA_HOME wiring. metadata.json declares JAVA_HOME as a constant
# pointing at the install root; confirm it is set and resolves under the
# package root (value differs per platform layout, so assert the wiring,
# not a literal path).
java_home = ocx.env("JAVA_HOME")
expect.ne(java_home, None)
expect.contains(java_home, ocx.package_root)
