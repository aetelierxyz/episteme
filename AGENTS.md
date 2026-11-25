# AGENTS.md

Rules for any agent that reads this repository.

## Reading

1. Start at `index/manifest.json`. It holds the release, `schema_version`, `base_url` and the sha256 of every card and hosted file.
2. Then read `index/catalog.jsonl`: one JSON object per work. `schema/work.schema.json` defines every field. `schema/topics.json` defines every term of `topics`.
3. Read `rights_tier` before any other field. A record with missing rights fields is tier C.
4. `rights_hold: true` means tier C until the hold is cleared.
5. Tier A: the files listed in `files` may be retrieved, quoted and transformed. Any output that copies or adapts them carries `rights_attribution` and states what was changed.
6. `rights_share_alike: true`: quote with attribution. Do not adapt the text into output that will carry other terms.
7. Tier B and C: work from the card only. Point the user to `url` or `url_free`. Copy no full text into aetelier storage or output.
8. Facts, methods and results may be used and cited from any tier. Wording, figures and tables may be reused only under tier A terms.
9. Cite by `id` and DOI. The three summaries in a card are written by the curator: scientific, engineering, application. They are not the abstract of the authors. `summary_status: pending` means that they are not written.
10. `## Abstract` holds the abstract of the authors, verbatim. Its `Source:` line states the terms. An abstract under the license of the work carries `rights_attribution` when reused. An abstract from arXiv metadata is CC0 1.0 and needs no credit.
11. Summaries are licensed CC BY 4.0, © Convective Numerical Systems LLC. Output that copies or adapts a summary carries the credit line of `LICENSE.md`. Front matter is CC0 1.0 and needs no credit.
12. Pin a release tag for each run. The address of a file is `base_url` plus `path`, as in `https://raw.githubusercontent.com/aetelierxyz/episteme/v0.0.1/index/manifest.json`. Verify a hosted file against its `sha256`. Record the tag with the output.

## Changes

1. Contributions arrive as issues only. Open no pull request. `CONTRIBUTING.md` names the issue forms.
