# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0", "jsonschema>=3.2"]
# ///
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import time
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple
from xml.etree import ElementTree

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parent.parent
NAME = "episteme"
HOLDER = "Convective Numerical Systems LLC"
CREDIT = "aetelier.xyz"
CONTACT = "support@aetelier.xyz"
REPO = "aetelierxyz/episteme"
REPO_URL = f"https://github.com/{REPO}"
RAW_URL = f"https://raw.githubusercontent.com/{REPO}"
SITE_URL = "https://aetelier.xyz/docs/episteme/"
CC = "https://creativecommons.org"
ARXIV_ABS = "https://arxiv.org/abs/"
ARXIV_RECORD = (
    "https://oaipmh.arxiv.org/oai?verb=GetRecord"
    "&identifier=oai:arXiv.org:{}&metadataPrefix=arXiv"
)
ARXIV_PAUSE = 3.0
USER_AGENT = f"{NAME} (+{REPO_URL}; {CONTACT})"

OWN_FILES = frozenset({"card.md", "cite.bib", "PERMISSION.md"})
HOSTED_FILES = frozenset({"source.pdf", "fulltext.md"})
BLOCKED_SUFFIXES = frozenset({".pdf", ".epub", ".djvu", ".ps", ".ppt", ".pptx", ".key"})
OPEN_LICENSES = frozenset({"CC0-1.0", "CC-PDM-1.0"})
CLEARED_ABSTRACT = frozenset({"work-license", "arxiv-cc0", "permission"})
STALE_DAYS = 365
SUMMARY_HEADINGS = (
    "## Scientific Summary",
    "## Engineering Summary",
    "## Application Summary",
)
SUMMARY_WORDS = 100
ABSTRACT_HEADING = "## Abstract"
NOTICE_HEADING = "## Card license"
NOTICE = (
    f"Summaries: © {HOLDER}, "
    f"[CC BY 4.0]({CC}/licenses/by/4.0/). "
    f"Front matter: [CC0 1.0]({CC}/publicdomain/zero/1.0/). "
    "The work keeps the license in `rights_license`."
)
CARD_LICENCES = ("CC0-1.0", "CC-BY-4.0")
LICENCE_URLS = {
    "CC0-1.0": f"{CC}/publicdomain/zero/1.0/",
    "CC-PDM-1.0": f"{CC}/publicdomain/mark/1.0/",
    "LicenseRef-arXiv-nonexclusive-1.0": (
        "https://arxiv.org/licenses/nonexclusive-distrib/1.0/"
    ),
}
LICENCE_NAMES = {
    "CC0-1.0": "CC0 1.0",
    "CC-PDM-1.0": "Public Domain Mark 1.0",
    "LicenseRef-arXiv-nonexclusive-1.0": "arXiv non-exclusive 1.0",
    "LicenseRef-all-rights-reserved": "All rights reserved",
    "LicenseRef-permission": "Written permission",
}
TOPIC_ID = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")

BIBTEX_TYPES = {
    "article": "article",
    "proceedings": "inproceedings",
    "preprint": "misc",
    "book": "book",
    "chapter": "incollection",
    "thesis": "phdthesis",
    "report": "techreport",
    "slides": "misc",
}
BIBTEX_CONTAINERS = {
    "article": "journal",
    "proceedings": "booktitle",
    "chapter": "booktitle",
    "thesis": "school",
    "report": "institution",
    "preprint": "howpublished",
    "slides": "howpublished",
}
MANIFEST_FILES = (
    ("index/catalog.jsonl", "catalog"),
    ("index/catalog.md", "catalog-table"),
    ("schema/work.schema.json", "schema"),
    ("schema/topics.json", "topics"),
    ("AGENTS.md", "agent-rules"),
    ("LICENSE.md", "license-map"),
)
Card = dict[str, Any]
Topics = dict[str, dict[str, str]]


class Release(NamedTuple):
    version: str
    date: str

    @property
    def tag(self) -> str:
        return f"v{self.version}"

    @property
    def base_url(self) -> str:
        return f"{RAW_URL}/{self.tag}/"


def plain(value: Any) -> Any:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()[:10]
    if isinstance(value, list):
        return [plain(item) for item in value]
    return value


