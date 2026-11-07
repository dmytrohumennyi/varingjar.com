#!/usr/bin/env python3
"""Usage: python3 tools/build-navigator.py   (run from the site root, needs beautifulsoup4)

Build the site navigator data: assets/js/site-tree.js and assets/js/site-search-<lang>.js.
Labels come from the pages themselves (h1) or from the short section labels already used on the site."""
import json, os, re, sys, pathlib
from bs4 import BeautifulSoup

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent)
LANGS = {"en": "", "uk": "uk/", "de": "de/"}
SKIP = {"404.html", "publications.html", "partners.html", "technology.html"}

UI = {
    "en": dict(title="Site navigator", search="Search the site — pages, articles, lectures…", open="Search and site map",
               short="Search", here="You are here", none="Nothing found. Try another word, or open a section below.",
               results="results", close="Close", general="General", home="Home", about="About the author",
               privacy="Privacy", contents="Section contents", hint="Tip: press / on any page to search.",
               sections={"model": "Framework", "evidence": "Evidence", "build": "Build", "teaching": "Teaching", "collab": "Collaborate"}),
    "uk": dict(title="Навігатор сайту", search="Пошук по сайту — сторінки, статті, лекції…", open="Пошук і мапа сайту",
               short="Пошук", here="Ви тут", none="Нічого не знайдено. Спробуйте інше слово або відкрийте розділ нижче.",
               results="результатів", close="Закрити", general="Загальне", home="Головна", about="Про автора",
               privacy="Конфіденційність", contents="Зміст розділу", hint="Порада: натисніть / на будь-якій сторінці, щоб шукати.",
               sections={"model": "Модель", "evidence": "Докази", "build": "Реалізація", "teaching": "Навчання", "collab": "Співпраця"}),
    "de": dict(title="Website-Navigator", search="Website durchsuchen — Seiten, Artikel, Vorlesungen…", open="Suche und Seitenübersicht",
               short="Suche", here="Sie sind hier", none="Nichts gefunden. Versuchen Sie ein anderes Wort oder öffnen Sie unten einen Bereich.",
               results="Ergebnisse", close="Schließen", general="Allgemein", home="Startseite", about="Über den Autor",
               privacy="Datenschutz", contents="Inhalt des Bereichs", hint="Tipp: Drücken Sie auf jeder Seite /, um zu suchen.",
               sections={"model": "Modell", "evidence": "Evidenz", "build": "Implementierung", "teaching": "Lehre", "collab": "Mitwirken"}),
}

