from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

import episteme
import jsonschema
import pytest
import yaml

SCHEMA_TEXT = (episteme.ROOT / "schema" / "work.schema.json").read_text(
    encoding="utf-8"
)
SCHEMA = json.loads(SCHEMA_TEXT)
VALIDATOR = jsonschema.Draft7Validator(SCHEMA)
TODAY = dt.date(2026, 11, 25)
RELEASE = episteme.Release("0.0.1", "2026-11-25")
ATTRIBUTION = "Doe (2020). Sample. CC BY 4.0."
CC = "https://creativecommons.org"
TOPICS: episteme.Topics = {
    "sample": {"id": "sample", "label": "Sample", "definition": "A sample term."}
}
CITATION = 'cff-version: 1.2.0\nversion: "0.0.1"\ndate-released: "2026-11-25"\n'
RECORD = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
<GetRecord><record><metadata>
<arXiv xmlns="http://arxiv.org/OAI/arXiv/">
<id>2001.00001</id>
<title>Sample</title>
<abstract>  First line of the abstract
with a wrap &amp; an entity.
</abstract>
</arXiv>
</metadata></record></GetRecord>
</OAI-PMH>"""
RECORD_TEXT = "First line of the abstract with a wrap & an entity."
BODY = (
    "\n# Sample\n\n"
    "## Scientific Summary\n\nNot yet written.\n\n"
    "## Engineering Summary\n\nNot yet written.\n\n"
    "## Application Summary\n\nNot yet written.\n\n"
    f"{episteme.NOTICE_HEADING}\n\n{episteme.NOTICE}\n"
)


def body_with(words: int) -> str:
    return BODY.replace("Not yet written.", " ".join(["word"] * words), 1)


def make(**changes: Any) -> dict[str, Any]:
    card: dict[str, Any] = {
        "schema_version": 1,
        "id": "doe_2020_sample",
        "type": "article",
        "title": "Sample",
        "authors": ["Doe, Jane"],
        "year": 2020,
        "venue": "Journal",
        "volume": "1",
        "issue": "2",
        "pages": "3-4",
        "publisher": "Press",
        "doi": "10.1234/sample",
        "arxiv": None,
        "isbn": None,
        "url": "https://doi.org/10.1234/sample",
        "url_free": None,
        "related": [],
        "version": "vor",
        "rights_tier": "A",
        "rights_license": "CC-BY-4.0",
        "rights_license_url": f"{CC}/licenses/by/4.0/",
        "rights_basis": "license",
        "rights_commercial": True,
        "rights_derivatives": True,
        "rights_share_alike": False,
        "rights_holder": "The Authors",
        "rights_evidence": "License statement, PDF p.1",
        "rights_verified": "2026-11-25",
        "rights_attribution": ATTRIBUTION,
        "rights_hold": False,
        "rights_note": None,
        "files": [],
        "abstract_included": False,
        "abstract_basis": "work-license",
        "keywords": [],
        "topics": ["sample"],
        "summary_status": "reviewed",
    }
    card.update(changes)
    return card


def closed(**changes: Any) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "rights_tier": "C",
        "rights_license": "LicenseRef-all-rights-reserved",
        "rights_license_url": None,
        "rights_basis": "none",
        "rights_commercial": False,
        "rights_derivatives": False,
        "rights_attribution": None,
        "abstract_basis": "none",
    }
    fields.update(changes)
    return make(**fields)


def preprint(**changes: Any) -> dict[str, Any]:
    fields: dict[str, Any] = {"arxiv": "2001.00001", "abstract_basis": "arxiv-cc0"}
    fields.update(changes)
    return closed(**fields)


def abstract_body(
    card: dict[str, Any], quote: str = "> Text.", source: str | None = None
) -> str:
    line = episteme.abstract_source(card) if source is None else source
    block = f"## Abstract\n\n{quote}\n\n{line}\n\n## Scientific Summary"
    return BODY.replace("## Scientific Summary", block, 1)


def write(root: Path, card: dict[str, Any], body: str = BODY) -> Path:
    folder = root / "works" / str(card["id"])
    folder.mkdir(parents=True)
    head = yaml.safe_dump(card, sort_keys=False, allow_unicode=True)
    (folder / "card.md").write_text(f"---\n{head}---\n{body}", encoding="utf-8")
    return folder


def errors_of(folder: Path) -> list[str]:
    return episteme.check_card(folder, VALIDATOR, TOPICS, TODAY)[1]


def scaffold(root: Path) -> None:
    (root / "schema").mkdir()
    (root / "schema" / "work.schema.json").write_text(SCHEMA_TEXT, encoding="utf-8")
    (root / "schema" / "topics.json").write_text(
        json.dumps({"topics": list(TOPICS.values())}), encoding="utf-8"
    )
    (root / "CITATION.cff").write_text(CITATION, encoding="utf-8")
    (root / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")


@pytest.mark.parametrize(
    ("licence", "flags"),
    [
        ("CC0-1.0", (True, True, False)),
        ("CC-PDM-1.0", (True, True, False)),
        ("CC-BY-4.0", (True, True, False)),
        ("CC-BY-SA-4.0", (True, True, True)),
        ("CC-BY-NC-4.0", (False, True, False)),
        ("CC-BY-ND-4.0", (True, False, False)),
        ("CC-BY-NC-SA-4.0", (False, True, True)),
        ("CC-BY-NC-ND-4.0", (False, False, False)),
    ],
)
def test_licence_flags(licence: str, flags: tuple[bool, bool, bool]) -> None:
    assert episteme.licence_flags(licence) == flags


def test_licence_flags_unknown() -> None:
    assert episteme.licence_flags("LicenseRef-all-rights-reserved") is None


@pytest.mark.parametrize(
    ("licence", "url"),
    [
        ("CC0-1.0", f"{CC}/publicdomain/zero/1.0/"),
        ("CC-PDM-1.0", f"{CC}/publicdomain/mark/1.0/"),
        ("CC-BY-4.0", f"{CC}/licenses/by/4.0/"),
        ("CC-BY-SA-4.0", f"{CC}/licenses/by-sa/4.0/"),
        ("CC-BY-NC-4.0", f"{CC}/licenses/by-nc/4.0/"),
        ("CC-BY-NC-SA-4.0", f"{CC}/licenses/by-nc-sa/4.0/"),
        ("CC-BY-ND-4.0", f"{CC}/licenses/by-nd/4.0/"),
        ("CC-BY-NC-ND-4.0", f"{CC}/licenses/by-nc-nd/4.0/"),
        (
            "LicenseRef-arXiv-nonexclusive-1.0",
            "https://arxiv.org/licenses/nonexclusive-distrib/1.0/",
        ),
        ("LicenseRef-all-rights-reserved", None),
        ("LicenseRef-permission", None),
    ],
)
def test_licence_url(licence: str, url: str | None) -> None:
    assert episteme.licence_url(licence) == url


@pytest.mark.parametrize(
    ("licence", "name"),
    [
        ("CC0-1.0", "CC0 1.0"),
        ("CC-BY-4.0", "CC BY 4.0"),
        ("CC-BY-NC-SA-4.0", "CC BY-NC-SA 4.0"),
        ("LicenseRef-all-rights-reserved", "All rights reserved"),
    ],
)
def test_licence_name(licence: str, name: str) -> None:
    assert episteme.licence_name(licence) == name


@pytest.mark.parametrize(
    ("licence", "tier"),
    [
        ("CC0-1.0", "A"),
        ("CC-BY-4.0", "A"),
        ("CC-BY-SA-4.0", "A"),
        ("CC-BY-NC-4.0", "B"),
        ("CC-BY-ND-4.0", "B"),
        ("CC-BY-NC-SA-4.0", "B"),
        ("CC-BY-NC-ND-4.0", "B"),
    ],
)
def test_tier_of_open_licences(licence: str, tier: str) -> None:
    flags = episteme.licence_flags(licence)
    assert flags is not None
    card = make(
        rights_license=licence,
        rights_commercial=flags[0],
        rights_derivatives=flags[1],
        rights_share_alike=flags[2],
    )
    assert episteme.derive_tier(card) == tier


def test_tier_without_licence() -> None:
    assert episteme.derive_tier(closed()) == "C"


@pytest.mark.parametrize(
    "identifier",
    ["bouchaud_2018_trades", "olfati_saber_2004_consensus", "lucchese_2024_short_term"],
)
def test_snake_case_ids_pass_the_schema(identifier: str) -> None:
    assert list(VALIDATOR.iter_errors(make(id=identifier))) == []


@pytest.mark.parametrize("identifier", ["bouchaud2018trades", "Bouchaud_2018_Trades"])
def test_other_ids_fail_the_schema(identifier: str) -> None:
    assert list(VALIDATOR.iter_errors(make(id=identifier))) != []


@pytest.mark.parametrize(
    "changes",
    [
        {"schema_version": 2},
        {"related": ["https://example.org/code"]},
        {"topics": []},
        {"topics": ["Not Kebab"]},
    ],
)
def test_schema_rejects(changes: dict[str, Any]) -> None:
    assert list(VALIDATOR.iter_errors(make(**changes))) != []


def test_schema_version_is_read_from_the_schema() -> None:
    assert episteme.schema_version(SCHEMA) == 1


def test_valid_cards_pass(tmp_path: Path) -> None:
    assert errors_of(write(tmp_path, make())) == []
    assert errors_of(write(tmp_path, closed(id="roe_2021_sample"))) == []


def test_tier_must_match_licence(tmp_path: Path) -> None:
    folder = write(tmp_path, make(rights_tier="B"))
    assert any("derived tier is A" in message for message in errors_of(folder))


def test_flags_must_match_licence(tmp_path: Path) -> None:
    folder = write(tmp_path, make(rights_license="CC-BY-NC-4.0", rights_tier="B"))
    assert any("do not match CC-BY-NC-4.0" in message for message in errors_of(folder))


def test_license_url_must_match_licence(tmp_path: Path) -> None:
    folder = write(tmp_path, make(rights_license_url=f"{CC}/licenses/by-nc/4.0/"))
    assert any("rights_license_url must be" in message for message in errors_of(folder))


def test_license_url_must_be_null_without_licence(tmp_path: Path) -> None:
    folder = write(tmp_path, closed(rights_license_url=f"{CC}/licenses/by/4.0/"))
    assert any("rights_license_url must be None" in m for m in errors_of(folder))


def test_hosted_file_needs_tier_a(tmp_path: Path) -> None:
    folder = write(tmp_path, closed(files=["source.pdf"]))
    (folder / "source.pdf").write_bytes(b"%PDF")
    assert any("need tier A" in message for message in errors_of(folder))


def test_hold_blocks_hosted_file(tmp_path: Path) -> None:
    folder = write(tmp_path, make(files=["source.pdf"], rights_hold=True))
    (folder / "source.pdf").write_bytes(b"%PDF")
    assert any("need tier A without hold" in message for message in errors_of(folder))


def test_undeclared_file_is_reported(tmp_path: Path) -> None:
    folder = write(tmp_path, make())
    (folder / "source.pdf").write_bytes(b"%PDF")
    assert any("directory holds" in message for message in errors_of(folder))


def test_topic_outside_the_vocabulary_is_rejected(tmp_path: Path) -> None:
    folder = write(tmp_path, make(topics=["sample", "other-term"]))
    assert any("['other-term'] are not terms" in m for m in errors_of(folder))


def test_abstract_needs_cleared_basis(tmp_path: Path) -> None:
    card = closed(abstract_included=True)
    folder = write(tmp_path, card, abstract_body(card, source="Source: none."))
    assert any("cleared abstract_basis" in message for message in errors_of(folder))


def test_abstract_section_needs_flag(tmp_path: Path) -> None:
    card = make()
    folder = write(tmp_path, card, abstract_body(card))
    assert any("does not match" in message for message in errors_of(folder))


def test_flag_needs_abstract_section(tmp_path: Path) -> None:
    folder = write(tmp_path, make(abstract_included=True))
    assert any("does not match" in message for message in errors_of(folder))


def test_abstract_under_the_work_license_passes(tmp_path: Path) -> None:
    card = make(abstract_included=True)
    body = abstract_body(card)
    line = f"Source: the work, © 2020 The Authors, [CC BY 4.0]({CC}/licenses/by/4.0/)."
    assert line in body
    assert errors_of(write(tmp_path, card, body)) == []


def test_abstract_from_arxiv_metadata_passes(tmp_path: Path) -> None:
    card = preprint(abstract_included=True)
    body = abstract_body(card)
    assert "Source: arXiv record [2001.00001](https://arxiv.org/abs/2001.00001)" in body
    assert f"metadata under [CC0 1.0]({CC}/publicdomain/zero/1.0/)." in body
    assert errors_of(write(tmp_path, card, body)) == []


def test_abstract_needs_its_source_line(tmp_path: Path) -> None:
    card = make(abstract_included=True)
    folder = write(tmp_path, card, abstract_body(card, source="Source: elsewhere."))
    assert any("must end with the line" in message for message in errors_of(folder))


def test_abstract_must_be_a_block_quote(tmp_path: Path) -> None:
    card = make(abstract_included=True)
    folder = write(tmp_path, card, abstract_body(card, quote="Text."))
    assert any("as a block quote" in message for message in errors_of(folder))


def test_abstract_comes_before_the_summaries(tmp_path: Path) -> None:
    card = make(abstract_included=True)
    source = episteme.abstract_source(card)
    body = BODY + f"\n## Abstract\n\n> Text.\n\n{source}\n"
    folder = write(tmp_path, card, body)
    assert any("sections are" in message for message in errors_of(folder))


def test_work_license_basis_needs_tier_a(tmp_path: Path) -> None:
    card = make(
        rights_license="CC-BY-NC-4.0",
        rights_license_url=f"{CC}/licenses/by-nc/4.0/",
        rights_commercial=False,
        rights_tier="B",
        rights_attribution=None,
    )
    folder = write(tmp_path, card)
    assert any("needs tier A" in message for message in errors_of(folder))


def test_arxiv_basis_needs_identifier(tmp_path: Path) -> None:
    folder = write(tmp_path, preprint(arxiv=None))
    assert any("needs an arxiv identifier" in m for m in errors_of(folder))


def test_with_abstract_adds_section_and_flag(tmp_path: Path) -> None:
    card = make()
    path = write(tmp_path, card) / "card.md"
    text = episteme.with_abstract(
        path.read_text(encoding="utf-8"), card, "  Two\nlines of text.  "
    )
    path.write_text(text, encoding="utf-8")
    assert "\nabstract_included: true\n" in text
    assert "\n## Abstract\n\n> Two lines of text.\n\nSource: the work, " in text
    assert text.index("## Abstract") < text.index("## Scientific Summary")
    assert errors_of(path.parent) == []


def test_with_abstract_refuses_an_uncleared_card(tmp_path: Path) -> None:
    card = closed()
    text = (write(tmp_path, card) / "card.md").read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="not cleared"):
        episteme.with_abstract(text, card, "Text.")


def test_arxiv_abstract_reads_the_record() -> None:
    assert episteme.arxiv_abstract(RECORD) == RECORD_TEXT


def test_arxiv_abstract_needs_the_element() -> None:
    with pytest.raises(ValueError, match="no abstract"):
        episteme.arxiv_abstract("<record><title>Sample</title></record>")


def test_sync_abstracts_adds_then_matches(tmp_path: Path) -> None:
    card = preprint()
    folder = write(tmp_path, card)
    asked: list[str] = []

    def get(url: str) -> str:
        asked.append(url)
        return RECORD

    assert episteme.sync_abstracts(tmp_path, [card], get) == (
        ["doe_2020_sample"],
        [],
        [],
    )
    assert asked == [episteme.ARXIV_RECORD.format("2001.00001")]
    text = (folder / "card.md").read_text(encoding="utf-8")
    assert f"> {RECORD_TEXT}\n" in text
    stored, body = episteme.split_card(text)
    assert stored["abstract_included"] is True
    assert errors_of(folder) == []
    assert episteme.sync_abstracts(tmp_path, [stored], get) == (
        [],
        ["doe_2020_sample"],
        [],
    )
    (folder / "card.md").write_text(
        text.replace(RECORD_TEXT, "Other text."), encoding="utf-8"
    )
    assert episteme.sync_abstracts(tmp_path, [stored], get) == (
        [],
        [],
        ["doe_2020_sample: the abstract differs from the arXiv record"],
    )
    assert body.count("## Abstract") == 1


def test_sync_abstracts_reports_a_failed_request(tmp_path: Path) -> None:
    card = preprint()
    folder = write(tmp_path, card)
    before = (folder / "card.md").read_text(encoding="utf-8")

    def get(url: str) -> str:
        raise OSError(f"no route to {url[:25]}")

    added, matched, problems = episteme.sync_abstracts(tmp_path, [card], get)
    assert (added, matched) == ([], [])
    assert problems == ["doe_2020_sample: no route to https://oaipmh.arxiv.org/"]
    assert (folder / "card.md").read_text(encoding="utf-8") == before


def test_sync_abstracts_skips_other_bases(tmp_path: Path) -> None:
    card = make()
    write(tmp_path, card)

    def get(url: str) -> str:
        raise AssertionError(url)

    assert episteme.sync_abstracts(tmp_path, [card], get) == ([], [], [])


def test_single_summary_heading_is_rejected(tmp_path: Path) -> None:
    folder = write(tmp_path, make(), "\n# Sample\n\n## Summary\n\nText.\n")
    assert any("summary headings" in message for message in errors_of(folder))


def test_summary_headings_keep_their_order(tmp_path: Path) -> None:
    first, second, third = episteme.SUMMARY_HEADINGS
    body = f"\n# Sample\n\n{second}\n\n{first}\n\n{third}\n"
    folder = write(tmp_path, make(), body)
    assert any("summary headings" in message for message in errors_of(folder))


def test_summary_of_100_words_passes(tmp_path: Path) -> None:
    assert errors_of(write(tmp_path, make(), body_with(100))) == []


def test_summary_over_100_words_is_rejected(tmp_path: Path) -> None:
    folder = write(tmp_path, make(), body_with(101))
    assert any("Scientific Summary has 101 words" in m for m in errors_of(folder))


def test_card_license_notice_must_match(tmp_path: Path) -> None:
    folder = write(tmp_path, make(), BODY.replace(episteme.NOTICE, "Other terms."))
    assert any("card license notice" in message for message in errors_of(folder))


def test_card_license_notice_names_the_licensor() -> None:
    assert "© Convective Numerical Systems LLC" in episteme.NOTICE


def test_card_license_section_is_required(tmp_path: Path) -> None:
    body = BODY.split(episteme.NOTICE_HEADING)[0]
    folder = write(tmp_path, make(), body)
    assert any("card license notice" in message for message in errors_of(folder))


def test_unknown_section_is_rejected(tmp_path: Path) -> None:
    folder = write(tmp_path, make(), BODY + "\n## Notes\n\nText.\n")
    assert any("sections are" in message for message in errors_of(folder))


def test_id_must_match_directory(tmp_path: Path) -> None:
    folder = write(tmp_path, make())
    renamed = folder.with_name("doe_2020_other")
    folder.rename(renamed)
    assert any("does not match directory" in message for message in errors_of(renamed))


def test_schema_rejects_unknown_key(tmp_path: Path) -> None:
    folder = write(tmp_path, make(extra=1))
    assert any("Additional properties" in message for message in errors_of(folder))


def test_stray_full_text_is_reported(tmp_path: Path) -> None:
    (tmp_path / "works").mkdir()
    (tmp_path / "paper.pdf").write_bytes(b"%PDF")
    assert episteme.tree_errors(tmp_path) == [
        "paper.pdf: full-text file outside a tier A work"
    ]


def test_paths_named_in_gitignore_are_not_scanned(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(
        "# notes\n/local\ncache/\n*.aux\n", encoding="utf-8"
    )
    for folder in ("local", "notes/cache", "notes/local", ".git"):
        (tmp_path / folder).mkdir(parents=True)
        (tmp_path / folder / "copy.pdf").write_bytes(b"%PDF")
    assert episteme.ignored_names(tmp_path) == ({"local"}, {".git", "cache"})
    assert episteme.tree_errors(tmp_path) == [
        "notes/local/copy.pdf: full-text file outside a tier A work"
    ]


def test_read_release(tmp_path: Path) -> None:
    assert episteme.read_release(tmp_path) == (None, ["CITATION.cff: missing"])
    (tmp_path / "CITATION.cff").write_text(CITATION, encoding="utf-8")
    release, errors = episteme.read_release(tmp_path)
    assert (release, errors) == (RELEASE, [])
    assert release is not None
    assert release.tag == "v0.0.1"
    assert release.base_url == (
        "https://raw.githubusercontent.com/aetelierxyz/episteme/v0.0.1/"
    )


def test_read_release_accepts_an_unquoted_date(tmp_path: Path) -> None:
    text = "version: 1.2.3\ndate-released: 2027-01-02\n"
    (tmp_path / "CITATION.cff").write_text(text, encoding="utf-8")
    assert episteme.read_release(tmp_path)[0] == episteme.Release("1.2.3", "2027-01-02")


def test_read_release_rejects_a_loose_version(tmp_path: Path) -> None:
    text = 'version: "1.0"\ndate-released: "2026-11-25"\n'
    (tmp_path / "CITATION.cff").write_text(text, encoding="utf-8")
    release, errors = episteme.read_release(tmp_path)
    assert release is None
    assert errors == ["CITATION.cff: version must read MAJOR.MINOR.PATCH"]


def test_read_topics(tmp_path: Path) -> None:
    scaffold(tmp_path)
    assert episteme.read_topics(tmp_path) == (TOPICS, [])


@pytest.mark.parametrize(
    ("terms", "message"),
    [
        (["zeta", "alpha"], "sorted by id"),
        (["alpha", "alpha"], "listed twice"),
        (["Alpha"], "not kebab-case"),
    ],
)
def test_read_topics_rejects(tmp_path: Path, terms: list[str], message: str) -> None:
    scaffold(tmp_path)
    entries = [{"id": term, "label": "Label", "definition": "Text."} for term in terms]
    (tmp_path / "schema" / "topics.json").write_text(
        json.dumps({"topics": entries}), encoding="utf-8"
    )
    assert any(message in error for error in episteme.read_topics(tmp_path)[1])


def test_repository_vocabulary_is_valid() -> None:
    topics, errors = episteme.read_topics(episteme.ROOT)
    assert errors == []
    assert "limit-order-book" in topics


def test_load_reports_unused_topic_and_missing_release(tmp_path: Path) -> None:
    scaffold(tmp_path)
    write(tmp_path, closed())
    entries = [*TOPICS.values(), {"id": "spare", "label": "Spare", "definition": "X."}]
    (tmp_path / "schema" / "topics.json").write_text(
        json.dumps({"topics": entries}), encoding="utf-8"
    )
    (tmp_path / "CITATION.cff").unlink()
    cards, errors, warnings = episteme.load(tmp_path, TODAY)
    assert len(cards) == 1
    assert errors == ["CITATION.cff: missing"]
    assert warnings == ["schema/topics.json: 'spare' is used by no work"]


def test_cleared_abstract_not_included_is_a_warning(tmp_path: Path) -> None:
    scaffold(tmp_path)
    write(tmp_path, preprint())
    warnings = episteme.load(tmp_path, TODAY)[2]
    assert warnings == ["works/doe_2020_sample/card.md: cleared abstract not included"]


def test_build_writes_generated_files(tmp_path: Path) -> None:
    scaffold(tmp_path)
    card = make(files=["source.pdf"], abstract_included=True)
    folder = write(tmp_path, card, abstract_body(card))
    (folder / "source.pdf").write_bytes(b"%PDF")
    write(tmp_path, preprint(id="roe_2021_sample"))
    cards, errors, _ = episteme.load(tmp_path, TODAY)
    assert errors == []
    written = {
        path.relative_to(tmp_path).as_posix()
        for path in episteme.build(tmp_path, cards)
    }
    assert written == {
        "index/catalog.jsonl",
        "index/catalog.md",
        "index/manifest.json",
        "REUSE.toml",
        "works/doe_2020_sample/cite.bib",
        "works/roe_2021_sample/cite.bib",
    }
    lines = (tmp_path / "index" / "catalog.jsonl").read_text(encoding="utf-8")
    first = json.loads(lines.splitlines()[0])
    assert first["rights_tier"] == "A"
    assert next(iter(first)) == "schema_version"
    catalog = (tmp_path / "index" / "catalog.md").read_text(encoding="utf-8")
    assert "2 works: 1 tier A, 0 tier B, 1 tier C." in catalog
    assert "Hosted files: 1. Abstracts: 1." in catalog
    assert f"[`CC-BY-4.0`]({CC}/licenses/by/4.0/)" in catalog
    assert "| Abstract | Summaries |" in catalog
    assert "| `sample` | A sample term. | 2 |" in catalog
    assert episteme.load(tmp_path, TODAY)[1] == []
    assert episteme.build(tmp_path, cards) == []


def test_build_stamps_the_schema_id(tmp_path: Path) -> None:
    scaffold(tmp_path)
    schema = tmp_path / "schema" / "work.schema.json"
    schema.write_text(
        SCHEMA_TEXT.replace("/v0.0.1/schema/", "/main/schema/"), encoding="utf-8"
    )
    write(tmp_path, make())
    cards = episteme.load(tmp_path, TODAY)[0]
    written = episteme.build(tmp_path, cards)
    assert schema in written
    assert json.loads(schema.read_text(encoding="utf-8"))["$id"] == (
        "https://raw.githubusercontent.com/aetelierxyz/episteme/v0.0.1/"
        "schema/work.schema.json"
    )


def test_manifest_pins_the_release_and_hashes_files(tmp_path: Path) -> None:
    scaffold(tmp_path)
    folder = write(tmp_path, make(files=["source.pdf"]))
    (folder / "source.pdf").write_bytes(b"%PDF-sample")
    cards = episteme.load(tmp_path, TODAY)[0]
    episteme.build(tmp_path, cards)
    data = json.loads(
        (tmp_path / "index" / "manifest.json").read_text(encoding="utf-8")
    )
    assert data["version"] == "0.0.1"
    assert data["tag"] == "v0.0.1"
    assert data["released"] == "2026-11-25"
    assert data["schema_version"] == 1
    assert data["licensor"] == "Convective Numerical Systems LLC"
    assert data["base_url"] == (
        "https://raw.githubusercontent.com/aetelierxyz/episteme/v0.0.1/"
    )
    assert data["counts"]["works"] == 1
    assert data["counts"]["hosted_files"] == 1
    assert data["counts"]["summaries"] == {"pending": 0, "draft": 0, "reviewed": 1}
    roles = {entry["role"]: entry for entry in data["files"]}
    assert set(roles) == {"catalog", "catalog-table", "schema", "topics", "agent-rules"}
    catalog = (tmp_path / "index" / "catalog.jsonl").read_bytes()
    assert roles["catalog"]["sha256"] == hashlib.sha256(catalog).hexdigest()
    assert roles["catalog"]["bytes"] == len(catalog)
    work = data["works"][0]
    assert work["id"] == "doe_2020_sample"
    card = (folder / "card.md").read_bytes()
    assert work["card"] == {
        "path": "works/doe_2020_sample/card.md",
        "bytes": len(card),
        "sha256": hashlib.sha256(card).hexdigest(),
    }
    assert work["hosted"] == [
        {
            "path": "works/doe_2020_sample/source.pdf",
            "license": "CC-BY-4.0",
            "bytes": 11,
            "sha256": hashlib.sha256(b"%PDF-sample").hexdigest(),
        }
    ]


def test_reuse_map_covers_cards_abstracts_and_hosted_files() -> None:
    hosted = make(files=["source.pdf"], abstract_included=True)
    shared = make(
        id="roe_2021_sample",
        year=2021,
        rights_license="CC-BY-SA-4.0",
        rights_license_url=f"{CC}/licenses/by-sa/4.0/",
        rights_share_alike=True,
        rights_holder=None,
        abstract_included=True,
    )
    reuse = episteme.reuse_toml([hosted, shared, preprint(id="poe_2022_sample")], 2026)
    own = "2026 Convective Numerical Systems LLC"
    assert f'SPDX-FileCopyrightText = "{own}"' in reuse
    assert 'path = ["tools/**"]' in reuse
    assert '".github/**", "schema/**", "index/**"' in reuse
    assert 'path = ["works/*/card.md"]' in reuse
    assert 'SPDX-License-Identifier = "CC0-1.0 AND CC-BY-4.0"' in reuse
    assert (
        'path = ["works/doe_2020_sample/card.md"]\n'
        'precedence = "override"\n'
        f'SPDX-FileCopyrightText = ["{own}", "2020 The Authors"]\n'
        'SPDX-License-Identifier = "CC0-1.0 AND CC-BY-4.0"'
    ) in reuse
    assert (
        'path = ["works/roe_2021_sample/card.md"]\n'
        'precedence = "override"\n'
        f'SPDX-FileCopyrightText = ["{own}", "2021 The Authors"]\n'
        'SPDX-License-Identifier = "CC0-1.0 AND CC-BY-4.0 AND CC-BY-SA-4.0"'
    ) in reuse
    assert (
        'path = ["works/doe_2020_sample/source.pdf"]\n'
        'precedence = "override"\n'
        'SPDX-FileCopyrightText = "2020 The Authors"\n'
        'SPDX-License-Identifier = "CC-BY-4.0"'
    ) in reuse
    assert "poe_2022_sample" not in reuse
    assert reuse.count('precedence = "override"') == 6
    assert reuse.index("works/*/card.md") < reuse.index("works/doe_2020_sample/card.md")


@pytest.mark.parametrize(
    ("authors", "lead"),
    [
        (["Doe, Jane"], "Doe"),
        (["Doe, Jane", "Roe, Rik"], "Doe and Roe"),
        (["Doe, Jane", "Roe, Rik", "Poe, Ann"], "Doe et al."),
    ],
)
def test_lead_author(authors: list[str], lead: str) -> None:
    assert episteme.lead_author(make(authors=authors)) == lead
