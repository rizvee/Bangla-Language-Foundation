# Bangla Dataset & Corpus Landscape — Phase 0 Review

## 1. Overview & Scope
This landscape document reviews the existing empirical dataset ecosystem for the Bangla language. The analysis surveys open-access corpora, academic benchmark datasets, speech archives, transliteration collections, and parallel translation resources across international and Bangladesh repositories (ACL Anthology, Hugging Face, Universal Dependencies, Bengali.AI, AI4Bharat, BUET CSE NLP).

---

## 2. Taxonomy of Existing Bangla Language Resources

Existing Bangla NLP resources can be classified into eight distinct functional modalities:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Existing Bangla Dataset Modalities                  │
├───────────────────┬───────────────────┬─────────────────────────────────┤
│ 1. Monolingual    │ 2. Syntactic      │ 3. Parallel Translation         │
│    Web Corpora    │    Treebanks      │    (Bitext)                     │
│    (Bangla2B+,    │    (UD bn_bru,    │    (BanglaNMT, BPCC,            │
│     IndicCorp v2) │     UD bn_pud)    │     Samanantar)                 │
├───────────────────┼───────────────────┼─────────────────────────────────┤
│ 4. Speech & Audio │ 5. Transliteration│ 6. Code-Mixed & Social          │
│    (Bengali.AI    │    & Banglish     │    (BnSentMix,                  │
│     Common Voice) │    (BanglaTLit)   │     SentiraBangla [Quarantined])│
├───────────────────┴───────────────────┴─────────────────────────────────┤
│ 7. Task Benchmarks (XNLI-bn, TyDi QA-bn, BELEBELE, IndicGLUE)          │
│ 8. Lexicographical Glossaries (Bangla Academy Dictionaries, ODBL)       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Systematic Analysis by Resource Category

### 3.1 Monolingual Web & Pretraining Corpora
- **Major Datasets**: `Bangla2B+` (BUET CSE NLP, 27.5 GB web text from 110 Bangladesh sites, CC-BY-NC-SA-4.0), `IndicCorp v2 (Bengali)` (AI4Bharat, 1.2B tokens, CC0-1.0), `OSCAR Bengali`.
- **Strengths**: Large volume of text; broad vocabulary coverage; suitable for self-supervised language model pre-training.
- **Critical Limitations**:
  - Unstructured text strings lacking syntactic or semantic frame annotations.
  - Skewed toward formal journalistic and encyclopedic registers; negligible coverage of everyday colloquial conversation.
  - Zero sentence family clustering or pragmatic variation tracking.

### 3.2 Syntactic & Dependency Treebanks
- **Major Datasets**: `Universal Dependencies Bengali-BRU (bn_bru)` (Begum Rokeya University, 56 sentences / 320 tokens, CC-BY-SA-4.0), `UD Bengali-PUD (bn_pud)` (1,000 parallel sentences).
- **Strengths**: Standardized Universal Dependencies (UD) morphosyntactic features and dependency relations.
- **Critical Limitations**:
  - Severe size limitation in Bangladesh native data (`UD_Bengali-BRU` contains only 56 sentences).
  - Parallel treebanks (`UD_Bengali-PUD`) are translated from foreign English/German sentences.
  - Lacks semantic frame labeling, semantic roles, and dialogue context.
  - No representation of regional dialects or Romanized Banglish.

### 3.3 Parallel Translation Corpora
- **Major Datasets**: `BanglaNMT` (BUET CSE NLP, 2.75M parallel pairs, CC-BY-NC-SA-4.0), `Bharat Parallel Corpus Collection (BPCC) Bengali Split` (AI4Bharat, CC-BY-4.0).
- **Strengths**: Curated sentence alignment between Bangla and English.
- **Critical Limitations**:
  - Significant synthetic and mined components in web-scale bitext collections.
  - Absence of multi-layer morphology or deep semantic frame annotations.

### 3.4 Speech & Spoken Language Corpora
- **Major Datasets**: `Bengali Common Voice Speech Dataset` (Bengali.AI / Mozilla Common Voice; Alam et al., 2022; arXiv:2206.14053; ~500,000 validated recordings, CC0-1.0).
- **Strengths**: Rich acoustic diversity across 64 administrative districts of Bangladesh; crowdsourced native speaker demographics.
- **Critical Limitations**:
  - Prompt texts are predominantly read from Wikipedia or newspaper sentences rather than spontaneous multi-turn dialogue.
  - Text transcripts lack fine-grained morphological parsing, semantic roles, or dialogue act tags.

