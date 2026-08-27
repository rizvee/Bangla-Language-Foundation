# Research Writing Policy & Anti-AI-Slop Standard — BLF

## 1. Objective & Philosophy
BLF documents must uphold the highest standards of scientific rigor, clarity, and precision. We strictly ban generic AI-generated filler, empty rhetorical framing, inflated claims, and pseudo-academic fluff.

Every sentence in a BLF document or dataset note must earn its place through concrete evidence, precise definitions, or falsifiable claims.

---

## 2. Stylistic Standards
1. **Evidence-Led**: Ground assertions in documented data, primary source citations, or direct experimental measurements.
2. **Restrained & Precise**: Avoid hyperbole ("revolutionary", "groundbreaking", "unprecedented", "game-changing"). State findings with measured calibration.
3. **Specific & Concrete**: Use domain-accurate linguistic and computational terminology without conversational filler.
4. **Natural Cadence**: Avoid mechanical formulaic transitions ("not only X but also Y", "furthermore it is crucial to consider", "in summary").

---

## 3. Flagged & Prohibited Vocabulary
The following phrases and terms are flagged by automated linters when used as rhetorical filler:
- `delve into`, `delving`
- `comprehensive` (unless strictly referring to an exhaustive dataset audit)
- `robust` (unless backed by quantifiable stress-testing metrics)
- `leveraging`, `unlock`, `revolutionize`
- `groundbreaking`, `pivotal`, `testament to`
- `in today's rapidly evolving`, `plays a crucial role`
- `it is important to note`, `intricate`, `multifaceted`

---

## 4. Citation Authenticity Discipline
- **Zero Hallucination Tolerance**: Never invent paper titles, authors, DOIs, ISBNs, arXiv IDs, or page numbers.
- **Verification Marking**: Field-level verification (`VERIFIED`, `PARTIALLY_VERIFIED`, `PROVISIONAL`, `QUARANTINED`, `REJECTED`) is mandatory. A source cannot be marked VERIFIED without traceable primary evidence.
- **Separation of Source Claim from Interpretation**: Always separate what the original source asserted from what the BLF team is inferring or extending.

---

## 5. Epistemic AI Slop: Definition & Guardrails
Beyond surface rhetorical filler, BLF strictly prohibits **Epistemic AI Slop**, defined as:
1. **Fabricated or Misattributed Identifiers**: Citing an actual paper's identifier (e.g. arXiv ID, ACL Anthology ID, DOI) for a completely different paper or dataset.
2. **Blended Metadata**: Conflating authors, datasets, and release years across unrelated publications into a single synthetic citation.
3. **Invented Dataset Statistics**: Guessing or assuming token counts, sentence counts, speaker counts, or license terms without primary evidence.
4. **Decorative Precision**: Providing plausible-sounding numbers or dates without a measured or cited source.
5. **Unsupported Novelty**: Making universal absence claims ("no dataset exists") without an exhaustive, documented search boundary.
6. **Circular LLM Verification**: Accepting a citation as verified merely because an LLM or subagent claimed it was verified without terminating at external evidence. Verification must always terminate at primary catalog, repository, or DOI evidence.

---

## 6. Permanent Research & Evidence Invariants
The following core axioms govern all research and data operations:

```
SCHEMA VALID            != SOURCE VERIFIED
SOURCE URL EXISTS       != CLAIM VERIFIED
AUTHORITY DOMAIN        != FIELD EVIDENCE
IDENTIFIER EXISTS       != IDENTIFIER MATCHES RECORD
MODEL REVIEW            != EXTERNAL VERIFICATION
```

Verification terminates only when the claimed value is matched against external evidence that actually contains and supports that exact value.
