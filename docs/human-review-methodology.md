# Human Review & Adjudication Protocol — BLF

## 1. Overview & Core Principles

The **Bangla Language Foundation (BLF)** enforces a strict two-stage human evaluation protocol to ensure that gold-standard linguistic data is grounded in authentic native-speaker judgments without confirmation bias or automated contamination.

```
+-------------------------------------------------------------------------+
| STAGE 1: BLINDED NATIVE JUDGMENT                                       |
| - Private session generated in .blf-private/ (Gitignored)               |
| - Opaque item IDs (BLIND-R1-A7K4) & randomized item order               |
| - Independent candidate-level acceptability (A, B, C) + Preferred sets  |
| - Practice items for calibration (excluded from analytical scoring)     |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| SECURE DECODING & INTER-ANNOTATOR AGREEMENT (IAA)                       |
| - Raw submissions decoded using private session mapping                 |
| - Target A: Candidate Acceptability Agreement (Cohen's Kappa & Matrix)  |
| - Target B: Preferred-Candidate Set Agreement (Exact & Partial Overlaps)|
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| DISAGREEMENT QUEUE EXTRACTION                                           |
| (Pre-registered criteria flag conflicts for Stage 2 review)             |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| STAGE 2: EVIDENCE-AWARE ADJUDICATION                                    |
| (Linguist reconciles items with access to grammar sources & evidence)   |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| GOLD SEED PROMOTION & RULE HARDENING                                    |
| (Adjudicated items promoted to Gold baseline; rules regression-tested)  |
+-------------------------------------------------------------------------+
```

---

## 2. Reviewer Eligibility & Qualifications

For Bangladesh Standard Bangla (BDSB) evaluations:
- **Primary Acceptability Evaluators**: Must be native Bangladeshi Bangla speakers who grew up in Bangladesh and regularly use standard/colloquial BDSB.
- **Linguistic Expertise**: At least one evaluator per review session should possess formal training in linguistics, Bangla grammar, language teaching, or NLP annotation.
- **Independence**: Evaluators must complete Stage 1 reviews independently without access to other reviewers' answers.
- **Privacy Minimization**: Only essential linguistic eligibility metadata is recorded (pseudonym, native status, variety, qualification category). No personal identifiable information (PII) is collected or stored. See [`docs/reviewer-consent-and-ethics.md`](../docs/reviewer-consent-and-ethics.md).

---

## 3. Stage 1: Private Blind Sessions & Candidate Randomization

To eliminate confirmation bias:
1. **Private Session Architecture**: Active review packs, seeds, item order mappings, and candidate permutations are generated in `.blf-private/review_sessions/<SESSION_ID>/` and are strictly gitignored.
2. **Withholding Research Metadata**: Evaluator packages withhold `system_hypothesis`, expected answers, internal rule confidence scores, research categories, and source citations.
3. **Opaque Item IDs**: Reviewers see opaque identifiers (e.g. `BLIND-R1-A7K4`) rather than internal `PILOT-ITEM-001` IDs.
4. **Independent Item & Candidate Shuffling**: Both the order of items and the order of candidate choices (**A**, **B**, **C**) are shuffled independently per reviewer.
5. **Practice Calibration**: Review sheets start with 3 non-scored practice items ([`data/review_queue/practice_items.json`](../data/review_queue/practice_items.json)) to calibrate candidate-level rating.

### Candidate-Level Judgments
Evaluators rate each presented candidate independently using categorical labels:
- `NATURAL_STANDARD`: Fully natural, idiomatic Bangladesh Standard Bangla.
- `NATURAL_COLLOQUIAL`: Natural and standard in colloquial Cholit speech.
- `MARKED_BUT_VALID`: Grammatical and attested, but carries special pragmatic or stylistic marking.
- `UNNATURAL`: Grammatically decipherable but awkward or unidiomatic in BDSB.
- `UNGRAMMATICAL`: Violates morphosyntactic rules of Bangla grammar.
- `MEANING_DIFFERS`: Conveys a different meaning than intended.
- `NEEDS_CONTEXT`: Acceptability depends heavily on surrounding discourse context.
- `UNSURE`: Evaluator is uncertain.

### Preferred Candidate Selection
Separately from acceptability ratings, evaluators select their preferred candidate(s) (e.g. `['A']`, `['A', 'B']` for equivalents, or `['NONE']` if all candidates are unnatural).

---

## 4. Dual Inter-Annotator Agreement (IAA) Methodology

Pairwise evaluation is executed via [`scripts/compute_iaa.py`](../scripts/compute_iaa.py) after decoding:
- **Target A: Candidate-Level Acceptability Agreement**:
  - Compares categorical ratings across all common `canonical_item_id × canonical_candidate_id` pairs.
  - Computes raw percent agreement ($P_o$), Cohen's Kappa ($\kappa$), and 2D confusion matrices.
  - Generates category-level breakdown reports.
- **Target B: Preferred-Candidate Set Agreement**:
  - Compares canonical preferred candidate sets per item.
  - Reports exact set match rate ($[\text{A}] == [\text{A}]$), partial overlaps ($[\text{A}, \text{B}]$ vs $[\text{A}]$), and disjoint preferences.

See [`docs/pilot-decision-protocol.md`](../docs/pilot-decision-protocol.md) for pre-registered adjudication trigger rules.

---

## 5. Stage 2: Evidence-Aware Adjudication

Items with conflicting candidate ratings or preferred choices are extracted into the disagreement queue:
1. **Unblinding Sources**: The expert adjudicator accesses full bibliographic evidence, grammar citations (Bangla Academy, Azad 1984, Thompson 2012), and corpus attestations.
2. **Reconciliation**: The adjudicator establishes the authoritative Gold standard form and records the linguistic rationale under [`schemas/v0_1/review_adjudication.schema.json`](../schemas/v0_1/review_adjudication.schema.json).
3. **Rule Hardening**: If an adjudication reveals a defect in a declarative rule, the rule is updated, a regression test is added, and the suite is re-verified.
