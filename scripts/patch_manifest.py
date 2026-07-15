#!/usr/bin/env python3
"""Patch the generated AndroidManifest.xml for Android TV.

Adds:
  - INTERNET + ACCESS_NETWORK_STATE permissions
  - touchscreen (required=false) and leanback (required=false) features
  - LEANBACK_LAUNCHER category alongside the existing LAUNCHER

Idempotent: safe to run more than once.
"""
import sys

def main():
    if len(sys.argv) < 2:
        print("usage: patch_manifest.py <path-to-AndroidManifest.xml>")
        sys.exit(1)
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()

    perms = (
        '    <uses-permission android:name="android.permission.INTERNET" />\n'
        '    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />\n'
        '    <uses-feature android:name="android.hardware.touchscreen" android:required="false" />\n'
        '    <uses-feature android:name="android.software.leanback" android:required="false" />\n'
    )
    if "android.software.leanback" not in s:
        s = s.replace("<application", perms + "\n    <application", 1)

    if "LEANBACK_LAUNCHER" not in s:
        s = s.replace(
            '<category android:name="android.intent.category.LAUNCHER" />',
            '<category android:name="android.intent.category.LAUNCHER" />\n'
            '                <category android:name="android.intent.category.LEANBACK_LAUNCHER" />',
            1,
        )

    open(p, "w", encoding="utf-8").write(s)
    print("Manifest patched for Android TV.")

if __name__ == "__main__":
    main()
