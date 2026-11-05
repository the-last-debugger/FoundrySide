"""Build a debug APK without Gradle, using the SDK build-tools directly.

Gradle is not installed here and downloading a distribution would be a large, unnecessary dependency.
The build-tools can do the whole job: `aapt2` links the manifest and assets, `javac` compiles one
activity against `android.jar`, `d8` produces the dex, and `apksigner` signs it with a local debug key.

    python scripts/build_apk.py

Writes app/android/build/foundryside.apk and reports its size and signature status.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "app" / "android"
BUILD = ANDROID / "build"
ASSETS = ANDROID / "assets"
SRC = ANDROID / "src"
MANIFEST = ANDROID / "AndroidManifest.xml"

SDK = Path(os.environ.get("ANDROID_SDK_ROOT") or
           Path(os.environ["LOCALAPPDATA"]) / "Android" / "Sdk")
# 34.0.0 ships a d8 that crashes on Java 17 class files with the JDK 25 javac; 37.0.0 handles them.
BUILD_TOOLS = "37.0.0"
BT = SDK / "build-tools" / BUILD_TOOLS
ANDROID_JAR = SDK / "platforms" / "android-34" / "android.jar"
JDK_BIN = Path(r"C:\Program Files\Java\jdk-25\bin")


def tool(name: str) -> str:
    for candidate in (BT / f"{name}.exe", BT / f"{name}.bat", JDK_BIN / f"{name}.exe",
                      BT / name):
        if Path(candidate).exists():
            return str(candidate)
    found = shutil.which(name)
    if found:
        return found
    raise SystemExit(f"required tool not found: {name}")


def run(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    result = subprocess.run(args, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        print(f"FAILED: {' '.join(str(a) for a in args[:3])} ...")
        print((result.stdout or "")[-1500:])
        print((result.stderr or "")[-1500:])
        raise SystemExit(1)
    return result


def main() -> int:
    for required, label in ((ANDROID_JAR, "android.jar"), (MANIFEST, "manifest")):
        if not Path(required).exists():
            raise SystemExit(f"missing {label}: {required}")

    if BUILD.exists():
        shutil.rmtree(BUILD)
    (BUILD / "classes").mkdir(parents=True)

    # 1. Compile the activity against the platform jar.
    sources = [str(p) for p in SRC.rglob("*.java")]
    javac = tool("javac")
    run([javac, "--release", "17", "-classpath", str(ANDROID_JAR), "-d", str(BUILD / "classes"),
         *sources])

    # 2. Dex it.
    class_files = [str(p) for p in (BUILD / "classes").rglob("*.class")]
    run([tool("d8"), "--lib", str(ANDROID_JAR), "--min-api", "24", "--output", str(BUILD),
         *class_files])

    # 3. Link resources, manifest and assets into an unsigned APK.
    unsigned = BUILD / "unsigned.apk"
    run([tool("aapt2"), "link", "-o", str(unsigned), "-I", str(ANDROID_JAR),
         "--manifest", str(MANIFEST), "-A", str(ASSETS),
         "--min-sdk-version", "24", "--target-sdk-version", "34",
         "--version-code", "1", "--version-name", "0.1"])

    # 4. Add classes.dex. aapt2 links assets but not code, so the dex is zipped in afterwards.
    with zipfile.ZipFile(unsigned, "a", zipfile.ZIP_DEFLATED) as archive:
        archive.write(BUILD / "classes.dex", "classes.dex")

    # 5. Align, sign, verify.
    aligned = BUILD / "aligned.apk"
    run([tool("zipalign"), "-f", "4", str(unsigned), str(aligned)])

    keystore = ANDROID / "debug.keystore"
    if not keystore.exists():
        run([tool("keytool"), "-genkeypair", "-keystore", str(keystore), "-storepass",
             "android", "-keypass", "android", "-alias", "androiddebugkey",
             "-dname", "CN=Android Debug,O=Android,C=US", "-keyalg", "RSA", "-keysize", "2048",
             "-validity", "10000"])

    final = BUILD / "foundryside.apk"
    run([tool("apksigner"), "sign", "--ks", str(keystore), "--ks-pass", "pass:android",
         "--key-pass", "pass:android", "--ks-key-alias", "androiddebugkey",
         "--out", str(final), str(aligned)])

    verify = run([tool("apksigner"), "verify", "--verbose", str(final)])

    size_kb = final.stat().st_size / 1024
    print(f"built {final.relative_to(ROOT)} ({size_kb:.0f} KB)")
    for line in (verify.stdout or "").splitlines():
        if line.startswith(("Verifies", "Verified using")):
            print(f"  {line.strip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
