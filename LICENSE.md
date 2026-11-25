# Licensing

This repository holds material under different terms. No single license covers it.

Convective Numerical Systems LLC is the copyright holder and the licensor of the tools, the summaries and every other part that is not a third-party work. aetelier.xyz is the name credited for the summaries.

| Material | Path | License |
|---|---|---|
| Tools | `tools/` | [MIT](https://opensource.org/license/mit), © Convective Numerical Systems LLC |
| Card summaries | text under `## Scientific Summary`, `## Engineering Summary`, `## Application Summary` in `works/*/card.md` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), © Convective Numerical Systems LLC |
| Card front matter, citations, index, schema, documentation | front matter of `works/*/card.md`, `works/*/cite.bib`, `index/`, `schema/`, `.github/`, `CITATION.cff`, `*.md` | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| Hosted works | `works/<id>/source.pdf`, `works/<id>/fulltext.md` | the license of the work, stated in `rights_license` and `rights_license_url` of its card |
| Original abstracts | text under `## Abstract` in `works/*/card.md` | the terms in the `Source:` line under the abstract: the license of the work, or [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) for arXiv metadata |

`REUSE.toml` maps every path to its license in machine-readable form. It follows the [REUSE specification](https://reuse.software/spec-3.3/). `LICENSES/` holds the text of each license. A card file carries both `CC0-1.0` and `CC-BY-4.0`. Its `## Card license` section states which part is which.

## Credit for a summary

A summary is the editorial work of aetelier.xyz. Convective Numerical Systems LLC holds its copyright. Reuse of a summary, whole or adapted, carries this credit:

> [Scientific, Engineering or Application] summary of "[title of the work]" by aetelier.xyz, © Convective Numerical Systems LLC, episteme, https://github.com/aetelierxyz/episteme, licensed under CC BY 4.0, https://creativecommons.org/licenses/by/4.0/

State the changes when the text was adapted.

## Third-party works

- Convective Numerical Systems LLC claims no rights in third-party works.
- A work is hosted only when its license allows commercial reuse. Its copyright notice and license statement stay intact. Its card carries the credit line in `rights_attribution`.
- Every other work is described by a card and linked to its publisher. Its text is not hosted.
- An original abstract inside a card belongs to its rights holder. It appears only when `abstract_basis` clears it: under the license of a tier A work, or as arXiv metadata under CC0 1.0. The `Source:` line under the abstract states which.

## License identifiers

Cards use the identifiers of the [SPDX License List](https://spdx.org/licenses/). Each card repeats the official URL in `rights_license_url`.

| Identifier | License | Official URL | Tier |
|---|---|---|---|
| `CC0-1.0` | Creative Commons Zero v1.0 Universal | https://creativecommons.org/publicdomain/zero/1.0/ | A |
| `CC-PDM-1.0` | Creative Commons Public Domain Mark 1.0 Universal | https://creativecommons.org/publicdomain/mark/1.0/ | A |
| `CC-BY-4.0` | Creative Commons Attribution 4.0 International | https://creativecommons.org/licenses/by/4.0/ | A |
| `CC-BY-SA-4.0` | Creative Commons Attribution Share Alike 4.0 International | https://creativecommons.org/licenses/by-sa/4.0/ | A |
| `CC-BY-NC-4.0` | Creative Commons Attribution Non Commercial 4.0 International | https://creativecommons.org/licenses/by-nc/4.0/ | B |
| `CC-BY-NC-SA-4.0` | Creative Commons Attribution Non Commercial Share Alike 4.0 International | https://creativecommons.org/licenses/by-nc-sa/4.0/ | B |
| `CC-BY-ND-4.0` | Creative Commons Attribution No Derivatives 4.0 International | https://creativecommons.org/licenses/by-nd/4.0/ | B |
| `CC-BY-NC-ND-4.0` | Creative Commons Attribution Non Commercial No Derivatives 4.0 International | https://creativecommons.org/licenses/by-nc-nd/4.0/ | B |
| `LicenseRef-arXiv-nonexclusive-1.0` | arXiv.org perpetual non-exclusive license 1.0 | https://arxiv.org/licenses/nonexclusive-distrib/1.0/ | C |
| `LicenseRef-all-rights-reserved` | copyright with no reuse license, free to read or paywalled | none | C |
| `LicenseRef-permission` | written grant of the rights holder, filed as `works/<id>/PERMISSION.md` | none | A or B, by the grant |
| `MIT` | MIT License, for the tools of this repository | https://opensource.org/license/mit | not a tier |

The three `LicenseRef-` identifiers describe terms that SPDX does not list. They describe the work, never a file in this repository.

## Accuracy and contact

Each license was read at the source on the date recorded in `rights_verified`. The data is best effort and is not legal advice.

Questions and removal requests: support@aetelier.xyz. Removal within 5 business days.
