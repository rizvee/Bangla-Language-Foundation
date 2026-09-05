# BLF Phase 4A — Open-Licensed Micro-Ingestion & Real Pipeline Stress Test Report

## Executive Summary

This report documents the first empirical engineering stress test of the BLF pipeline on real, openly licensed external Bangla language data.

- **Phase**: Phase 4A
- **Execution Tag**: `OPEN_SOURCE_PIPELINE_STRESS_TEST`
- **Primary Source**: `UniversalDependencies/UD_Bengali-BRU` (CC BY-SA 4.0)
- **Secondary Source Audited**: `UniversalDependencies/UD_Bengali-PUD` (CC BY-SA 4.0 shell)
- **Status of Production Corpus**: `NOT_STARTED`
- **Total Gold Records**: `0` (Strict invariant maintained)
- **Human Review**: `DEFERRED_BY_PROJECT_OWNER`

---

## 1. Upstream Source Verification & Checksums

| Repository | Pinned Commit SHA | License | Data Files | Data Checksum (SHA-256) | Status |
|---|---|---|---|---|---|
| `UniversalDependencies/UD_Bengali-BRU` | `368fd57f51577cbb26bde10ac361927a45688d97` | CC BY-SA 4.0 | `bn_bru-ud-test.conllu` (56 sents, 320 tokens) | `8fb0629b35d93561349d7d206d76ab47cbe6bff7f6e52c14244440416f611792` | Verified Empirical Data |
| `UniversalDependencies/UD_Bengali-PUD` | `100d41ed26abf36364fca620509848659a84fa05` | CC BY-SA 4.0 | None (0 .conllu files in repo) | N/A | Shell Repository (Data unreleased upstream) |

### Empirical Discovery on UD_Bengali-PUD:
Upstream inspection revealed that while the `UD_Bengali-PUD` repository has an official `LICENSE.txt` and `README.md` metadata block dating from UD v2.9, no `.conllu` files have been committed to either the `master` or `dev` branches on GitHub. Consequently, micro-ingestion was executed exclusively on `UD_Bengali-BRU`.

---

## 2. Ingestion & Pipeline Stress Results

### 2.1 Ingestion & Parsing
- Parser: `CoNLLUIngestionAdapter` (`src/blf/ingestion/conllu.py`)
- Total Sentences Ingested: **56**
- Total Tokens Ingested: **320**
- Ingestion Parsing Errors: **0**

### 2.2 Reversible Unicode Normalization
- Normalizer: `ReversibleNormalizer(normalize_terminal_period_to_dari=True)`
- Perfect Snapshot Reversibility: **56/56 (100.0%)**
- Operations Applied:


### 2.3 Conservative Text Cleaning
- Cleaner: `ConservativeTextCleaner`
- Average Bengali Character Ratio: **75.71%**
- Removed Control Characters: **0**

### 2.4 Deduplication & Near-Duplicate Detection
- Unique Sentences: **56/56**
- Exact Duplicates: **0**

---

## 3. Universal Dependencies Crosswalk Calibration

### 3.1 Token Coverage
- UPOS Token Coverage: **100.00%** (320/320)
- DEPREL Token Coverage: **100.00%** (320/320)

### 3.2 Observed vs. Unobserved Discrepancy Analysis
Empirical inspection of the 56-sentence BRU treebank identified discrepancies against prior theoretical assumptions in `src/blf/ontology/ud_crosswalk.py`:
- **Unobserved UPOS**: `CCONJ` is not present in the BRU test split (conjunctions are tagged as `SCONJ` or connectives).
- **Unobserved DEPREL**: Relations previously hypothesized as observed in BRU (`obl:tmod`, `compound:svc`, `clf`) do not appear in this 56-sentence empirical sample.
- **Unmapped DEPREL**: Emerging relations present in BRU treebank include `vocative`, `acl:relcl`, `nmod:poss`, `fixed`, `ccomp`, `nsubj:pass`.

---

## 4. Benchmark Contamination & Leakage Audit

- Auditor: `ContaminationChecker(ngram_size=4)`
- Test Items (BRU empirical sentences): **56**
- Training Items (Internal Diagnostic Sentence Families): **22**
- Contamination Status: **`CLEAN`**
- Incidents Detected: **0**
- Checked Dimensions: ``

Zero train-test leakage was detected between the external open-license BRU dataset and the internal BLF diagnostic benchmark suites.

---

## 5. Distributional Diversity Metrics

- **UPOS Diversity**:
  - Unique Tags: `14`
  - Shannon Entropy: `2.9761`
  - Simpson Diversity Index: `0.8414`
- **DEPREL Diversity**:
  - Unique Relations: `27`
  - Shannon Entropy: `3.6945`
  - Simpson Diversity Index: `0.887`

---

## 6. Epistemic Invariants & Gate Status

```
OPEN_SOURCE_PIPELINE_STRESS_TEST = COMPLETE
PRODUCTION_CORPUS               = NOT_STARTED
GOLD_RECORDS                    = 0
HUMAN_REVIEW                    = DEFERRED_BY_PROJECT_OWNER
```