def split_card(text: str) -> tuple[Card, str]:
    if not text.startswith("---\n"):
        raise ValueError("front matter missing")
    head, closed, body = text[4:].partition("\n---\n")
    if not closed:
        raise ValueError("front matter not closed")
    meta = yaml.safe_load(head)
    if not isinstance(meta, dict):
        raise ValueError("front matter is not a mapping")
    return {str(key): plain(value) for key, value in meta.items()}, body


def read_release(root: Path) -> tuple[Release | None, list[str]]:
    path = root / "CITATION.cff"
    if not path.is_file():
        return None, ["CITATION.cff: missing"]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return None, [f"CITATION.cff: {error}"]
    if not isinstance(data, dict):
        return None, ["CITATION.cff: not a mapping"]
    version = str(data.get("version", ""))
    date = str(plain(data.get("date-released", "")))
    errors: list[str] = []
    if not VERSION.fullmatch(version):
        errors.append("CITATION.cff: version must read MAJOR.MINOR.PATCH")
    if not ISO_DATE.fullmatch(date):
        errors.append("CITATION.cff: date-released must read YYYY-MM-DD")
    if errors:
        return None, errors
    return Release(version, date), []


def read_topics(root: Path) -> tuple[Topics, list[str]]:
    where = "schema/topics.json"
    path = root / "schema" / "topics.json"
    if not path.is_file():
        return {}, [f"{where}: missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return {}, [f"{where}: {error}"]
    entries = data.get("topics") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        return {}, [f"{where}: 'topics' must be a non-empty list"]
    topics: Topics = {}
    errors: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"id", "label", "definition"}:
            errors.append(f"{where}: each topic holds id, label and definition")
            continue
        term = str(entry["id"])
        if not TOPIC_ID.fullmatch(term):
            errors.append(f"{where}: '{term}' is not kebab-case")
        if term in topics:
            errors.append(f"{where}: '{term}' is listed twice")
        if not str(entry["label"]).strip() or not str(entry["definition"]).strip():
            errors.append(f"{where}: '{term}' needs a label and a definition")
        topics[term] = {key: str(value) for key, value in entry.items()}
    if list(topics) != sorted(topics):
        errors.append(f"{where}: topics must be sorted by id")
    return topics, errors


def schema_version(schema: dict[str, Any]) -> int:
    return int(schema["properties"]["schema_version"]["const"])


def licence_flags(licence: str) -> tuple[bool, bool, bool] | None:
    if licence in OPEN_LICENSES:
        return True, True, False
    if licence.startswith("CC-BY"):
        parts = licence.split("-")
        return "NC" not in parts, "ND" not in parts, "SA" in parts
    return None


def licence_url(licence: str) -> str | None:
    if licence in LICENCE_URLS:
        return LICENCE_URLS[licence]
    if licence.startswith("CC-BY"):
        *terms, version = licence.lower().split("-")[1:]
        return f"{CC}/licenses/{'-'.join(terms)}/{version}/"
    return None


def licence_name(licence: str) -> str:
    if licence in LICENCE_NAMES:
        return LICENCE_NAMES[licence]
    if licence.startswith("CC-BY"):
        *terms, version = licence.split("-")[1:]
        return f"CC {'-'.join(terms)} {version}"
    return licence


def derive_tier(card: Card) -> str:
    basis = card["rights_basis"]
    licence = str(card["rights_license"])
    if basis == "public-domain" or licence in OPEN_LICENSES:
        return "A"
    if basis == "none":
        return "C"
    if card["rights_commercial"] and card["rights_derivatives"]:
        return "A"
    return "B"


def work_holder(card: Card) -> str:
    return f"{card['year']} {card['rights_holder'] or 'The Authors'}"


