"""Builds <app>/privacy/index.html from the privacy text compiled into each app.

The in-app policy (PRIVACY_POLICY in ui/InfoScreens.kt) is the source of truth, so the
web copy can never drift from what players see. Run from the website folder after
changing any app's policy:

    python tools/gen_privacy.py

The page chrome below (head, header, app sub-navigation, footer) is the same markup the
hand-written pages use. If you change it here, change it in the other pages too.
"""
import html
import os
import re
import sys

APPS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SITE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# slug -> (display name, path to the app's Kotlin sources)
APPS = {
    "peepdoku": ("Peepdoku", "peepdoku/app/src/main/java/com/shortbudgets/logicriddle"),
    "birdoku": ("Birdoku", "birdoku/app/src/main/java/com/shortbudgets/logicriddle"),
    "arrowz": ("Arrowz", "arrowz/app/src/main/java/com/shortbudgets/arrowz"),
    "pipewise": ("Pipewise", "pipewise/app/src/main/java/com/shortbudgets/pipewise"),
}

# Every app on the site: slug -> (name, has an account deletion page)
SITE_APPS = {
    "peepdoku": ("Peepdoku", False),
    "birdoku": ("Birdoku", False),
    "arrowz": ("Arrowz", False),
    "pipewise": ("Pipewise", False),
    "rollbook": ("Rollbook", True),
    "laraib": ("Laraib", True),
}


# ---------------------------------------------------------------- shared chrome

def head(title, description):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#F7F8F6" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#0E1411" media="(prefers-color-scheme: dark)">
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
  <link rel="icon" type="image/png" href="/assets/favicon-32.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/site.css">
  <script src="/assets/site.js" defer></script>
</head>"""


def header(current=None):
    """current: 'games', 'apps' or 'contact', to mark the matching global link."""
    def link(href, label, key, extra=""):
        cur = ' aria-current="page"' if current == key else ""
        cls = f' class="{extra}"' if extra else ""
        return f'<a href="{href}"{cls}{cur}>{label}</a>'
    return f"""  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="wrap bar">
      <a class="brand" href="/"><span class="brand-mark" aria-hidden="true">SL</span>Salmari Labs</a>
      <nav class="global-nav" aria-label="Main">
        {link("/#games", "Games", "games")}
        {link("/#apps", "Productivity", "apps", "nav-hide-sm")}
        {link("/#privacy", "Privacy", "privacy", "nav-hide-sm")}
        {link("/#contact", "Contact", "contact", "nav-cta")}
      </nav>
    </div>
  </header>"""


def subnav(slug, current):
    """current: 'overview', 'privacy', 'support' or 'delete'."""
    name, has_delete = SITE_APPS[slug]
    items = [("overview", f"/{slug}/", "Overview"),
             ("support", f"/{slug}/#support", "Support"),
             ("privacy", f"/{slug}/privacy/", "Privacy policy")]
    if has_delete:
        items.append(("delete", f"/{slug}/delete-account/", "Delete account"))
    current_attr = ' aria-current="page"'
    links = "\n".join(
        f'        <a href="{href}"{current_attr if key == current else ""}>{label}</a>'
        for key, href, label in items)
    return f"""  <div class="subnav">
    <div class="wrap">
      <a class="subnav-app" href="/{slug}/"><img src="/assets/{slug}-192.png" alt="" width="26" height="26"><span>{name}</span></a>
      <nav aria-label="{name}">
{links}
      </nav>
    </div>
  </div>"""


def footer():
    return """  <footer class="site-footer">
    <div class="wrap footer-grid">
      <div class="footer-brand">
        <a class="brand" href="/"><span class="brand-mark" aria-hidden="true">SL</span>Salmari Labs</a>
        <p>Small, focused Android apps: cozy logic puzzles, a planner for teachers and a Quran Hifz tracker. Every one works offline.</p>
      </div>
      <div>
        <h2>Puzzle games</h2>
        <ul>
          <li><a href="/peepdoku/">Peepdoku</a></li>
          <li><a href="/birdoku/">Birdoku</a></li>
          <li><a href="/arrowz/">Arrowz</a></li>
          <li><a href="/pipewise/">Pipewise</a></li>
        </ul>
      </div>
      <div>
        <h2>Productivity</h2>
        <ul>
          <li><a href="/rollbook/">Rollbook</a></li>
          <li><a href="/laraib/">Laraib</a></li>
        </ul>
      </div>
      <div>
        <h2>Privacy</h2>
        <ul>
          <li><a href="/peepdoku/privacy/">Peepdoku privacy</a></li>
          <li><a href="/birdoku/privacy/">Birdoku privacy</a></li>
          <li><a href="/arrowz/privacy/">Arrowz privacy</a></li>
          <li><a href="/pipewise/privacy/">Pipewise privacy</a></li>
          <li><a href="/rollbook/privacy/">Rollbook privacy</a></li>
          <li><a href="/laraib/privacy/">Laraib privacy</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="wrap">
        <span>© 2026 Salmari Labs. All rights reserved.</span>
        <a href="mailto:salmarilabs@gmail.com">salmarilabs@gmail.com</a>
      </div>
    </div>
  </footer>
