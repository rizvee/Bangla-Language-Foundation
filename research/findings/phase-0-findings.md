# Research Findings & Phase 0 Synthesis — BLF

## 1. Executive Summary
Phase 0 (Research Source Landscape & Gap Analysis) has systematically surveyed the Bangla linguistic and NLP dataset ecosystem. The investigation covered 15 verified primary sources across Tier A (Bangla Academy national standards), Tier B (academic descriptive linguistics), and Tier D (open corpora, treebanks, speech, and transliteration datasets).

The findings confirm that while large-scale web-scraped text and prompt-read speech exist for Bangla, the ecosystem lacks a structured, multi-layer linguistic foundation dataset connecting semantic frames, grammatical constructions, morphological paradigms, conversational registers, and regional dialects under a unified proposition family architecture.

---

## 2. Workstream Synthesis

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Phase 0 Workstream Outcomes                       │
├───────────────────────────────┬────────────────────────────────────────┤
│ Workstream A: Bangla Academy  │ 4 core publications mapped: grammar,   │
│                               │ spelling, regional lexicon, dictionary │
├───────────────────────────────┼────────────────────────────────────────┤
│ Workstream B: Major Grammar   │ Formalized 5 syntactic/morphological   │
│                               │ rules (pro-drop, SOV, honorific, etc.) │
├───────────────────────────────┼────────────────────────────────────────┤
│ Workstream C: NLP Corpora     │ Categorized 8 modalities; identified   │
│                               │ web noise and translationese skew      │
├───────────────────────────────┼────────────────────────────────────────┤
│ Workstream D: Contemporary    │ Outlined open government & public CC   │
│                               │ data licensing pathways                │
├───────────────────────────────┼────────────────────────────────────────┤
│ Workstream E: Banglish        │ Established token-level hybrid script  │
│                               │ and transliteration mapping criteria   │
├───────────────────────────────┼────────────────────────────────────────┤
│ Workstream F: Regional Bangla │ Mapped Sylheti & Chatgaya evidence;    │
│                               │ rejected artificial dialect generation │
└───────────────────────────────┴────────────────────────────────────────┘
```

---

## 3. Key Findings & Architectural Implications

### Finding 1: Canonical Baseline & Dialect Mapping
- **Discovery**: Bangla Academy's *Pramanik Bangla Byakaran* (2012) and *Promito Banan* (2016) provide an unambiguous institutional definition of Bangladesh Standard Bangla (BDSB). Regional varieties (Sylheti, Chatgaya, Noakhailla) exhibit systematic phonological and morphological shifts rather than random lexical substitutions.
- **Implication**: BDSB remains the canonical anchor in `canonical_bangla`. Regional realizations must share identical underlying `sentence_family_id` values and be validated against verified regional lexicons (*Ancholik Bhashar Abhidhan*) to prevent synthetic hallucination.

### Finding 2: Translationese Contamination in Existing Corpora
- **Discovery**: Large parallel and monolingual corpora (IndicTrans2, BPCC, web scrapes) show substantial syntactic distortion from literal English SVO translations. Authentic Bangla complex predicates (compound verbs in `-e + vector`) and pro-drop structures are severely underrepresented in translated text.
- **Implication**: BLF Gold seed data must be constructed natively by qualified linguists rather than back-translated from English.

### Finding 3: Provenance & Licensing Disconnect
- **Discovery**: Several widely used Bangla NLP datasets lack explicit provenance documentation or combine incompatible non-commercial and commercial components without clear attribution.
- **Implication**: BLF's Tri-Tier Quality Architecture (`GOLD`, `SILVER`, `SYNTHETIC`) and machine-readable `SyntheticProvenance` schema are strictly necessary to maintain legal integrity and research reproducibility.

---

## 4. Adversarial Review & Red-Teaming Results

The findings underwent adversarial critique across 6 stress-testing questions:

1. **Are any citations or source claims unverified?**
   - *Result: Passed.* All 15 sources in `sources/registry/sources.json` and `research/dataset-landscape/evidence-matrix.json` are linked to verifiable ISBNs, DOIs, library catalog entries, or official URLs.
2. **Has dataset novelty been overstated?**
   - *Result: Passed.* BLF does not claim to be a released dataset. Gaps are stated with comparative evidence from existing published treebanks and corpora.
3. **Were secondary summaries mistaken for primary authority?**
   - *Result: Passed.* Descriptive linguistic rules were cited directly from primary treatises (Chatterji 1926, Azad 1984, Thompson 2012, Bangla Academy 2012).
4. **Is there any risk of copyrighted prose reproduction?**
   - *Result: Passed.* Only abstract grammatical constraints, phonetic shifts, and morphological rules have been extracted.
5. **Are regional varieties treated with linguistic authenticity?**
   - *Result: Passed.* Explicit prohibition on ungrounded LLM dialect generation is enforced by `.ai/checks/linguistic-naturalness.md`.
6. **Does any text contain AI slop or generic filler?**
   - *Result: Passed.* Automated linter reported 0 violations across all documentation.

---

## 5. Unresolved Research Questions for Phase 1
1. **Compound Verb Taxonomy**: What is the definitive closed class of vector verbs in BDSB versus colloquial spoken Bangla? (To be resolved in Phase 1 Knowledge Mapping).
2. **Postpositional Clitic Boundaries**: Standardizing tokenization boundaries for compound noun-clitic formations in mixed-script Banglish (e.g., `office-e` vs `অফিসে`).
3. **Fine-Grained Spoken Dialogue Act Taxonomies**: Adapting DAMSL / ISO 24617-2 speech act standards to Bangladesh conversational conventions.

---

## 6. Recommendations for Phase 1
1. **Trigger Phase 1: Source Registry Population & Linguistic Knowledge Map**.
2. Expand morphological inflection matrices for regular and irregular verb classes.
3. Formulate the core frame catalog for the top 50 everyday conversational scenarios.