### 3.5 Transliteration & Code-Mixed Corpora
- **Major Datasets**: `BanglaTLit` (Fahim et al., 2024; EMNLP 2024 Findings; 42.7k annotated pairs + 245.7k PT corpus, MIT License), `BnSentMix` (Alam et al., 2025; LoResLM 2025; 20,000 code-mixed samples, Apache-2.0 repository license).
- **Strengths**: Verified benchmarks for Romanized Banglish back-transliteration and code-mixed social sentiment classification.
- **Critical Limitations**:
  - Focus is confined to string transliteration or 4-class sentiment polarity.
  - Lacks token-level script classification, morphological decomposition of hybrid words (`office-e`, `table-ta`), or semantic frame alignment.
  - Underlying social media content carries platform-specific redistribution restrictions.

---

## 4. Evidence Matrix & Licensing Summary

| Resource ID | Resource Name | Size / Units | Primary License | Redistribution Rights | Verification Status |
|---|---|---|---|---|---|
| `BA-GRAM-2011` | Pramita Bangla Bhashar Byakaran | 2 vols | Copyrighted | Derived features only | `VERIFIED` |
| `BA-SPELL-2016` | Promito Bangla Bananer Niyom | Rulebook (ISBN 984-07-5531-5) | Statutory Public Notice | Derived features only | `VERIFIED` |
| `BA-REGDICT-1965` | Ancholik Bhashar Abhidhan | 3 vols (120k words) | Copyrighted | Derived features only | `VERIFIED` |
| `BA-BENG-ENG-2019` | Bengali-English Dictionary | 1 vol (1,248 pp) | Copyrighted | Derived features only | `VERIFIED` |
| `ODBL-SKC-1926` | Origin & Development of Bengali | 2 vols (1,179 pp) | Public Domain | Derived features only | `VERIFIED` |
| `AZAD-SYNTAX-1984` | Bakkototto (Bangla Syntax) | 1 vol (320 pp) | Copyrighted | Derived features only | `VERIFIED` |
| `THOMPSON-GRAM-2012`| Bengali: Comprehensive Grammar | 1 vol (672 pp) | Copyrighted | Derived features only | `VERIFIED` |
| `UD-BN-BRU-2021` | UD Bengali-BRU Treebank | 56 sentences | CC-BY-SA-4.0 | Open redistribution | `VERIFIED` |
| `UD-BN-PUD-2017` | Parallel UD Bengali Treebank | 1,000 sentences | CC-BY-SA-4.0 | Open redistribution | `VERIFIED` |
| `BANGLA2B-2022` | Bangla2B+ / BanglaBERT Pretraining | 27.5 GB text | CC-BY-NC-SA-4.0 | Derived features only | `VERIFIED` |
| `BANGLANMT-2020` | BanglaNMT Parallel Corpus | 2.75M pairs | CC-BY-NC-SA-4.0 | Derived features only | `VERIFIED` |
| `INDICCORP-V2-BN` | IndicCorp v2 (Bengali) | 1.2B tokens | CC0-1.0 | Open redistribution | `VERIFIED` |
| `BENGLAI-SPEECH-2022`| Bengali Common Voice Speech | ~500,000 recordings| CC0-1.0 | Open redistribution | `VERIFIED` |
| `BANGLATLIT-2024` | BanglaTLit Transliteration | 42.7k pairs + 245k PT| MIT | Open redistribution | `VERIFIED` |
| `BNSENTMIX-2025` | BnSentMix Code-Mixed Dataset | 20,000 sentences | Apache-2.0 | Restricted review | `VERIFIED` |
| `BPCC-BENGALI-2023` | BPCC Bengali Parallel Component | Mined + Human split | CC-BY-4.0 | Open redistribution | `PARTIALLY_VERIFIED` |
| `SOAS-SYLHETI-2014` | SOAS Sylheti Documentation | Journal Monograph | Copyrighted | Derived features only | `VERIFIED` |

For complete machine-readable field records and artifact-specific breakdowns, see [evidence-matrix.json](evidence-matrix.json).
