# Research & Dataset Status — BLF

Last Updated: 2026-08-28

---

## 1. Project Phase
- **Current Phase**: Phase 2A.1 — Linguistic Integrity Recovery, Attestation & Gold-Readiness Gate (Complete)
- **Milestone State**: Phase 1A-1D, 2A, and 2A.1 Fully Operational Multi-Layer Linguistic OS
- **Primary Branch**: `main`
- **Gold-Readiness Verdict**: `CONDITIONAL_READY_FOR_HUMAN_CURATION`

---

## 2. Quantitative Metrics (Verifiable State)

| Metric | Current Value | Notes |
|---|---|---|
| **Schemas Authoring** | 14 schemas (`v0.1-draft-2.0`) | Utterance, Sentence Family, Source, Synthetic Provenance, Linguistic Evidence, Linguistic Claim, Linguistic Rule, Linguistic Example, Inflectional Paradigm, Linguistic Construction, Complex Predicate, Dialogue Act, Semantic Frame, Corpus Attestation |
| **Verified Sources in Registry** | 16 references | Tier A (4), Tier B (4), Tier D (8) with artifact breakdowns |
| **Partially Verified Sources** | 1 reference | BPCC Bengali Parallel Component |
| **Quarantined Sources** | 4 references | Recorded in `sources/registry/source-audit.jsonl` |
| **Linguistic Evidence Items** | 21 items | 100% verified against primary sources (`ontology/evidence/pilot_evidence.json`) |
| **Atomic Linguistic Claims** | 36 claims | 100% evidence-grounded across 5 levels (`ontology/claims/pilot_claims.json`) |
| **Declarative Linguistic Rules** | 20 rules | 100% claim-supported and unit-tested (`ontology/rules/pilot_rules.json`) |
| **Provenance-Backed Examples** | 22 examples | Source-cited and verified (`ontology/examples/pilot_examples.json`) |
| **Inflectional Paradigms** | 14 paradigms | Nouns (4), Pronouns (5), Verbs (5 including `PARADIGM-VERB-HO`) (`ontology/paradigms/`) |
| **Syntactic Constructions** | 22 constructions | SOV, SV, Ditransitive, Copular, Existential, Polar Ki, Imperatives (`ontology/constructions/`) |
| **Complex Predicates** | 8 predicates | Telic `phela`, Benefactive `neoa`/`dewa`, Inceptive `utha`, LVC `kora`/`howa` (`ontology/complex_predicates/`) |
| **Pragmatic Dialogue Acts** | 17 dialogue acts | Speech acts, honorificity constraints, clitics (`ontology/pragmatics/`) |
| **Pragmatic Particles** | 7 particles | Multi-sense focus clitics (`-i`, `-o`), discourse markers (`to`, `na`, `je`, `ba`, `ki`) |
| **Semantic Frames** | 24 core frames | Source-grounded communicative frames across everyday domains (`ontology/frames/`) |
| **Corpus Attestations** | 12 attestations | Empirical citations linking grammar literature and corpora under fair use (`ontology/attestations/`) |
| **Diagnostic Review Queue** | 156 items | Curated linguistic phenomena queue in `data/review_queue/` marked `PENDING_HUMAN_REVIEW` |
| **Provenance Graph Integrity** | 100% Traceable | 0 broken links from Utterance to Primary Source (`scripts/validate_provenance_graph.py`) |
| **Automated Tests** | 75 unit tests | 100% passing across 15 test suites |
| **Rule Test Coverage** | 100% (20/20) | Documented in `research/linguistic-knowledge/rule-test-coverage.md` |
| **Dataset Scale** | 0 production records | In research & knowledge modeling (no mass generation) |
| **Dataset License** | Undecided | Pending source-license and redistribution audit |

---

## 3. Active Components & Verification

- **Frozen Evidence Baseline**: Implemented in `research/phase-0-manifest.json` (Phase 0.3) with cryptographic SHA-256 checksums across all core registries and schemas.
- **Claim-Level & Artifact-Specific Source Auditor**: Implemented in `scripts/audit_sources.py` and `sources/registry/source-audit.jsonl` enforcing semantic identifier matching, author list validation, and artifact license precision.
- **Differential Object Marking (DOM) Engine**: Implemented in `src/blf/linguistics/dom.py` with multi-dimensional `ObjectFeatures` (Animacy, Definiteness, Specificity, Referentiality).
- **Polarity-Aware Conjugation**: Implemented in `src/blf/linguistics/morphology/verbal_conjugator.py` enforcing standard perfective negation with `-নি` and general postverbal `না`.
- **Corpus Attestation Layer**: Implemented in `schemas/v0_1/corpus_attestation.schema.json`, `src/blf/ontology/attestation.py`, `ontology/attestations/corpus_attestations.json`, and validated by `scripts/validate_attestations.py`.
- **Diagnostic Human Review Pack**: Implemented in `scripts/generate_review_pack.py` producing `data/review_queue/linguistic_review_pack.json` and `.md`.
- **Gold-Readiness Gate**: Formalized in `research/gold-readiness-report.md` and `.json`.

---

## 4. Known Limitations & Research Gaps

1. **Human Expert Sign-Off**: The 156 diagnostic review items in `data/review_queue/` remain in status `PENDING_HUMAN_REVIEW` pending native linguist validation before Phase 3 Gold seed scaling.
2. **Dialect Representations**: Dialectal markers for Sylheti and Chittagonian are grounded in scholarly field literature; empirical spoken audio transcriptions will be integrated during Gold corpus expansion.