def rights_errors(card: Card) -> list[str]:
    errors: list[str] = []
    licence = str(card["rights_license"])
    basis = card["rights_basis"]
    flags = (
        card["rights_commercial"],
        card["rights_derivatives"],
        card["rights_share_alike"],
    )
    expected = licence_flags(licence)
    if expected is not None:
        if basis not in {"license", "public-domain"}:
            errors.append(
                f"rights_basis '{basis}' does not match open license {licence}"
            )
        if flags != expected:
            errors.append(
                f"rights flags {flags} do not match {licence}, expected {expected}"
            )
    elif basis == "license":
        errors.append(f"rights_basis 'license' needs an open license, found {licence}")
    elif basis == "none" and any(flags):
        errors.append("rights flags must all be false when rights_basis is 'none'")
    if card["rights_license_url"] != licence_url(licence):
        errors.append(f"rights_license_url must be {licence_url(licence)}")
    tier = derive_tier(card)
    if tier != card["rights_tier"]:
        errors.append(f"rights_tier is {card['rights_tier']}, derived tier is {tier}")
    if card["rights_tier"] == "A" and not card["rights_attribution"]:
        errors.append("tier A needs rights_attribution")
    return errors


def file_errors(card: Card, folder: Path) -> list[str]:
    errors: list[str] = []
    present = {item.name for item in folder.iterdir() if item.is_file()}
    hosted = present - OWN_FILES
    declared = set(card["files"])
    if hosted != declared:
        errors.append(
            f"files lists {sorted(declared)}, directory holds {sorted(hosted)}"
        )
    if hosted - HOSTED_FILES:
        errors.append(f"unexpected files {sorted(hosted - HOSTED_FILES)}")
    if hosted and (card["rights_tier"] != "A" or card["rights_hold"]):
        errors.append(f"hosted files {sorted(hosted)} need tier A without hold")
    if card["rights_basis"] == "permission" and "PERMISSION.md" not in present:
        errors.append("rights_basis 'permission' needs PERMISSION.md")
    return errors


def topic_errors(card: Card, topics: Topics) -> list[str]:
    unknown = [term for term in card["topics"] if term not in topics]
    if unknown:
        return [f"topics {unknown} are not terms of schema/topics.json"]
    return []


def sections(body: str) -> list[tuple[str, str]]:
    found: list[tuple[str, list[str]]] = []
    for line in body.splitlines():
        if line.startswith("## "):
            found.append((line.strip(), []))
        elif found:
            found[-1][1].append(line)
    return [(heading, "\n".join(lines).strip()) for heading, lines in found]


def abstract_source(card: Card) -> str | None:
    basis = card["abstract_basis"]
    if basis == "arxiv-cc0" and card["arxiv"]:
        return (
            f"Source: arXiv record [{card['arxiv']}]({ARXIV_ABS}{card['arxiv']}), "
            f"metadata under [CC0 1.0]({LICENCE_URLS['CC0-1.0']})."
        )
    if basis == "work-license" and card["rights_license_url"]:
        name = licence_name(str(card["rights_license"]))
        return (
            f"Source: the work, © {work_holder(card)}, "
            f"[{name}]({card['rights_license_url']})."
        )
    if basis == "permission":
        return "Source: the work, by the written grant in `PERMISSION.md`."
    return None


def quoted(section: str) -> str:
    lines = [line[1:] for line in section.splitlines() if line.startswith(">")]
    return " ".join(" ".join(lines).split())


def abstract_errors(card: Card, body: str) -> list[str]:
    errors: list[str] = []
    included = bool(card["abstract_included"])
    basis = card["abstract_basis"]
    if included and basis not in CLEARED_ABSTRACT:
        errors.append("abstract_included needs a cleared abstract_basis")
    if basis == "work-license" and (card["rights_tier"] != "A" or card["rights_hold"]):
        errors.append("abstract_basis 'work-license' needs tier A without hold")
    if basis == "arxiv-cc0" and not card["arxiv"]:
        errors.append("abstract_basis 'arxiv-cc0' needs an arxiv identifier")
    found = [text for heading, text in sections(body) if heading == ABSTRACT_HEADING]
    if included != bool(found):
        errors.append("abstract_included does not match the '## Abstract' section")
    source = abstract_source(card)
    for text in found:
        quote, _, last = text.rpartition("\n")
        lines = [line for line in quote.splitlines() if line.strip()]
        if not quoted(quote) or any(not line.startswith(">") for line in lines):
            errors.append("'## Abstract' must hold the abstract as a block quote")
        if source is not None and last.strip() != source:
            errors.append(f"'## Abstract' must end with the line: {source}")
    return errors


