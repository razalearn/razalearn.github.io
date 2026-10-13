# razalearn.github.io

The public website for Short Budgets apps, served by GitHub Pages at https://razalearn.github.io.

| URL | Used by |
|---|---|
| `/app-ads.txt` | AdMob. Must stay at the site root, and this domain must be the developer website on the Play listing. |
| `/<app>/privacy/` | Play Console privacy policy URL, AdMob consent message, and the in-app `AppInfo.PRIVACY_POLICY_URL`, for `peepdoku`, `birdoku` and `arrowz`. |
| `/<app>/` | Play listing website and support page. |
| `/rollbook/privacy/` | Rollbook's Play Console privacy policy URL and the in-app `AppInfo.PRIVACY_POLICY_URL`. Written by hand, not generated: update it whenever the app starts collecting something new. |
| `/rollbook/delete-account/` | Rollbook's account deletion URL in the Play Console Data safety form. |

The privacy pages are generated from `PRIVACY_POLICY` in each app's `ui/InfoScreens.kt`, which is
the source of truth. After changing an app's policy (and `AppInfo.POLICY_LAST_UPDATED`), run
`python tools/gen_privacy.py` from this folder, with the app projects checked out next to
`peepdoku/` as they are locally, then commit and push.
