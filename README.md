# razalearn.github.io

The public website for Short Budgets apps, served by GitHub Pages at https://razalearn.github.io.

| URL | Used by |
|---|---|
| `/app-ads.txt` | AdMob. Must stay at the site root, and this domain must be the developer website on the Play listing. |
| `/<app>/privacy/` | Play Console privacy policy URL, AdMob consent message, and the in-app `AppInfo.PRIVACY_POLICY_URL`, for `peepdoku`, `birdoku` and `arrowz`. |
| `/<app>/` | Play listing website and support page. |
| `/rollbook/privacy/` | Rollbook's Play Console privacy policy URL and the in-app `AppInfo.PRIVACY_POLICY_URL`. Written by hand, not generated: update it whenever the app starts collecting something new. |
| `/rollbook/delete-account/` | Rollbook's account deletion URL in the Play Console Data safety form. |
| `/laraib/privacy/`, `/laraib/delete-account/` | Laraib's Play Console privacy policy and account deletion URLs. Written by hand, like Rollbook's. |

The privacy pages are generated from `PRIVACY_POLICY` in each app's `ui/InfoScreens.kt`, which is
the source of truth. After changing an app's policy (and `AppInfo.POLICY_LAST_UPDATED`), run
`python tools/gen_privacy.py` from this folder, with the app projects checked out next to
`peepdoku/` as they are locally, then commit and push.

## Design

All pages share `assets/site.css` (design tokens, light and dark themes, components) and the
optional `assets/site.js` (table-of-contents highlighting). Each app page sets
`<body data-app="<slug>">` to pick up that app's accent colour. The header, app sub-navigation
and footer markup lives in `tools/gen_privacy.py` (`header()`, `subnav()`, `footer()`); the
hand-written pages repeat the same markup, so change both together.
