"""
Build script -- package the sticky notes app into a standalone EXE.

Usage:
    python build.py

Requires: PyInstaller (pip install pyinstaller)
"""

import os
import shutil
import subprocess
import sys


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PROJECT_DIR, "dist")
BUILD_DIR = os.path.join(PROJECT_DIR, "build")
SPEC_FILE = os.path.join(PROJECT_DIR, "StickyNotesTodo.spec")
OUTPUT_EXE = os.path.join(DIST_DIR, "StickyNotesTodo.exe")


def clean_build():
    """Remove previous build artifacts."""
    for d in [DIST_DIR, BUILD_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
    if os.path.exists(SPEC_FILE):
        os.remove(SPEC_FILE)


def build_exe():
    """Run PyInstaller to build the EXE."""
    print("=" * 60)
    print("  Building StickyNotesTodo.exe ...")
    print("=" * 60)

    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",               # Single EXE
        "--windowed",              # No console window
        "--name", "StickyNotesTodo",
        "--distpath", DIST_DIR,
        "--workpath", BUILD_DIR,
        "--specpath", PROJECT_DIR,
        "--noconfirm",
    ]

    # Try to find an icon file
    icon_path = os.path.join(PROJECT_DIR, "icon.ico")
    if os.path.exists(icon_path):
        pyinstaller_args.extend(["--icon", icon_path])

    # Main script
    pyinstaller_args.append(os.path.join(PROJECT_DIR, "main.py"))

    result = subprocess.run(pyinstaller_args, cwd=PROJECT_DIR)
    if result.returncode != 0:
        print("\n[FAIL] Build failed!")
        sys.exit(1)

    # Verify output
    if os.path.exists(OUTPUT_EXE):
        size_mb = os.path.getsize(OUTPUT_EXE) / (1024 * 1024)
        print("\n[SUCCESS] Build successful!")
        print("   Output: " + OUTPUT_EXE)
        print("   Size: %.1f MB" % size_mb)
    else:
        print("\n[FAIL] Output EXE not found!")
        sys.exit(1)


def main():
    clean_build()
    build_exe()
    # Clean up build artifacts (keep only the EXE)
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    if os.path.exists(SPEC_FILE):
        os.remove(SPEC_FILE)


if __name__ == "__main__":
    main()