def section_errors(card: Card, body: str) -> list[str]:
    errors: list[str] = []
    parts = sections(body)
    found = [heading for heading, _ in parts if "Summary" in heading]
    if found != list(SUMMARY_HEADINGS):
        errors.append(
            f"summary headings are {found}, expected {list(SUMMARY_HEADINGS)}"
        )
    for heading, text in parts:
        words = len(text.split())
        if heading in SUMMARY_HEADINGS and words > SUMMARY_WORDS:
            errors.append(f"{heading[3:]} has {words} words, limit is {SUMMARY_WORDS}")
    if [text for heading, text in parts if heading == NOTICE_HEADING] != [NOTICE]:
        errors.append(f"'{NOTICE_HEADING}' must hold the card license notice")
    expected = [*SUMMARY_HEADINGS, NOTICE_HEADING]
    if card["abstract_included"]:
        expected.insert(0, ABSTRACT_HEADING)
    order = [heading for heading, _ in parts]
    if not errors and order != expected:
        errors.append(f"sections are {order}, expected {expected}")
    return errors


def with_abstract(text: str, card: Card, abstract: str) -> str:
    source = abstract_source(card)
    flag = "\nabstract_included: false\n"
    anchor = f"\n{SUMMARY_HEADINGS[0]}\n"
    clean = " ".join(abstract.split())
    if source is None or not clean:
        raise ValueError("abstract is not cleared or is empty")
    if text.count(flag) != 1 or text.count(anchor) != 1:
        raise ValueError("card does not accept an abstract")
    block = f"\n{ABSTRACT_HEADING}\n\n> {clean}\n\n{source}\n"
    return text.replace(flag, flag.replace("false", "true")).replace(
        anchor, block + anchor
    )


def arxiv_abstract(record: str) -> str:
    for element in ElementTree.fromstring(record).iter():
        if element.tag.rpartition("}")[2] == "abstract":
            text = " ".join("".join(element.itertext()).split())
            if text:
                return text
    raise ValueError("the arXiv record holds no abstract")


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def sync_abstracts(
    root: Path,
    cards: list[Card],
    get: Callable[[str], str] = fetch,
    pause: float = 0.0,
) -> tuple[list[str], list[str], list[str]]:
    added: list[str] = []
    matched: list[str] = []
    problems: list[str] = []
    asked = 0
    for card in cards:
        if card["abstract_basis"] != "arxiv-cc0":
            continue
        if asked:
            time.sleep(pause)
        asked += 1
        name = str(card["id"])
        path = root / "works" / name / "card.md"
        text = path.read_text(encoding="utf-8")
        try:
            abstract = arxiv_abstract(get(ARXIV_RECORD.format(card["arxiv"])))
        except (OSError, ValueError, ElementTree.ParseError) as error:
            problems.append(f"{name}: {error}")
            continue
        held = [
            section
            for heading, section in sections(split_card(text)[1])
            if heading == ABSTRACT_HEADING
        ]
        if not held:
            path.write_text(with_abstract(text, card, abstract), encoding="utf-8")
            added.append(name)
        elif quoted(held[0].rpartition("\n")[0]) == abstract:
            matched.append(name)
        else:
            problems.append(f"{name}: the abstract differs from the arXiv record")
    return added, matched, problems


def card_warnings(card: Card, today: dt.date) -> list[str]:
    warnings: list[str] = []
    age = (today - dt.date.fromisoformat(card["rights_verified"])).days
    if age > STALE_DAYS:
        warnings.append(f"rights verified {age} days ago")
    if card["rights_hold"]:
        warnings.append("rights on hold")
    if card["abstract_basis"] in CLEARED_ABSTRACT and not card["abstract_included"]:
        warnings.append("cleared abstract not included")
    if card["summary_status"] == "pending":
        warnings.append("summaries pending")
    return warnings