</body>
</html>
"""


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def doc_page(*, slug, title, description, h1, crumb, current, meta, sections, foot_note, comment=""):
    """A document page (privacy policy) with breadcrumbs, metadata and a table of contents.

    meta: list of (label, value). sections: list of (heading, inner html).
    """
    name = SITE_APPS[slug][0]
    toc = "\n".join(
        f'            <li><a href="#{slugify(h)}">{html.escape(h)}</a></li>' for h, _ in sections)
    body = "\n".join(
        f'      <section id="{slugify(h)}">\n'
        f'        <h2>{html.escape(h)}<a class="anchor" href="#{slugify(h)}" aria-label="Link to this section">#</a></h2>\n'
        f'{inner}\n      </section>' for h, inner in sections)
    meta_html = "\n".join(
        f'        <div><dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd></div>' for k, v in meta)
    return f"""{head(title, description)}
<body data-app="{slug}">
{header()}
{subnav(slug, current)}

  <main id="main">
    {comment}
    <div class="page-head">
      <div class="wrap">
        <nav class="crumbs" aria-label="Breadcrumb">
          <ol>
            <li><a href="/">Home</a></li>
            <li><a href="/{slug}/">{name}</a></li>
            <li aria-current="page">{crumb}</li>
          </ol>
        </nav>
        <p class="eyebrow">Legal</p>
        <h1>{h1}</h1>
        <dl class="meta">
{meta_html}
        </dl>
      </div>
    </div>

    <div class="wrap doc-layout">
      <aside class="toc">
        <details open>
          <summary>On this page</summary>
          <p class="toc-title">On this page</p>
          <ol>
{toc}
          </ol>
        </details>
      </aside>
      <article class="prose">
{body}
        <div class="doc-foot">
          <span>{foot_note}</span>
          <a href="/{slug}/" class="arrow-link">Back to {name}</a>
        </div>
      </article>
    </div>
  </main>

{footer()}"""


def render_generated(slug, name, updated, developer, sections):
    """sections: list of (heading, paragraph html)."""
    return doc_page(
        slug=slug,
        title=f"{name} Privacy Policy",
        description=f"How {name}, a puzzle game by Salmari Labs, handles your data.",
        h1=f"{name} privacy policy",
        crumb="Privacy policy",
        current="privacy",
        meta=[("Last updated", updated), ("Developer", developer)],
        sections=[(h, f"        <p>{p}</p>") for h, p in sections],
        foot_note=f"This is the same policy shown inside the {name} app.",
        comment="<!-- Generated by tools/gen_privacy.py from PRIVACY_POLICY in the app's ui/InfoScreens.kt. Do not edit by hand. -->",
    )


# ---------------------------------------------------------------- generator

STRING = r'"(?:[^"\\]|\\.)*"'
ENTRY = re.compile(rf'({STRING})\s+to\s+((?:{STRING}\s*\+?\s*)+)')


def kotlin_const(src, name):
    match = re.search(rf'const val {name} = "([^"]*)"', src)
    if not match:
        sys.exit(f"{name} not found in AppInfo.kt")
    return match.group(1)


def literal(token, consts):
    text = bytes(token[1:-1], "utf-8").decode("unicode_escape")
    for key, value in consts.items():
        text = text.replace("${AppInfo.%s}" % key, value)
    if "${" in text:
        sys.exit(f"Unresolved template in: {text}")
    return text


def linkify(text, email):
    out = html.escape(text, quote=False)
    out = out.replace(
        "policies.google.com/privacy",
        '<a href="https://policies.google.com/privacy">policies.google.com/privacy</a>')
    out = out.replace(email, f'<a href="mailto:{email}">{email}</a>')
    return out


def main():
    for slug, (name, rel) in APPS.items():
        src_dir = os.path.join(APPS_ROOT, rel)
        info = open(os.path.join(src_dir, "AppInfo.kt"), encoding="utf-8").read()
        consts = {k: kotlin_const(info, k) for k in ("NAME", "SUPPORT_EMAIL", "DEVELOPER", "POLICY_LAST_UPDATED")}
        screens = open(os.path.join(src_dir, "ui", "InfoScreens.kt"), encoding="utf-8").read()
        block = re.search(r"private val PRIVACY_POLICY = listOf\((.*?)\n\)\n", screens, re.S)
        if not block:
            sys.exit(f"PRIVACY_POLICY not found for {slug}")
        sections = []
        for heading, body in ENTRY.findall(block.group(1)):
            title = literal(heading, consts)
            text = "".join(literal(t, consts) for t in re.findall(STRING, body))
            sections.append((title, linkify(text, consts["SUPPORT_EMAIL"])))
        if len(sections) < 5:
            sys.exit(f"Only {len(sections)} sections parsed for {slug}")
        out_dir = os.path.join(SITE, slug, "privacy")
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(render_generated(slug, name, consts["POLICY_LAST_UPDATED"], consts["DEVELOPER"], sections))
        print(f"{slug}: {len(sections)} sections, updated {consts['POLICY_LAST_UPDATED']}")


if __name__ == "__main__":
    main()
