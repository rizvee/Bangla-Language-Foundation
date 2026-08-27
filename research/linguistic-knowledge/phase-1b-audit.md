# Phase 1A & Phase 1B Linguistic Correctness & Morphotactics Audit

**Audit Date**: 2026-08-28  
**Auditing Agent**: `bangla-linguist` & `adversarial-reviewer`  
**Scope**: All Phase 1A evidence items, claims, rules, examples, and Phase 1B morphological engines and paradigm catalogs.

---

## 1. Audit Executive Summary

| Audit Domain | Total Inspected | Confirmed | Corrected / Refined | Restricted | Deprecated Assumptions |
|---|---|---|---|---|---|
| **Linguistic Claims** | 36 claims | 33 | 3 | 0 | 0 |
| **Declarative Rules** | 20 rules | 18 | 2 | 0 | 0 |
| **Nominal Morphotactics** | 4 paradigms | 3 | 1 (stacking rule) | 1 (classifier-plural co-occurrence) | 1 (unrestricted concatenation) |
| **Pronominal System** | 5 paradigms | 4 | 1 (human locatives) | 1 (synthetic locative on personal pronouns) | 0 |
| **Verbal Conjugation** | 4 paradigms | 4 | 0 | 0 | 0 |

---

## 2. Detailed Findings & Classifications

### 2.1 Finding AUD-LING-001: Classifier-Plural Mutually Exclusive Morphotactics `[DEPRECATED ASSUMPTION & CORRECTED]`
- **Previous Assumption**: The theoretical suffix ordering formula was described as:
  $$\text{[NounRoot]} + \text{[Classifier]} + \text{[Plural]} + \text{[Case]} + \text{[Clitic]}$$
- **Linguistic Reality (BA-GRAM-2011 Vol. 1, p. 158; Thompson 2012, p. 70)**:
  In standard Bangla (BDSB), singular numeral classifiers (`-ta`, `-ti`, `-khana`, `-jon`) and plural inflectional markers (`-ra`/`-era`, `-gulo`/`-gula`, `-shob`, `-der`) are **mutually exclusive** when attaching directly to a single noun stem.
  - Ungrammatical: $*\text{বইটাতোলা}$, $*\text{মানুষটিরা}$, $*\text{কলমটাগুলো}$ (*double determination / clash of singular classifier and plural marker*).
  - Grammatical:
    1. Singular Definite: $\text{বই} + \text{টা} + \text{র} \rightarrow$ **বইটার** (`[Root] + [SingularClassifier] + [Case]`).
    2. Plural Definite/Collective: $\text{বই} + \text{গুলো} + \text{র} \rightarrow$ **বইগুলোর** (`[Root] + [PluralMarker] + [Case]`).
    3. External Quantifier: $\text{তিনটি} + \text{বই} + \text{এর} \rightarrow$ **তিনটি বইয়ের** (`[Quantifier + Classifier] + [BareRoot] + [Case]`).
- **Action Taken**:
  - Deprecated the linear formula `Noun + Classifier + Plural + Case`.
  - Formalized the bifurcated template in `NominalDeclensionEngine` and documentation.
  - Added negative regression test asserting that direct stacking of singular classifier and plural suffix is rejected.

---

### 2.2 Finding AUD-LING-002: Synthetic Locative on Personal Pronouns `[RESTRICTED & ANNOTATED]`
- **Previous Assumption**: Complete matrix included synthetic `-te` on all personal pronouns (`আমাতে`, `তোমাতে`, `আপনাতে`, `তাদেরতে`, `কাদেরতে`).
- **Linguistic Reality (Azad 1984, p. 145; Thompson 2012, p. 95)**:
  In natural conversational BDSB, personal pronouns resist direct synthetic locative case `-te`. Forms like *আমাতে* or *তোমাতে* are archaic/literary/poetic (*Sadhu/Bhab-bikashe*).
  - Natural BDSB expresses personal pronominal locative via postpositional phrases:
    - *আমার মধ্যে* / *আমাদের মাঝে* (*among/in me/us*)
    - *আমার কাছে* / *তাদের কাছে* (*with me/them*)
  - Conversely, demonstrative and inanimate pronouns take synthetic locative naturally and productively:
    - *এতে* (*in this*), *ওতে* (*in that*), *তাতে* (*in that/thereby*), *কিসে* (*in what*), *যাতে* (*in which / so that*).
- **Action Taken**:
  - Annotated personal pronominal `-te` forms in `pronominal_paradigms.json` with register label `literary_marked`.
  - Added canonical conversational postpositional equivalents in documentation and realization rules.

---

### 2.3 Finding AUD-LING-003: Citation Lemma vs Morphological Root Distinction `[CONFIRMED & HARDENED]`
- **Linguistic Grounding**:
  In Indo-Aryan and Bangla linguistics, the citation entry in standard lexicons is the non-finite verbal noun in `-a` (*করা*, *যাওয়া*, *খাওয়া*, *দেওয়া*, *বলা*), while the computational morphological engine operates upon the bound root (*kor-*, *ja-*, *kha-*, *de-*, *bol-*).
- **Action Taken**:
  - Confirmed that `VerbalConjugatorEngine` accepts both citation lemmas (`করা`) and lexical roots (`কর`), maintaining clear separation between lexical citations and bound morphophonological stems without inventing artificial abstract roots.

---

### 2.4 Finding AUD-LING-004: Differential Object Marking Boundary with Human Generic Nouns `[CONFIRMED & CLARIFIED]`
- **Linguistic Grounding (Thompson 2012, Section 4.3; BA-GRAM-2011 Vol. 2, p. 415)**:
  While animate direct objects canonically require `-ke`, non-specific generic human profession nouns in non-referential or predicate contexts take zero marking (e.g. *ডাক্তার ডাকো* 'Call a doctor', *চাকর রাখো* 'Hire a servant').
- **Action Taken**:
  - Verified that rule `RUL-MSYN-DOM-ACCUSATIVE` explicitly documents this exception (`NON_SPECIFIC_GENERIC_HUMAN`).
  - Added regression test `EX-MSYN-DOM-GENERIC-HUMAN`.

---

## 3. Audit Action Ledger

| Ledger ID | Component | Status | Action Description |
|---|---|---|---|
| `AUD-ACT-01` | `src/blf/linguistics/morphology/nominal_declension.py` | `COMPLETED` | Enforce mutually exclusive classifier vs plural branches. |
| `AUD-ACT-02` | `research/linguistic-knowledge/morphological-paradigms.md` | `COMPLETED` | Update morphotactic template and pronominal locative register notes. |
| `AUD-ACT-03` | `tests/test_morphology.py` | `COMPLETED` | Add tests rejecting classifier+plural co-affixation and validating demonstrative vs personal locatives. |
| `AUD-ACT-04` | `ontology/paradigms/pronominal_paradigms.json` | `COMPLETED` | Add register notes on synthetic personal locatives. |
