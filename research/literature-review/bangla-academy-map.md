# Bangla Academy Linguistic Resource Map — Phase 0 Review

## 1. Institutional Context & Authority
The **Bangla Academy** (established 1955, Dhaka) serves as the primary statutory national authority for the Bangla language in Bangladesh. Its publications establish the official normative standards for orthography, grammar, pronunciation, lexicography, and terminology.

This review maps the specific Bangla Academy publications that directly inform the linguistic modeling, normalization rules, and validation checks of the Bangla Language Foundation (BLF).

---

## 2. Core Bangla Academy Publications Catalog

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Bangla Academy Reference Hierarchy                   │
├───────────────────────────────┬────────────────────────────────────────┤
│ 1. Orthography & Spelling     │ Promito Bangla Bananer Niyom (2016)    │
├───────────────────────────────┼────────────────────────────────────────┤
│ 2. Formal Grammar             │ Pramanik Bangla Byakaran (Vols 1-3)    │
├───────────────────────────────┼────────────────────────────────────────┤
│ 3. Lexicography & Bilingual   │ Bengali-English Dictionary (3rd Ed)    │
│    Equivalence                │ Byabaharik Bangla Abhidhan             │
├───────────────────────────────┼────────────────────────────────────────┤
│ 4. Dialectology & Regional    │ Bangladesher Ancholik Bhashar          │
│    Vocabulary                 │ Abhidhan (Shahidullah, Vols 1-3)       │
├───────────────────────────────┼────────────────────────────────────────┤
│ 5. Phonetics & Pronunciation  │ Bangla Uccharon Abhidhan               │
├───────────────────────────────┼────────────────────────────────────────┤
│ 6. Administrative Terminology │ Proshashonik Poribhasha                │
└───────────────────────────────┴────────────────────────────────────────┘
```

---

## 3. Detailed Source Breakdown & Engineering Relevance

### 3.1 Promito Bangla Bananer Niyom (Standard Spelling Rules, 2016)
- **Scope**: Codification of standard modern spelling rules in Bangladesh.
- **Key Linguistic Rules Extracted**:
  - Elimination of non-Tatsama retroflex nasal `ণ` in foreign loanwords and native words (e.g., `কোরআন`, `ইরান`, `ঝরনা`, `গভর্নর`).
  - Restriction of `ষ` to Tatsama words governed by Satwa-Bidhan; foreign and native words strictly use `স` or `শ`.
  - Normalization of invariant long vowels (`ঈ`, `ঊ`) to short vowels (`ই`, `উ`) in non-Tatsama vocabulary.
  - Elimination of unnecessary hasant (`্`) where pronunciation is unambiguously closed or open.
- **BLF Engineering Utility**: Directly implemented in `src/blf/linguistics/normalizer.py` for Unicode NFC string normalization and orthographic consistency auditing.

### 3.2 Pramanik Bangla Byakaran (Standard Bangla Grammar, Vols. 1–3, 2012)
- **Editors**: Rafiqul Islam and Pabitra Sarkar.
- **Scope**: Comprehensive descriptive and normative grammar of standard modern Bangladesh Bangla.
- **Key Linguistic Rules Extracted**:
  - **Volume 1 (Phonetics & Phonology)**: Inherent vowel `/ɔ/` vs `/o/` realization rules; nasalization markers (Chandrabindu); vowel harmony processes.
  - **Volume 2 (Morphology & Parts of Speech)**: Eightfold word class taxonomy (Visheshya, Visheshan, Sarbanam, Kriya, Kriyabisheshan, Anusarga, Jojok, Anonyoyi); nominal case suffixes (`-e`, `-te`, `-ke`, `-re`, `-r`, `-er`); verbal inflection matrices (Tense $\times$ Aspect $\times$ Person $\times$ Politeness).
  - **Volume 3 (Syntax & Discourse)**: Constituent hierarchy; compound verbs (Yukta-Kriya and Mishro-Kriya); passive and impersonal constructions; topic-focus word order permutations.
- **BLF Engineering Utility**: Authoritative baseline for morphological tagging enums in `src/blf/linguistics/tags.py` and syntactic schema validation in `schemas/v0_1/utterance.schema.json`.

### 3.3 Bangladesher Ancholik Bhashar Abhidhan (Regional Dialect Dictionary, 1965)
- **Editor**: Muhammad Shahidullah.
- **Scope**: 3-volume compilation recording over 120,000 regional lexical items across Bangladesh administrative districts.
- **Key Linguistic Data**:
  - Phonetic transcriptions of regional spoken forms in Sylhet, Chittagong, Noakhali, Barishal, Rangpur, Rajshahi, Mymensingh, and Dhaka.
  - Identification of unique nominal and verbal suffixes (e.g., Sylheti `-ain` for 3rd person honorific; Chatgaya `-re` and tonal pitch contours).
- **BLF Engineering Utility**: Establishes ground-truth vocabulary to prevent artificial, hallucinated dialect spellings in synthetic and crowd-annotated regional realizations.

### 3.4 Bangla Uccharon Abhidhan (Bangla Pronunciation Dictionary)
- **Editors**: Naren Biswas et al.
- **Scope**: Phonetic dictionary providing standard BDSB pronunciation for headwords in Bengali phonetic transcription.
- **BLF Engineering Utility**: Phonetic alignment verification for future ASR/TTS and speech-compatible dataset layers.

---

## 4. Legal & Extraction Boundaries
- All Bangla Academy publications reviewed are under institutional copyright.
- BLF extracts abstract grammatical rules, morphological feature tables, phonological mappings, and orthographic constraints.
- No verbatim text pages, full dictionary entries, or multi-paragraph book passages are copied into the repository.