def check_card(
    folder: Path, validator: Any, topics: Topics, today: dt.date
) -> tuple[Card | None, list[str], list[str]]:
    path = folder / "card.md"
    if not path.is_file():
        return None, ["card.md missing"], []
    try:
        card, body = split_card(path.read_text(encoding="utf-8"))
    except (ValueError, yaml.YAMLError) as error:
        return None, [str(error)], []
    schema_errors = sorted(
        f"{'/'.join(str(part) for part in issue.path) or 'card'}: {issue.message}"
        for issue in validator.iter_errors(card)
    )
    if schema_errors:
        return None, schema_errors, []
    errors: list[str] = []
    if card["id"] != folder.name:
        errors.append(f"id '{card['id']}' does not match directory '{folder.name}'")
    errors += rights_errors(card)
    errors += file_errors(card, folder)
    errors += topic_errors(card, topics)
    errors += abstract_errors(card, body)
    errors += section_errors(card, body)
    return card, errors, card_warnings(card, today)


def ignored_names(root: Path) -> tuple[frozenset[str], frozenset[str]]:
    rooted: set[str] = set()
    anywhere: set[str] = {".git"}
    path = root / ".gitignore"
    lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
    for line in lines:
        entry = line.strip()
        name = entry.strip("/")
        if not name or entry.startswith("#") or any(mark in name for mark in "*?[!/"):
            continue
        (rooted if entry.startswith("/") else anywhere).add(name)
    return frozenset(rooted), frozenset(anywhere)


def tree_errors(root: Path) -> list[str]:
    errors: list[str] = []
    works = root / "works"
    rooted, anywhere = ignored_names(root)
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file() or relative.parts[0] in rooted:
            continue
        if anywhere.intersection(relative.parts):
            continue
        if path.suffix.lower() not in BLOCKED_SUFFIXES:
            continue
        if path.parent.parent == works and path.name in HOSTED_FILES:
            continue
        errors.append(f"{relative.as_posix()}: full-text file outside a tier A work")
    return errors


def load(root: Path, today: dt.date) -> tuple[list[Card], list[str], list[str]]:
    schema = json.loads(
        (root / "schema" / "work.schema.json").read_text(encoding="utf-8")
    )
    validator = jsonschema.Draft7Validator(schema)
    topics, topic_issues = read_topics(root)
    cards: list[Card] = []
    errors = tree_errors(root) + read_release(root)[1] + topic_issues
    warnings: list[str] = []
    works = root / "works"
    folders = (
        sorted(item for item in works.iterdir() if item.is_dir())
        if works.is_dir()
        else []
    )
    for folder in folders:
        card, card_errors, notes = check_card(folder, validator, topics, today)
        where = f"works/{folder.name}/card.md"
        errors += [f"{where}: {message}" for message in card_errors]
        warnings += [f"{where}: {message}" for message in notes]
        if card is not None:
            cards.append(card)
    used = {term for card in cards for term in card["topics"]}
    warnings += [
        f"schema/topics.json: '{term}' is used by no work"
        for term in topics
        if term not in used
    ]
    return cards, errors, warnings


def tex(value: Any) -> str:
    text = str(value)
    for char in "&%#":
        text = text.replace(char, "\\" + char)
    return text


def bibtex(card: Card) -> str:
    fields: list[tuple[str, str]] = [
        ("title", "{" + tex(card["title"]) + "}"),
        ("author", " and ".join(tex(author) for author in card["authors"])),
        ("year", str(card["year"])),
    ]
    container = BIBTEX_CONTAINERS.get(card["type"])
    if container and card["venue"]:
        fields.append((container, tex(card["venue"])))
    for key, name in (
        ("volume", "volume"),
        ("issue", "number"),
        ("publisher", "publisher"),
    ):
        if card[key]:
            fields.append((name, tex(card[key])))
    if card["pages"]:
        fields.append(("pages", str(card["pages"]).replace("-", "--")))
    for key in ("isbn", "doi"):
        if card[key]:
            fields.append((key, str(card[key])))
    if card["arxiv"]:
        fields += [("eprint", str(card["arxiv"])), ("archiveprefix", "arXiv")]
    fields.append(("url", str(card["url"])))
    width = max(len(name) for name, _ in fields)
    lines = [f"  {name.ljust(width)} = {{{value}}}," for name, value in fields]
    return "\n".join([f"@{BIBTEX_TYPES[card['type']]}{{{card['id']},", *lines, "}", ""])


def cell(value: Any) -> str:
    return str(value).replace("|", "\\|")


