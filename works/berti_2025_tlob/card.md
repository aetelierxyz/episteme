---
schema_version: 1
id: berti_2025_tlob
type: preprint
title: 'TLOB: A Novel Transformer Model with Dual Attention for Price Trend Prediction with Limit Order Book Data'
authors:
- Berti, Leonardo
- Kasneci, Gjergji
year: 2025
venue: arXiv
volume: null
issue: null
pages: null
publisher: null
doi: 10.48550/arXiv.2502.15757
arxiv: '2502.15757'
isbn: null
url: https://arxiv.org/abs/2502.15757
url_free: https://arxiv.org/abs/2502.15757
related: []
version: preprint
rights_tier: B
rights_license: CC-BY-NC-SA-4.0
rights_license_url: https://creativecommons.org/licenses/by-nc-sa/4.0/
rights_basis: license
rights_commercial: false
rights_derivatives: true
rights_share_alike: true
rights_holder: null
rights_evidence: 'arXiv OAI-PMH record 2502.15757, license field: http://creativecommons.org/licenses/by-nc-sa/4.0/'
rights_verified: 2026-11-25
rights_attribution: null
rights_hold: false
rights_note: The arXiv PDF (v2) carries ACM template rights text on p.1. The license of the arXiv record governs the arXiv copy.
files: []
abstract_included: true
abstract_basis: arxiv-cc0
keywords: []
topics:
- limit-order-book
- deep-learning
- forecasting
summary_status: pending
---

# TLOB: A Novel Transformer Model with Dual Attention for Price Trend Prediction with Limit Order Book Data

Berti, Leonardo; Kasneci, Gjergji (2025). arXiv:2502.15757.

## Abstract

> Price Trend Prediction (PTP) based on Limit Order Book (LOB) data is a fundamental challenge in financial markets. Despite advances in deep learning, existing models fail to generalize across different market conditions and assets. Surprisingly, by adapting a simple MLP-based architecture to LOB, we show that we surpass SoTA performance; thus, challenging the necessity of complex architectures. Unlike past work that shows robustness issues, we propose TLOB, a transformer-based model that uses a dual attention mechanism to capture spatial and temporal dependencies in LOB data. This allows it to adaptively focus on the market microstructure, making it particularly effective for longer-horizon predictions and volatile market conditions. We also introduce a new labeling method that improves on previous ones, removing the horizon bias. We evaluate TLOB's effectiveness across four horizons, using the established FI-2010 benchmark, a NASDAQ and a Bitcoin dataset. TLOB outperforms SoTA methods in every dataset and horizon. Additionally, we empirically show how stock price predictability has declined over time, -6.68 in F1-score, highlighting the growing market efficiency. Predictability must be considered in relation to transaction costs, so we experimented with defining trends using an average spread, reflecting the primary transaction cost. The resulting performance deterioration underscores the complexity of translating trend classification into profitable trading strategies. We argue that our work provides new insights into the evolving landscape of stock price trend prediction and sets a strong foundation for future advancements in financial AI. We release the code at https://github.com/LeonardoBerti00/TLOB.

Source: arXiv record [2502.15757](https://arxiv.org/abs/2502.15757), metadata under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

## Scientific Summary

Not yet written.

## Engineering Summary

Not yet written.

## Application Summary

Not yet written.

## Card license

Summaries: © Convective Numerical Systems LLC, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Front matter: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). The work keeps the license in `rights_license`.
