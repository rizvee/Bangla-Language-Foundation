# Research Findings & Phase 0 Synthesis — BLF

## 1. Executive Summary
Phase 0 (Research Source Landscape & Gap Analysis) and Phase 0.1 (Source Integrity Recovery & Evidence Hardening) have systematically surveyed the Bangla linguistic and NLP dataset ecosystem. The investigation established a field-level verified registry of 16 fully verified primary sources and 1 partially verified source across Tier A (Bangla Academy statutory standards), Tier B (academic descriptive linguistics), and Tier D (open corpora, treebanks, speech archives, transliteration benchmarks, and code-mixed datasets), alongside 4 quarantined historical records.

The hardened findings confirm that while web-scraped text (Bangla2B+, IndicCorp v2) and prompt-read speech (Bengali.AI Common Voice) exist for Bangla, the ecosystem exhibits acute resource deficits in syntactic treebanks (only 56 sentences in `UD_Bengali-BRU`), frame semantics, connected regional dialect syntax, and token-level mixed-script alignment.

---

## 2. Workstream Synthesis

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Phase 0 Workstream Outcomes                       │
├───────────────────────────────┬────────────────────────────────────────┤
│ Workstream A: Bangla Academy  │ 4 core publications verified: grammar, │
│                               │ spelling, regional lexicon, dictionary │
├───────────────────────────────┼────────────────────────────────────────┤
│ Workstream B: Major Grammar   │ Formalized syntactic/morphological     │
│                               │ rules (pro-drop, SOV, honorific, etc.) │
├───────────────────────────────┼────────────────────────────────────────┤
│ Workstream C: NLP Corpora     │ Verified Bangla2B+, BanglaNMT,         │
│                               │ IndicCorp v2, UD BRU/PUD, Common Voice │
├───────────────────────────────┼────────────────────────────────────────┤
│ Workstream D: Contemporary    │ Mapped open CC0/CC-BY data pathways    │
├───────────────────────────────┼────────────────────────────────────────┤
│ Workstream E: Banglish        │ Verified BanglaTLit (EMNLP 2024) and   │
│                               │ BnSentMix (LoResLM 2025) benchmarks    │
├───────────────────────────────┼────────────────────────────────────────┤
│ Workstream F: Regional Bangla │ Verified Shahidullah (1965) and SOAS   │
│                               │ Sylheti Project (Simard et al., 2014)  │
└───────────────────────────────┴────────────────────────────────────────┘
```

---

## 3. Key Findings & Architectural Implications

### Finding 1: Canonical Baseline & Dialect Mapping
- **Discovery**: Bangla Academy's *Pramanik Bangla Byakaran* (2012) and *Promito Banan* (2016) provide the definitive statutory definition of Bangladesh Standard Bangla (BDSB). Regional varieties (Sylheti, Chatgaya, Noakhailla) exhibit systematic phonological and morphological shifts documented in Shahidullah's *Ancholik Bhashar Abhidhan* (1965) and academic documentation (Simard et al., 2014).
- **Implication**: BDSB remains the canonical anchor in `canonical_bangla`. Regional realizations must share identical underlying `sentence_family_id` values and be validated against verified regional lexicons to prevent synthetic hallucination.

### Finding 2: Severe Syntactic Treebank Deficit
- **Discovery**: The official native Bangladesh Universal Dependencies treebank (`UD_Bengali-BRU`) contains only 56 sentences and 320 tokens. Other available treebanks (`UD_Bengali-PUD`) are translated parallel corpora from English/German.
- **Implication**: BLF's multi-layer syntactic construction modeling will fill a major empirical void in native Bangladesh computational syntax.

### Finding 3: Provenance & Epistemic Audit Discipline
- **Discovery**: In Phase 0.1, automated cross-identifier checks detected misattributed paper IDs in early candidate drafts (e.g. associating Bengali.AI with unrelated arXiv ID 2206.14051 instead of real 2206.14053; false ACL Anthology IDs for transliteration/code-mixing).
- **Implication**: Field-level verification (`VERIFIED`, `PARTIALLY_VERIFIED`, `QUARANTINED`) and machine-readable evidence metadata are permanently enforced via `scripts/audit_sources.py` and regression tests in `tests/test_source_audit.py`.

---

## 4. Adversarial Review & Red-Teaming Results

The source registry and findings underwent adversarial audit:

1. **Are all verified citations linked to primary evidence?**
   - *Result: Passed.* Every `VERIFIED` record in `sources/registry/sources.json` contains a structured `verification` block with primary evidence URLs, accessed dates, and verified fields.
2. **Were false historical identifiers quarantined with an audit trail?**
   - *Result: Passed.* 4 records were quarantined and recorded in `sources/registry/source-audit.jsonl`.
3. **Were ungrounded regional citations removed?**
   - *Result: Passed.* Composite or unverified citations (e.g. `CHATGAYA-PHONO-2018`) were quarantined.
4. **Are gap claims calibrated to evidence?**
   - *Result: Passed.* Unproven claims regarding SVO calque distortion were downgraded to `[NOT_YET_VERIFIED]` empirical hypotheses, and universal absence claims were calibrated to search bounds.

---

## 5. Phase 0 Acceptance Status
- With all 16 primary sources field-level verified, regression tests passing, and quarantined audit ledgers established, **Phase 0 and Phase 0.1 evidence hardening are complete and accepted**.
