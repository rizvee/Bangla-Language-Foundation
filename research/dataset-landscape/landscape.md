# Bangla Dataset & Corpus Landscape — Phase 0 Review

## 1. Overview & Scope
This landscape document reviews the existing empirical dataset ecosystem for the Bangla language. The analysis surveys open-access corpora, academic benchmark datasets, speech archives, transliteration collections, and parallel translation resources across international and Bangladesh repositories (ACL Anthology, Hugging Face, Universal Dependencies, Bengali.AI, AI4Bharat).

---

## 2. Taxonomy of Existing Bangla Language Resources

Existing Bangla NLP resources can be classified into eight distinct functional modalities:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Existing Bangla Dataset Modalities                  │
├───────────────────┬───────────────────┬─────────────────────────────────┤
│ 1. Monolingual    │ 2. Syntactic      │ 3. Parallel Translation         │
│    Web Corpora    │    Treebanks      │    (Bitext)                     │
│    (IndicCorp v2, │    (UD bn_bengal, │    (IndicTrans, BPCC,           │
│     OSCAR, mC4)   │     UD bn_iu)     │     BanglaNMT)                  │
├───────────────────┼───────────────────┼─────────────────────────────────┤
│ 4. Speech & Audio │ 5. Transliteration│ 6. Code-Mixed & Social          │
│    (Bengali.AI,   │    & Banglish     │    (SentiraBangla,              │
│     Common Voice) │    (QCRI Banglish)│     Banglish Sentiment)         │
├───────────────────┴───────────────────┴─────────────────────────────────┤
│ 7. Task Benchmarks (XNLI-bn, TyDi QA-bn, BELEBELE, IndicGLUE)          │
│ 8. Lexicographical Glossaries (Bangla Academy Dictionaries, ODBL)       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Systematic Analysis by Resource Category

### 3.1 Monolingual Web & Pretraining Corpora
- **Major Datasets**: `IndicCorp v2 (Bengali)` (1.2B tokens, CC0), `OSCAR Bengali` (Common Crawl filtered), `mC4 Bengali`.
- **Strengths**: High volume of text; broad vocabulary coverage; suitable for self-supervised language model pre-training.
- **Critical Limitations**:
  - Unstructured text strings lacking syntactic or semantic annotations.
  - High contamination of machine-translated web content (translationese) and repetitive advertising text.
  - Skewed toward formal journalistic and encyclopedic registers; negligible coverage of everyday colloquial conversation.
  - Zero sentence family clustering or pragmatic variation tracking.

### 3.2 Syntactic & Dependency Treebanks
- **Major Datasets**: `Universal Dependencies Bengali (bn_bengal)` (1,048 sentences, CC-BY-SA-4.0), `UD Bengali-IU` (derived from Indian Language Treebank project).
- **Strengths**: Standardized Universal Dependencies (UD) morphosyntactic features and dependency relations.
- **Critical Limitations**:
  - Extremely limited size (barely 1,000 sentences for `bn_bengal`).
  - Restricted to formal written prose from news and literature.
  - Lacks semantic frame labeling, semantic roles, and dialogue context.
  - No representation of regional dialects or Romanized Banglish.

### 3.3 Parallel Translation Corpora
- **Major Datasets**: `IndicTrans2 / Bharat Parallel Corpus (BPCC)` (8.5M pairs, CC-BY-4.0), `Flores-200 (ben_Beng)`, `BanglaNMT`.
- **Strengths**: Large-scale sentence alignment between Bangla and English / Indic languages.
- **Critical Limitations**:
  - Dominated by synthetic back-translation and Wikipedia text.
  - Translationese artifacts: rigid Subject-Verb-Object (SVO) English structures translated literally into Bangla, distorting natural Bengali constituent order (SOV with focus-driven movement).
  - Absence of multi-layer morphology or deep semantic frame annotations.

### 3.4 Speech & Spoken Language Corpora
- **Major Datasets**: `Bengali.AI Speech Corpus` (1,200+ hours, CC0-1.0), `Mozilla Common Voice (bn)` (~500 hours).
- **Strengths**: Rich acoustic diversity across 64 administrative districts of Bangladesh; crowdsourced native speaker demographics.
- **Critical Limitations**:
  - Prompt texts are predominantly read from Wikipedia or newspaper sentences rather than spontaneous multi-turn dialogue.
  - Text transcripts lack fine-grained morphological parsing, semantic roles, or dialogue act tags.

### 3.5 Transliteration & Code-Mixed Corpora
- **Major Datasets**: `QCRI Banglish-to-Bengali Transliteration Dataset` (125k pairs, CC-BY-4.0), `SentiraBangla` (21k code-mixed sentences, CC-BY-NC-4.0).
- **Strengths**: Empirical capture of authentic Romanized social media text and Bangla-English mixed utterances.
- **Critical Limitations**:
  - Focus is confined to string-to-string character transliteration or coarse sentiment polarity labels.
  - Lacks token-level script classification, morphological decomposition of mixed words (e.g., English noun + Bengali locative suffix `library-te`), or semantic role alignment.

---

## 4. Evidence Matrix & Licensing Summary

| Resource ID | Resource Name | Size / Units | Primary License | Redistribution Rights | Human Verified |
|---|---|---|---|---|---|
| `BA-GRAM-2012` | Pramanik Bangla Byakaran | 3 vols (~1800 pp) | All-Rights-Reserved | Derived features only | Yes |
| `BA-REGDICT-1965` | Ancholik Bhashar Abhidhan | 3 vols (120k words) | All-Rights-Reserved | Derived features only | Yes |
| `UD-BN-BENGAL-2023` | UD Bengali Treebank | 1,048 sentences | CC-BY-SA-4.0 | Open redistribution | Yes |
| `INDICCORP-V2-BN` | IndicCorp v2 (Bengali) | 1.2B tokens | CC0-1.0 | Open redistribution | No (Automated) |
| `BENGLAI-SPEECH-2022`| Bengali.AI Speech Corpus | 1,200 hours audio | CC0-1.0 | Open redistribution | Yes |
| `BANGLISH-TRANSLIT-2021` | Banglish Transliteration | 125k sentence pairs | CC-BY-4.0 | Open redistribution | Yes |
| `SENTIRABANGLA-2022` | SentiraBangla Code-Mixed | 21,000 sentences | CC-BY-NC-4.0 | Derived features only | Yes |
| `INDICTRANS-2022` | IndicTrans / BPCC (bn) | 8.5M pairs | CC-BY-4.0 | Open redistribution | Partial (Synthetic) |

For complete machine-readable field records, see [evidence-matrix.json](evidence-matrix.json).
