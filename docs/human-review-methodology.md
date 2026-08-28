# Human Review & Adjudication Protocol — BLF

## 1. Overview & Core Principles

The **Bangla Language Foundation (BLF)** enforces a strict two-stage human evaluation protocol to ensure that gold-standard linguistic data is grounded in authentic native-speaker judgments without confirmation bias or automated contamination.

```
+-------------------------------------------------------------+
| STAGE 1: BLINDED NATIVE JUDGMENT                           |
| (Independent native review with randomized candidate order) |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| INTER-ANNOTATOR AGREEMENT (IAA)                             |
| (Pairwise Cohen's Kappa, Confusion Matrices, Category QA)   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| DISAGREEMENT QUEUE EXTRACTION                               |
| (Items with rater divergence flagged for adjudication)      |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| STAGE 2: EVIDENCE-AWARE ADJUDICATION                        |
| (Linguist reconciles items with access to grammar sources)  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| GOLD SEED PROMOTION                                         |
| (Adjudicated items eligible for Gold corpus baseline)       |
+-------------------------------------------------------------+
```

---

## 2. Reviewer Eligibility & Qualifications

For Bangladesh Standard Bangla (BDSB) evaluations:
- **Primary Acceptability Evaluators**: Must be native Bangladeshi Bangla speakers who grew up in Bangladesh and regularly use standard/colloquial BDSB.
- **Linguistic Expertise**: At least one evaluator per review session should possess formal training in linguistics, Bangla grammar, language teaching, or NLP annotation.
- **Independence**: Evaluators must complete Stage 1 reviews independently without access to other reviewers' answers.
- **Constraint on Non-Native Researchers**: Computational linguists or researchers who are non-native speakers may participate in pipeline design or schema development, but may **never** independently establish native Gold acceptability judgments.

---

## 3. Stage 1: Blinded Review & Candidate Randomization

To eliminate confirmation bias:
1. **Withholding Hypotheses**: Evaluator packages withhold `system_hypothesis`, expected answers, internal rule confidence scores, and source citations.
2. **Deterministic Candidate Permutation**: Candidate options (**A**, **B**, **C**) are shuffled per item using seeded pseudo-random permutations (e.g. `seed=101` for `REV-LINGUIST-01`, `seed=202` for `REV-NATIVE-02`).
3. **Secret Mapping**: The mapping between displayed candidate labels and canonical candidate IDs is stored in `data/review_queue/pilot_40_randomization_mapping.json` for post-review decoding.

### Allowed Categorical Judgments
- `NATURAL_STANDARD`: Fully natural, idiomatic Bangladesh Standard Bangla.
- `NATURAL_COLLOQUIAL`: Natural and standard in colloquial Cholit speech.
- `MARKED_BUT_VALID`: Grammatical and attested, but carries special pragmatic or stylistic marking.
- `UNNATURAL`: Grammatically decipherable but awkward or unidiomatic in BDSB.
- `UNGRAMMATICAL`: Violates morphosyntactic rules of Bangla grammar.
- `MEANING_DIFFERS`: The sentence is valid but conveys a different meaning than intended.
- `NEEDS_CONTEXT`: Acceptability depends heavily on surrounding discourse context.
- `UNSURE`: Evaluator is uncertain.

---

## 4. Inter-Annotator Agreement (IAA) Methodology

Pairwise evaluation is executed via [`scripts/compute_iaa.py`](../scripts/compute_iaa.py):
- **Intersection Matching**: Agreement is computed strictly over items evaluated by both specific raters.
- **Metrics Computed**:
  - **Raw Percent Agreement**: $P_o = \frac{\sum \text{agreed}}{\text{total common items}}$
  - **Cohen's Kappa ($\kappa$)**: $\kappa = \frac{P_o - P_e}{1 - P_e}$, accounting for chance agreement.
  - **Confusion Matrices**: Tracking systematic rater differences (e.g., standard vs colloquial thresholds).
  - **Category Breakdown**: Agreement broken down across linguistic phenomena (morphology, DOM, complex predicates, questions).
- **Interpretation Caution**: In a 40-item multi-category pilot, raw Kappa values must be analyzed alongside category prevalence and marginal category distributions.

---

## 5. Stage 2: Evidence-Aware Adjudication

Items with conflicting judgments or preferred candidates are extracted into the disagreement queue:
1. **Unblinding Sources**: During adjudication, the expert linguist accesses full bibliographic evidence, grammar citations (Bangla Academy, Azad 1984, Thompson 2012), and corpus attestations.
2. **Reconciliation**: The adjudicator establishes the authoritative Gold standard form and records the detailed linguistic rationale.
3. **Rule Feedback**: If an adjudication reveals a flaw in an automated rule (e.g. DOM on inanimate demonstratives), the underlying declarative rule is updated and re-verified.
4. **Adjudication Schema**: Authoritative decisions are recorded under [`schemas/v0_1/review_adjudication.schema.json`](../schemas/v0_1/review_adjudication.schema.json) with status `ADJUDICATED_GOLD`.
