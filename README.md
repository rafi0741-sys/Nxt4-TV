# Streamline TV — Xtream IPTV player for Android TV

A standalone Android TV app that plays Xtream Codes IPTV accounts (Live / Movies / Series), with full D-pad remote navigation. Built by wrapping a single-page web app in Capacitor.

Streams load **inside the native WebView**, so the CORS limitation of the browser version is gone.

---

## What's in here

```
streamline-tv/
├── www/index.html          The whole app (TV-adapted: D-pad nav, TV-safe sizing)
├── capacitor.config.json   Cleartext + mixed-content enabled (for http:// servers)
├── package.json
├── .github/workflows/build-apk.yml   Cloud build → downloadable APK
└── android-config/
    ├── AndroidManifest-additions.xml  Reference for TV manifest merges
    └── make-banner.html               Generates the required 320×180 TV banner
```

`www/hls.min.js` and the `android/` folder are created during the build (they're gitignored).

---

## Path A — Cloud build (no installs)

Best if you don't want Android Studio on your machine.

1. Create a new GitHub repo and push this whole folder to it:
   ```bash
   cd streamline-tv
   git init && git add . && git commit -m "Streamline TV"
   git branch -M main
   git remote add origin https://github.com/<you>/streamline-tv.git
   git push -u origin main
   ```
2. On GitHub, open the **Actions** tab. The "Build Android TV APK" workflow runs automatically on push (or click **Run workflow**).
3. When it finishes (~4–6 min), open the run and download the **streamline-tv-debug-apk** artifact. Inside is `app-debug.apk`.
4. Install it on your TV (see **Installing on the TV** below).

The workflow fetches HLS.js, adds the Android platform, patches the manifest for the leanback launcher automatically, and builds the debug APK. Nothing to configure.

> Note: the auto-built APK uses the default app icon and no custom banner. To add the TV banner, generate one with `android-config/make-banner.html` and commit it to `android/app/src/main/res/drawable/banner.png`, then add `android:banner="@drawable/banner"` to the `<application>` tag before pushing. (Optional — the app runs without it.)

---

## Path B — Local build (Android Studio)

Best if you want to customise icons/banner, sign a release APK, or debug on a device.

### 1. Install prerequisites
- **Node.js 18+** — https://nodejs.org
- **Android Studio** — https://developer.android.com/studio
  During setup, let it install the Android SDK. Then in Android Studio → SDK Manager, make sure an SDK Platform (API 34) and the build-tools are installed.

### 2. Build
```bash
cd streamline-tv
npm run fetch-hls          # downloads hls.min.js into www/
npm install                # installs Capacitor
npx cap add android        # creates the android/ project

# Merge the Android TV bits from android-config/AndroidManifest-additions.xml
# into android/app/src/main/AndroidManifest.xml (leanback launcher, uses-feature, permissions)

npx cap sync android
npm run open               # opens the project in Android Studio
```
In Android Studio: **Build → Build Bundle(s)/APK(s) → Build APK(s)**. The APK lands in
`android/app/build/outputs/apk/debug/app-debug.apk`.

Or from the command line:
```bash
npm run build:apk
```

### 3. Optional: banner + icon
- Open `android-config/make-banner.html` in a browser, download `banner.png`, place it in
  `android/app/src/main/res/drawable/`, and add `android:banner="@drawable/banner"` to `<application>`.
- Replace launcher icons via Android Studio → right-click `res` → New → Image Asset.

---

## Installing on the TV

Pick whichever is easiest:

- **Send Files to TV / adb over network** (most common):
  1. On the TV: Settings → enable **Developer options** and **USB/network debugging**.
  2. From your computer: `adb connect <TV-ip>:5555` then `adb install app-debug.apk`.
- **Downloader app** (no computer): put the APK on a cloud link, install the "Downloader" app on the TV, enter the URL, and it installs.
- **USB stick**: copy the APK to a USB drive, plug into the TV, open with a file manager, install. You may need to allow "install from unknown sources".

After install, "Streamline TV" appears in the Android TV apps row.

---

## Using it with a remote

- **D-pad** moves the highlight between the sidebar, channel list, and player.
- **OK/Center** selects. On the video area, OK toggles fullscreen.
- **Back** exits fullscreen.
- Text fields open the on-screen keyboard when selected.

---

## Notes & limits

- **Codecs:** the WebView plays what Android's system decoder supports — HLS (`.m3u8`), MP4/H.264, AAC. Exotic containers (e.g. some MKV/AC3 VOD) may not play in a WebView. If you need bulletproof codec coverage, the next step up is swapping the `<video>`/HLS layer for a native ExoPlayer bridge — tell me if you want that version.
- **http:// servers** are allowed via the cleartext config. That's expected for most IPTV panels.
- This is a **player only** — it ships with no channels or credentials. You supply your own legal Xtream account.
- Debug APKs are unsigned for the Play Store but install fine via sideload. For a Play Store release you'd generate a signed release build + AAB.
