"""Build static EN/PT pages from the Spanish guide and reviewed translations.

Run after editing docs/index.html. Missing translations fail the build.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
BASE = 'https://mauricioperera.github.io/julia-finetune-workspace/'
TRANSLATIONS = json.loads((DOCS / 'translations.json').read_text(encoding='utf-8'))
source = (DOCS / 'index.html').read_text(encoding='utf-8')


def metadata(page, locale):
    page = re.sub(r'\s*<link rel="(?:canonical|alternate)"[^>]*>', '', page)
    links = [f'<link rel="canonical" href="{BASE}{locale + "/" if locale != "es" else ""}">']
    for lang, route in [('es', ''), ('en', 'en/'), ('pt', 'pt/'), ('x-default', '')]:
        links.append(f'<link rel="alternate" hreflang="{lang}" href="{BASE}{route}">')
    return page.replace('</head>', '  ' + '\n  '.join(links) + '\n</head>')


for locale in ('en', 'pt'):
    def translate(match):
        raw = match.group(1)
        text = raw.strip()
        if not text or text in {'j.', 'Julia', 'fine-tuning', 'Julia fine-tuning', 'GitHub ↗', 'Español', 'English', 'Português', '01', '02', '03', '↓', '↳', '⧉', '▤', '→', '↗', '3/6'}:
            return match.group(0)
        if text.startswith(BASE):
            translated = BASE + locale + '/prompt.md'
        else:
            translated = TRANSLATIONS[text][locale]
        return '>' + raw.replace(text, html.escape(translated, quote=False)) + '<'

    page = re.sub(r'>([^<>]*)<', translate, source)
    for attribute in ('aria-label', 'content'):
        def translate_attribute(match):
            value = match.group(1)
            if value not in TRANSLATIONS:
                if attribute == 'aria-label':
                    raise KeyError(value)
                return match.group(0)
            return attribute + '="' + html.escape(TRANSLATIONS[value][locale], quote=True) + '"'
        page = re.sub(attribute + r'="([^"]*)"', translate_attribute, page)
    page = page.replace('lang="es"', f'lang="{locale}"')
    page = page.replace('href="styles.css"', 'href="../styles.css"').replace('src="script.js"', 'src="../script.js"')
    options = '<option value="../"' + '>Español</option>'
    options += '<option value="' + ('./" selected' if locale == 'en' else '../en/"') + '>English</option>'
    options += '<option value="' + ('./" selected' if locale == 'pt' else '../pt/"') + '>Português</option>'
    page = re.sub(r'<option.*?</select>', options + '</select>', page)
    folder = DOCS / locale
    folder.mkdir(exist_ok=True)
    (folder / 'index.html').write_text(metadata(page, locale), encoding='utf-8', newline='\n')

(DOCS / 'index.html').write_text(metadata(source, 'es'), encoding='utf-8', newline='\n')
print('Built Spanish, English and Portuguese pages.')