# short labels already used in the sidebars (kept identical for consistency)
SHORT = {
    "en": {"programme.html": "Framework overview", "architecture.html": "Architecture", "evolution.html": "Model evolution",
           "research.html": "Evidence overview", "research/experiments/index.html": "Experiments",
           "research/publications.html": "Publications and talks", "research/roadmap.html": "Evidence roadmap",
           "research/cases/index.html": "Mission cases", "research/bibliography.html": "Full publication catalogue",
           "research/monograph.html": "Monograph", "research/projects.html": "Projects and dissertation",
           "implementation.html": "Build overview", "implementation/runtime-questions.html": "Four runtime questions",
           "implementation/software-reference.html": "Reference software: C++ → ROS 2",
           "implementation/hardware-path.html": "Hardware path: RISC-V → SoC IP",
           "implementation/validation-limits.html": "Validation limits", "applications.html": "Application domains",
           "applications/robotics.html": "Robotics", "applications/aerospace.html": "Aerospace",
           "applications/case-criteria.html": "Case criteria", "teaching.html": "Teaching overview",
           "teaching/embedded-software-engineering/index.html": "Course map: Embedded Software Engineering",
           "collaboration.html": "Collaboration overview", "collaboration/partners.html": "People and partners",
           "contact.html": "Contact"},
    "uk": {"programme.html": "Огляд моделі", "architecture.html": "Архітектура", "evolution.html": "Еволюція моделі",
           "research.html": "Огляд доказів", "research/experiments/index.html": "Експерименти",
           "research/publications.html": "Публікації й доповіді", "research/roadmap.html": "Карта доказів",
           "research/cases/index.html": "Кейси місій", "research/bibliography.html": "Повний каталог публікацій",
           "research/monograph.html": "Монографія", "research/projects.html": "Проєкти й дисертація",
           "implementation.html": "Огляд реалізації", "implementation/runtime-questions.html": "Чотири питання під час виконання",
           "implementation/software-reference.html": "Референсне ПЗ: C++ → ROS 2",
           "implementation/hardware-path.html": "Апаратний шлях: RISC-V → SoC IP",
           "implementation/validation-limits.html": "Що треба довести далі", "applications.html": "Домени застосування",
           "applications/robotics.html": "Робототехніка", "applications/aerospace.html": "Аерокосмічна галузь",
           "applications/case-criteria.html": "Критерії кейсу", "teaching.html": "Огляд навчання",
           "teaching/embedded-software-engineering/index.html": "Мапа курсу",
           "collaboration.html": "Огляд співпраці", "collaboration/partners.html": "Люди й партнери",
           "contact.html": "Контакт"},
    "de": {"programme.html": "Modellübersicht", "architecture.html": "Architektur", "evolution.html": "Modellentwicklung",
           "research.html": "Evidenz-Übersicht", "research/experiments/index.html": "Experimente",
           "research/publications.html": "Publikationen und Vorträge", "research/roadmap.html": "Evidenz-Roadmap",
           "research/cases/index.html": "Missionsfälle", "research/bibliography.html": "Vollständiger Publikationskatalog",
           "research/monograph.html": "Monografie", "research/projects.html": "Projekte und Dissertation",
           "implementation.html": "Übersicht", "implementation/runtime-questions.html": "Vier Laufzeitfragen",
           "implementation/software-reference.html": "Referenzsoftware: C++ → ROS 2",
           "implementation/hardware-path.html": "Hardwarepfad: RISC-V → SoC IP",
           "implementation/validation-limits.html": "Validierungsgrenzen", "applications.html": "Anwendungsdomänen",
           "applications/robotics.html": "Robotik", "applications/aerospace.html": "Luft- und Raumfahrt",
           "applications/case-criteria.html": "Fallkriterien", "teaching.html": "Lehre: Übersicht",
           "teaching/embedded-software-engineering/index.html": "Kursübersicht",
           "collaboration.html": "Übersicht", "collaboration/partners.html": "Personen und Partner",
           "contact.html": "Kontakt"},
}

LECTURES = [f"teaching/embedded-software-engineering/lecture-{i:02d}.html" for i in range(1, 15)]
STRUCT = [
    ("model", [
        ("programme.html", []),
        ("knowledge/start-here.html", []), ("knowledge/survivability-metric.html", []), ("knowledge/model-validity.html", []),
        ("framework/failure-resources.html", []), ("framework/abstraction-hierarchy.html", []),
        ("framework/capability-admissibility.html", []), ("framework/epistemic-resources.html", []),
        ("framework/transformation-space.html", []), ("framework/timing.html", []), ("framework/trajectory.html", []),
        ("architecture.html", ["architecture/abstraction-state.html", "architecture/supervisor-loop.html",
                               "architecture/candidate-evaluation.html", "architecture/timing-mechanism.html"]),
        ("evolution.html", ["evolution/formulations.html", "evolution/missing-guarantees.html",
                            "evolution/revised-model.html", "evolution/evidence-trail.html"]),
    ]),
    ("evidence", [
        ("research.html", []),
        ("research/experiments/index.html", ["research/experiments/exp-01-irreversible-actuator-damage/index.html",
                                             "research/experiments/exp-02-graph-reconfiguration/index.html",
                                             "research/experiments/exp-03-survivability-driven-reconfiguration/index.html"]),
        ("research/publications.html", []), ("research/roadmap.html", []), ("research/cases/index.html", []),
        ("research/bibliography.html", []), ("research/monograph.html", []), ("research/projects.html", []),
    ]),
    ("build", [
        ("implementation.html", ["implementation/runtime-questions.html", "implementation/software-reference.html",
                                 "implementation/hardware-path.html", "implementation/validation-limits.html"]),
        ("applications.html", ["applications/robotics.html", "applications/aerospace.html", "applications/case-criteria.html"]),
    ]),
    ("teaching", [
        ("teaching.html", []),
        ("teaching/embedded-software-engineering/index.html", LECTURES),
    ]),
    ("collab", [
        ("collaboration.html", ["collaboration/hard-problem.html", "collaboration/partners.html", "collaboration/support-evidence.html"]),
        ("contact.html", []),
    ]),
]

