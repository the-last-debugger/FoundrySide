# Android app

A debug APK of the market companion that runs **entirely offline** on the phone. No server, no
network, no accounts, no bets.

## Build

```bash
python scripts/export_app_data.py      # bundle a data slice (~150 KB)
python scripts/build_apk.py            # writes app/android/build/foundryside.apk
```

The build uses the SDK's own tools and **no Gradle**: `aapt2` links the manifest and assets, `javac`
compiles one activity against `android.jar`, `d8` produces the dex, `zipalign` aligns and `apksigner`
signs with a local debug key. Gradle is not installed here and a wrapper download would be a large
dependency for one activity.

Requirements: Android SDK build-tools 37 (34's `d8` crashes on Java 17 class files with the JDK 25
`javac`), `platforms/android-34`, and a JDK on `PATH`.

## What the app does

| Tab | Shows |
| --- | --- |
| Assess | The recorded prices for a selection, the de-vigged market probability, the price-implied probability, with claim tags |
| Market | Every book held for the fixture, with its own margin and implied probabilities, plus the over/under pair when present |
| Structures | The same net upside at different prices: stake at risk, gross, hit probability, expected loss, variance |
| Slip | One selection's price, stake arithmetic, gross, net and full-stake loss |

## Design decisions that matter

- **No `INTERNET` permission in the manifest.** The platform, not a convention, prevents a request.
  `settings.setBlockNetworkLoads(true)` is a second barrier, and the WebView refuses navigation away
  from the packaged page.
- **The data ships inside the APK.** A WebView cannot fetch a local file, so the slice is embedded as
  `data.js`. It is 600 fixtures — a slice, not the corpus.
- **One selection per slip.** Combining legs needs a joint distribution; the app cannot estimate one,
  and saying so is better than multiplying as though legs were independent.
- **Claim tags throughout.** Observed, estimated, hypothetical, exactly as in the local server.
- **One stylesheet, two consumers.** pp/ui/theme.css is the single source of colours, spacing and
  component classes. scripts/export_app_data.py copies it into the APK's assets, so the phone and
  the local page cannot drift apart visually; only layout that is genuinely different (desktop versus
  phone) stays inline in each page.
- **The same explainer.** The "How to read these numbers" panel appears in the app, stating that the
  best recorded price is not a price you were offered and that the de-vigged probability is an
  assumption rather than a forecast.

## Known limits

1. **Not installed or run on a device.** The APK is built and signature-verified, and its assets are
   unit-tested, but no emulator or handset was available to launch it. That gap is real and is stated
   rather than glossed.
2. **Debug signing.** Signed with a local debug key, not a release key. Not for distribution.
3. **600-fixture slice**, chosen for bundle size; the local server has the full corpus.
4. **The JavaScript is a port**, not the Python engine. The arithmetic is duplicated because the app
   is offline, and ports drift — so scripts/check_js_parity.py runs the JavaScript under Node and
   compares de-vig, assessments and structure tables against the Python engine on shared fixtures.
   The port mirrors the engine's field names and rounding exactly, which is what makes the comparison
   exact rather than approximate. Run it after touching either side.

## Reproducing the verification

```bash
python -m unittest tests.test_apk_assets     # 10 checks on the bundled assets
python scripts/build_apk.py                  # rebuild and re-sign
```
