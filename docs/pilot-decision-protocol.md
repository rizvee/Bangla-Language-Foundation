# Pre-Registered Human Review Pilot Decision Protocol — BLF

## 1. Protocol Objective
To ensure objective, unbiased evaluation of the Phase 2A.2 40-item pilot, this protocol freezes all decision rules **prior** to the collection and observation of human evaluator responses.

---

## 2. Agreement & Adjudication Decision Rules

For every canonical item $I$ and candidate $C$:

| Evaluator A Judgment | Evaluator B Judgment | Preliminary Outcome | Required Pipeline Action |
|---|---|---|---|
| `NATURAL_STANDARD` | `NATURAL_STANDARD` | `STANDARD_CANDIDATE_PENDING_ADJUDICATION` | Promoted to Gold candidate pool upon formal adjudication review. |
| `NATURAL_STANDARD` | `NATURAL_COLLOQUIAL` | `REGISTER_DIFFERENCE_FLAG` | Investigate register calibration. Do not collapse automatically; tag appropriate style register. |
| `NATURAL_*` | `UNGRAMMATICAL` | `HIGH_PRIORITY_CONFLICT` | **Mandatory Adjudication**: Expert linguist reviews primary grammar evidence and corpus attestations. |
| `NATURAL_*` | `UNNATURAL` | `IDIOMATICITY_CONFLICT` | Adjudication review to determine whether phrasing is dialectal, archaic, or awkward. |
| Any | `NEEDS_CONTEXT` | `CONTEXT_INSPECTION_FLAG` | Inspect pilot context prompt wording for ambiguity before modifying linguistic rules. |
| Any | `MEANING_DIFFERS` | `SEMANTIC_DRIFT_FLAG` | Inspect translation/gloss and semantic frame constraints. |
| `UNSURE` | `UNSURE` | `INSUFFICIENT_EVIDENCE` | Excluded from Gold baseline. Flagged for future empirical field collection. |
| `UNGRAMMATICAL` | `UNGRAMMATICAL` | `REJECTED_UNGRAMMATICAL` | Candidate confirmed ungrammatical; rule invariant reinforced. |

---

## 3. Preference & Acceptability Separation
- **Acceptability**: Evaluated independently per candidate sentence ($C_A, C_B, C_C$). Multiple candidates in the same item may be judged `NATURAL_STANDARD`.
- **Preference**: Evaluates whether one candidate is the unmarked canonical standard ($[\text{A}]$), multiple are equivalent ($[\text{A}, \text{B}]$), or none are acceptable ($[\text{NONE}]$).
- **Rule**: A candidate cannot be marked as preferred unless it is also judged acceptable (`NATURAL_STANDARD`, `NATURAL_COLLOQUIAL`, or `MARKED_BUT_VALID`).

---

## 4. Rule Modification & Re-Verification Invariant
If Stage 2 Adjudication identifies a defect in an underlying declarative linguistic rule (e.g. DOM or interrogative valency):
1. The declarative rule in `ontology/rules/pilot_rules.json` is modified.
2. A targeted regression test is added to `tests/`.
3. The affected construction is re-verified across all 10 master validation suites.
4. A targeted second human review is scheduled before Gold promotion.