def lead_author(card: Card) -> str:
    families = [str(author).split(",")[0] for author in card["authors"]]
    if len(families) <= 2:
        return " and ".join(families)
    return f"{families[0]} et al."


def tally(cards: list[Card]) -> dict[str, Any]:
    return {
        "works": len(cards),
        "tier_a": sum(card["rights_tier"] == "A" for card in cards),
        "tier_b": sum(card["rights_tier"] == "B" for card in cards),
        "tier_c": sum(card["rights_tier"] == "C" for card in cards),
        "hosted_files": sum(len(card["files"]) for card in cards),
        "abstracts": sum(bool(card["abstract_included"]) for card in cards),
        "summaries": {
            status: sum(card["summary_status"] == status for card in cards)
            for status in ("pending", "draft", "reviewed")
        },
    }


def tally_line(cards: list[Card]) -> str:
    counts = tally(cards)
    return (
        f"{counts['works']} works: {counts['tier_a']} tier A, "
        f"{counts['tier_b']} tier B, {counts['tier_c']} tier C. "
        f"Hosted files: {counts['hosted_files']}. Abstracts: {counts['abstracts']}."
    )


def topic_use(cards: list[Card], term: str) -> int:
    return sum(term in card["topics"] for card in cards)


def catalog_markdown(cards: list[Card], topics: Topics) -> str:
    lines = [
        "# Catalog",
        "",
        "Generated from the cards in `works/`.",
        "",
        tally_line(cards),
        "",
        "| Work | Year | Tier | License | Hosted | Abstract | Summaries | Source |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for card in cards:
        tier = (
            f"{card['rights_tier']} (hold)"
            if card["rights_hold"]
            else card["rights_tier"]
        )
        name = f"{lead_author(card)}, {card['title']}"
        licence = f"`{card['rights_license']}`"
        if card["rights_license_url"]:
            licence = f"[{licence}]({card['rights_license_url']})"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"[{cell(name)}](../works/{card['id']}/card.md)",
                    str(card["year"]),
                    tier,
                    licence,
                    ", ".join(card["files"]) or "-",
                    "yes" if card["abstract_included"] else "-",
                    str(card["summary_status"]),
                    f"[link]({card['url']})",
                ]
            )
            + " |"
        )
    lines += [
        "",
        "## Topics",
        "",
        "Defined in `schema/topics.json`.",
        "",
        "| Topic | Definition | Works |",
        "|---|---|---|",
    ]
    lines += [
        f"| `{term}` | {cell(entry['definition'])} | {topic_use(cards, term)} |"
        for term, entry in topics.items()
    ]
    return "\n".join(lines) + "\n"


def annotation(paths: list[str], holders: list[str], licence: str) -> list[str]:
    holder = holders[0] if len(holders) == 1 else holders
    return [
        "",
        "[[annotations]]",
        f"path = {json.dumps(paths)}",
        'precedence = "override"',
        f"SPDX-FileCopyrightText = {json.dumps(holder, ensure_ascii=False)}",
        f"SPDX-License-Identifier = {json.dumps(licence)}",
    ]


def reuse_toml(cards: list[Card], year: int) -> str:
    own = f"{year} {HOLDER}"
    lines = [
        "version = 1",
        f"SPDX-PackageName = {json.dumps(NAME)}",
        f"SPDX-PackageDownloadLocation = {json.dumps(REPO_URL)}",
    ]
    lines += annotation(["tools/**"], [own], "MIT")
    lines += annotation(
        [
            "*.md",
            ".gitignore",
            ".gitattributes",
            "CITATION.cff",
            ".github/**",
            "schema/**",
            "index/**",
            "works/*/cite.bib",
        ],
        [own],
        "CC0-1.0",
    )
    lines += annotation(["works/*/card.md"], [own], " AND ".join(CARD_LICENCES))
    for card in cards:
        if card["abstract_included"] and card["abstract_basis"] == "work-license":
            licence = str(card["rights_license"])
            extra = [] if licence in CARD_LICENCES else [licence]
            lines += annotation(
                [f"works/{card['id']}/card.md"],
                [own, work_holder(card)],
                " AND ".join([*CARD_LICENCES, *extra]),
            )
    for card in cards:
        if card["files"]:
            paths = [f"works/{card['id']}/{name}" for name in sorted(card["files"])]
            lines += annotation(paths, [work_holder(card)], str(card["rights_license"]))
    return "\n".join(lines) + "\n"


