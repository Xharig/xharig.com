# SPDX-License-Identifier: GPL-3.0-only
"""
Builds the English home page `en/index.html` from the German `index.html`.

The German page is the only source. Every text element carries `data-de` and
`data-en`; this script puts the `data-en` text into the element, sets every
attribute that has a `data-en-<attribute>` twin (meta description, links) to
the English value, switches `lang`, the canonical address and the language
buttons, and points relative paths one folder up.

    python3 tools/seite_en_bauen.py            # write en/index.html
    python3 tools/seite_en_bauen.py --pruefen  # exit 1 if en/index.html is outdated

Fails if an element with `data-de` contains markup or lacks `data-en`, so no
German text slips through unnoticed.
"""

import html
import os
import re
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(WURZEL, "index.html")
ZIEL = os.path.join(WURZEL, "en", "index.html")
ADRESSE = "https://xharig.com/"

KOPF = ("<!-- Generated from index.html by tools/seite_en_bauen.py."
        " Do not edit; change index.html and run the script. -->\n")

TEXT_ELEMENT = re.compile(
    r'(<(?P<tag>[a-zA-Z][a-zA-Z0-9]*)\b(?P<attr>[^>]*\bdata-de="[^"]*"[^>]*)>)'
    r'(?P<inhalt>[^<]*)'
    r'(</(?P=tag)>)')
DATA_EN = re.compile(r'\bdata-en="([^"]*)"')


class Fehler(Exception):
    pass


def _ersetzen(muster, ersatz, text, anzahl, was):
    neu, n = re.subn(muster, ersatz, text)
    if n != anzahl:
        raise Fehler("%s: expected %d match(es), found %d" % (was, anzahl, n))
    return neu


def _attribute_tauschen(m):
    """`x="de" data-en-x="en"` becomes `x="en"` inside one tag."""
    tag = m.group(0)
    for name, wert in re.findall(r'\sdata-en-([a-zA-Z-]+)="([^"]*)"', tag):
        tag = re.sub(r'\s+data-en-%s="[^"]*"' % re.escape(name), "", tag, count=1)
        tag, n = re.subn(r'(?<![\w-])%s="[^"]*"' % re.escape(name),
                         lambda _m: '%s="%s"' % (name, wert), tag, count=1)
        if n != 1:
            raise Fehler('data-en-%s without %s="…": %s' % (name, name, tag[:120]))
    return tag


def bauen(quelle):
    gesamt = len(re.findall(r'\bdata-de="', quelle))
    getroffen = [0]

    def text_tauschen(m):
        en = DATA_EN.search(m.group("attr"))
        if en is None:
            raise Fehler("data-en missing: %s" % m.group(1)[:120])
        getroffen[0] += 1
        text = html.escape(html.unescape(en.group(1)), quote=False)
        return m.group(1) + text + m.group(5)

    seite = TEXT_ELEMENT.sub(text_tauschen, quelle)
    if getroffen[0] != gesamt:
        raise Fehler("%d of %d data-de elements could not be translated "
                     "(element contains markup?)" % (gesamt - getroffen[0], gesamt))

    seite = re.sub(r'<[a-zA-Z][^>]*\bdata-en-[^>]*>', _attribute_tauschen, seite)
    if re.search(r'\sdata-en-[a-zA-Z-]+="', seite):
        raise Fehler("data-en-<attribute> left over")

    seite = _ersetzen(r'<html lang="de">', '<html lang="en">', seite, 1, "lang")
    seite = _ersetzen(r'<link rel="canonical" href="%s">' % re.escape(ADRESSE),
                      '<link rel="canonical" href="%sen/">' % ADRESSE,
                      seite, 1, "canonical")
    seite = _ersetzen(r'(<a href="/" data-lang="de"[^>]*?) class="an"', r'\1', seite, 1, "button de")
    seite = _ersetzen(r'(<a href="/en/" data-lang="en"[^>]*?)>', r'\1 class="an">', seite, 1, "button en")

    seite = re.sub(r'\b(src|href)="(assets/|impressum\.html|datenschutz\.html)', r'\1="../\2', seite)

    if "<!DOCTYPE html>\n" not in seite:
        raise Fehler("DOCTYPE line not found")
    return seite.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n" + KOPF, 1)


def dateien_pruefen(seite):
    fehlend = [p for p in re.findall(r'\b(?:src|href)="\.\./([^"?]+)', seite)
               if not os.path.exists(os.path.join(WURZEL, p))]
    if fehlend:
        raise Fehler("missing files: " + ", ".join(sorted(set(fehlend))))


def main(argv):
    with open(QUELLE, encoding="utf-8") as f:
        quelle = f.read()
    try:
        seite = bauen(quelle)
        dateien_pruefen(seite)
    except Fehler as e:
        print("en/index.html: " + str(e))
        return 1

    if "--pruefen" in argv:
        try:
            with open(ZIEL, encoding="utf-8") as f:
                vorhanden = f.read()
        except OSError:
            vorhanden = None
        if vorhanden != seite:
            print("en/index.html is outdated: run python3 tools/seite_en_bauen.py")
            return 1
        print("en/index.html is up to date")
        return 0

    os.makedirs(os.path.dirname(ZIEL), exist_ok=True)
    with open(ZIEL, "w", encoding="utf-8", newline="\n") as f:
        f.write(seite)
    print("written: en/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
