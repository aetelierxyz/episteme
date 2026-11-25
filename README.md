# episteme

Research Artifacts Compatible with the [aetelier.xyz](https://aetelier.xyz) Platform for Agentic Quant Research

A rights-aware research index for agents, readable by humans. Full text is hosted strictly only where the license allows commercial reuse. Every other work is a citation card that points to its publisher.

# Tiers

| Tier | License of the work                                                                                                                                                                                                                                                                                        | Stored here                       | Use by aetelier agents                       |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | -------------------------------------------- |
| A    | [CC0](https://creativecommons.org/publicdomain/zero/1.0/), [public domain](https://creativecommons.org/publicdomain/mark/1.0/), [CC BY](https://creativecommons.org/licenses/by/4.0/), [CC BY-SA](https://creativecommons.org/licenses/by-sa/4.0/)                                                         | card, `source.pdf`, `fulltext.md` | retrieve, quote, transform, with attribution |
| B    | any NonCommercial or NoDerivatives variant: [CC BY-NC](https://creativecommons.org/licenses/by-nc/4.0/), [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/), [CC BY-ND](https://creativecommons.org/licenses/by-nd/4.0/), [CC BY-NC-ND](https://creativecommons.org/licenses/by-nc-nd/4.0/) | card, link                        | card only                                    |
| C    | no reuse license: [arXiv default license](https://arxiv.org/licenses/nonexclusive-distrib/1.0/), SSRN, author copies, paywalled                                                                                                                                                                            | card, link                        | card only                                    |

A card holds the citation, the DOI or URL, the license and where it was read, keywords, topics from one shared vocabulary, and three summaries written by the curator: scientific, engineering, application, at most 100 words each. `summary_status` tells whether they are written. An original abstract appears only when it is cleared: by the license of the work, by the CC0 dedication of arXiv metadata, or by written permission. The line under an abstract names its source and its terms.

One rule holds everywhere: a full text is present only if commercial reuse is permitted.

# Layout

| Path | Holds |
|---|---|
| `works/<id>/card.md` | one work: front matter, cleared abstract, three summaries |
| `works/<id>/cite.bib` | BibTeX, generated |
| `works/<id>/source.pdf`, `works/<id>/fulltext.md` | tier A only |
| `works/<id>/PERMISSION.md` | written grant of the rights holder, when that is the basis |
| `index/manifest.json` | release, schema version, sha256 of every card and hosted file, generated; entry point for agents |
| `index/catalog.jsonl` | one record per work, generated |
| `index/catalog.md` | the same list as a table, generated |
| `schema/work.schema.json` | fields of a card |
| `schema/topics.json` | topic vocabulary shared by all works |
| `tools/episteme.py` | validator and builder |
| `AGENTS.md` | rules for agents |
| `CITATION.cff` | citation metadata, release version and date |
| `SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md` | policies |
| `LICENSE.md`, `LICENSES/`, `REUSE.toml` | license map, license texts, per-path licenses |

# Use

- Agents: read `AGENTS.md`, then `index/manifest.json`, then `index/catalog.jsonl`.
- Pinned address of any file: `https://raw.githubusercontent.com/aetelierxyz/episteme/<tag>/<path>`. Releases are tagged `v` plus the version, as in `v0.0.1`.
- Humans: open https://aetelier.xyz/docs/research/library/ or `index/catalog.md`.
- Validate a copy: `uv run tools/episteme.py check`

# Rights and removal

Each license was read at the source on the date recorded in the card. The data is best effort and is not legal advice. Convective Numerical Systems LLC claims no rights in third-party works.

Rights holders: write to support@aetelier.xyz. Removal within 5 business days.

# Contributions

Issues only. See `CONTRIBUTING.md`.

# Add a work

Maintainers add each work with these steps.

1. Pick the version with the most open license.
2. Read the license at the source. In order of weight: the statement inside the file, the license field of the arXiv record, the license array of the Crossref record, the record of an institutional repository.
3. Create `works/<id>/card.md` and fill every key of `schema/work.schema.json`.
4. Set the rights fields from the first table below.
5. Tier A without hold: add `source.pdf`, optionally `fulltext.md`.
6. Take `topics` from `schema/topics.json`.
7. Add the abstract only when the second table clears it.
8. Write each summary from the paper. Do not paraphrase the abstract.
9. Run the check, then the build: `uv run tools/episteme.py check`, `uv run tools/episteme.py build`.

| License of the version | `rights_license` | `rights_basis` | Tier |
|---|---|---|---|
| CC0 | `CC0-1.0` | `license` | A |
| Public domain | `CC-PDM-1.0` | `public-domain` | A |
| CC BY | `CC-BY-4.0` | `license` | A |
| CC BY-SA | `CC-BY-SA-4.0` | `license` | A |
| CC BY-NC | `CC-BY-NC-4.0` | `license` | B |
| CC BY-NC-SA | `CC-BY-NC-SA-4.0` | `license` | B |
| CC BY-ND | `CC-BY-ND-4.0` | `license` | B |
| CC BY-NC-ND | `CC-BY-NC-ND-4.0` | `license` | B |
| arXiv default license | `LicenseRef-arXiv-nonexclusive-1.0` | `none` | C |
| No license stated | `LicenseRef-all-rights-reserved` | `none` | C |
| Written grant | `LicenseRef-permission` | `permission` | A or B, by the grant |

Set `rights_hold: true` when two sources state different rights. A work on hold hosts no file.

| `abstract_basis` | When | Text comes from |
|---|---|---|
| `work-license` | the described version is tier A without hold | the licensed file of the work |
| `arxiv-cc0` | the work has an arXiv record | that record, through `uv run tools/episteme.py abstracts` |
| `permission` | the rights holder granted it in writing | the work |
| `none` | every other case | nothing |

# License

See `LICENSE.md`. Card summaries: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), © Convective Numerical Systems LLC, credit to aetelier.xyz. Card front matter, index, schema and documentation: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Tools: [MIT](https://opensource.org/license/mit), © Convective Numerical Systems LLC. Each hosted work and each abstract: its own terms, stated and linked in its card.