def stamped_schema(text: str, release: Release) -> str:
    target = f"{release.base_url}schema/work.schema.json"
    return re.sub(
        r'("\$id":\s*")[^"]*', lambda found: found.group(1) + target, text, count=1
    )


def digest(root: Path, relative: str, **extra: str) -> dict[str, Any]:
    data = (root / relative).read_bytes()
    return {
        "path": relative,
        **extra,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def manifest(root: Path, cards: list[Card], release: Release, version: int) -> str:
    works = []
    for card in cards:
        folder = f"works/{card['id']}"
        works.append(
            {
                "id": card["id"],
                "card": digest(root, f"{folder}/card.md"),
                "hosted": [
                    digest(
                        root, f"{folder}/{name}", license=str(card["rights_license"])
                    )
                    for name in sorted(card["files"])
                ],
            }
        )
    data = {
        "name": NAME,
        "version": release.version,
        "tag": release.tag,
        "released": release.date,
        "schema_version": version,
        "repository": REPO_URL,
        "site": SITE_URL,
        "base_url": release.base_url,
        "licensor": HOLDER,
        "contact": CONTACT,
        "counts": tally(cards),
        "files": [
            digest(root, relative, role=role)
            for relative, role in MANIFEST_FILES
            if (root / relative).is_file()
        ],
        "works": works,
    }
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def write(path: Path, text: str, written: list[Path]) -> None:
    if not path.is_file() or path.read_text(encoding="utf-8") != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written.append(path)


def build(root: Path, cards: list[Card]) -> list[Path]:
    release = read_release(root)[0]
    topics = read_topics(root)[0]
    if release is None:
        raise ValueError("CITATION.cff holds no release")
    schema_path = root / "schema" / "work.schema.json"
    schema_text = stamped_schema(schema_path.read_text(encoding="utf-8"), release)
    outputs = {
        schema_path: schema_text,
        root / "index" / "catalog.jsonl": "".join(
            json.dumps(card, ensure_ascii=False) + "\n" for card in cards
        ),
        root / "index" / "catalog.md": catalog_markdown(cards, topics),
        root / "REUSE.toml": reuse_toml(cards, int(release.date[:4])),
    }
    for card in cards:
        outputs[root / "works" / card["id"] / "cite.bib"] = bibtex(card)
    written: list[Path] = []
    for path, text in outputs.items():
        write(path, text, written)
    version = schema_version(json.loads(schema_text))
    write(
        root / "index" / "manifest.json",
        manifest(root, cards, release, version),
        written,
    )
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="episteme")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="validate every card and the tree")
    commands.add_parser(
        "build",
        help="validate, then write index/, works/*/cite.bib and REUSE.toml",
    )
    commands.add_parser(
        "abstracts",
        help="add or compare the abstracts cleared by arXiv metadata; needs network",
    )
    args = parser.parse_args(argv)
    today = dt.date.today()
    cards, errors, warnings = load(ROOT, today)
    for message in warnings:
        print(f"warning: {message}", file=sys.stderr)
    for message in errors:
        print(f"error: {message}", file=sys.stderr)
    if errors:
        print(f"{len(errors)} errors, {len(warnings)} warnings", file=sys.stderr)
        return 1
    if args.command == "abstracts":
        added, matched, problems = sync_abstracts(ROOT, cards, pause=ARXIV_PAUSE)
        for name in added:
            print(f"added works/{name}/card.md")
        for message in problems:
            print(f"error: {message}", file=sys.stderr)
        print(f"{len(added)} added, {len(matched)} match, {len(problems)} failed")
        return 1 if problems else 0
    if args.command == "build":
        for path in build(ROOT, cards):
            print(f"wrote {path.relative_to(ROOT).as_posix()}")
    tiers = " ".join(
        f"{tier}={sum(card['rights_tier'] == tier for card in cards)}" for tier in "ABC"
    )
    print(f"{len(cards)} works: {tiers}, {len(warnings)} warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