SECTION_OF = [("teaching", "teaching"), ("programme", "model"), ("framework/", "model"), ("knowledge/", "model"),
              ("architecture", "model"), ("evolution", "model"), ("research", "evidence"), ("implementation", "build"),
              ("applications", "build"), ("collaboration", "collab"), ("contact", "collab")]


def section_of(path):
    for pre, sec in SECTION_OF:
        if path.startswith(pre):
            return sec
    return "general"


def clean(t):
    return re.sub(r"\s+", " ", t or "").strip()


def page_info(lang, path):
    f = ROOT / (LANGS[lang] + path)
    soup = BeautifulSoup(f.read_text(encoding="utf-8"), "html.parser")
    h1 = soup.find("h1")
    title = clean(h1.get_text(" ")) if h1 else ""
    if not title and soup.title:
        title = clean(soup.title.get_text()).split(" — ")[0]
    desc = soup.find("meta", attrs={"name": "description"})
    desc = clean(desc["content"]) if desc and desc.get("content") else ""
    main = soup.find("main")
    heads, text = [], ""
    if main:
        for t in main(["script", "style", "svg", "nav", "aside", "button"]):
            t.decompose()
        for t in main.select(".module-back, .cases-back, .portfolio-back, .research-subnav, .course-context-v3, .module-nextprev, .module-local-nav, .i18n-note"):
            t.decompose()
        heads = [clean(h.get_text(" ")) for h in main.find_all(["h2", "h3", "h4"])]
        text = clean(main.get_text(" "))
    return title, desc, heads, text


def label(lang, path, title):
    if path in SHORT[lang]:
        return SHORT[lang][path]
    if path in LECTURES:
        return f"{path[-7:-5]} · {title}"
    return title.rstrip(".")


tree, search = {}, {}
for lang in LANGS:
    infos = {}
    for f in sorted((ROOT / LANGS[lang]).glob("**/*.html") if lang != "en" else ROOT.glob("**/*.html")):
        rel = f.relative_to(ROOT).as_posix()
        if lang == "en" and (rel.startswith("uk/") or rel.startswith("de/")):
            continue
        path = rel[len(LANGS[lang]):]
        if path in SKIP:
            continue
        title, desc, heads, text = page_info(lang, path)
        if not text:
            continue
        infos[path] = (title, desc, heads, text)
    # tree
    sections = []
    for sec, items in STRUCT:
        out = []
        for p, kids in items:
            assert p in infos, (lang, p)
            node = {"u": p, "t": label(lang, p, infos[p][0])}
            if kids:
                node["c"] = [{"u": k, "t": label(lang, k, infos[k][0])} for k in kids if k in infos]
            out.append(node)
        sections.append({"k": sec, "t": UI[lang]["sections"][sec], "i": out})
    sections.append({"k": "general", "t": UI[lang]["general"], "i": [
        {"u": "index.html", "t": UI[lang]["home"]}, {"u": "about.html", "t": UI[lang]["about"]},
        {"u": "privacy.html", "t": UI[lang]["privacy"]}]})
    ui = {k: v for k, v in UI[lang].items() if k != "sections"}
    tree[lang] = {"ui": ui, "s": sections, "p": LANGS[lang]}
    # search entries
    labels = {}
    for s in sections:
        for n in s["i"]:
            labels[n["u"]] = n["t"]
            for c in n.get("c", []):
                labels[c["u"]] = c["t"]
    entries = []
    for p, (title, desc, heads, text) in infos.items():
        sec = section_of(p)
        entries.append({"u": p, "t": title or labels.get(p, p), "s": UI[lang]["sections"].get(sec, UI[lang]["general"]),
                        "d": desc, "h": " · ".join(h for h in heads if h)[:1500], "x": text[:20000]})
    search[lang] = entries

js = ROOT / "assets" / "js"
(js / "site-tree.js").write_text("/* Væringjar II · site navigator tree (generated). */\nwindow.VJ_TREE=" +
                                 json.dumps(tree, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
for lang, entries in search.items():
    (js / f"site-search-{lang}.js").write_text(
        "/* Væringjar II · search index (generated). */\nwindow.VJ_SEARCH=window.VJ_SEARCH||{};window.VJ_SEARCH." + lang + "=" +
        json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(lang, len(entries), "pages,", round(os.path.getsize(js / f"site-search-{lang}.js") / 1024), "KB")
print("tree", round(os.path.getsize(js / "site-tree.js") / 1024), "KB")
