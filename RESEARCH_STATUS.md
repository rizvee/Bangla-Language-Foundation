# Research & Dataset Status — BLF

Last Updated: 2026-08-28

---

## 1. Project Phase
- **Current Phase**: Phase 2A.2c — Private Blind Sessions, Candidate-Level Judgments & Human Pilot Freeze (Complete)
- **Milestone State**: Phase 1A-1D, 2A, 2A.1, 2A.2, 2A.2b, and 2A.2c Operational
- **Primary Branch**: `main`
- **Gold-Readiness Verdict**: `READY_FOR_CONTROLLED_HUMAN_REVIEW_PILOT`

---

## 2. Quantitative Metrics (Verifiable State)

| Metric | Current Value | Notes |
|---|---|---|
| **Schemas Authoring** | 17 schemas (`v0.1-draft-2.0`) | Utterance, Sentence Family, Source, Synthetic Provenance, Linguistic Evidence, Linguistic Claim, Linguistic Rule, Linguistic Example, Inflectional Paradigm, Linguistic Construction, Complex Predicate, Dialogue Act, Semantic Frame, Corpus Attestation, Human Review Submission, Decoded Review Record, Review Adjudication |
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
| **Corpus Attestations** | 12 attestations | Audited & classified as `PROVISIONAL` with quarantined unindexed splits (`ontology/attestations/`) |
| **Diagnostic Candidate Pack** | 156 items | Epistemically labeled in `data/review_queue/linguistic_review_pack.json` marked `PENDING_HUMAN_REVIEW` |
| **Human Review Pilot** | 40 items | Canonical research pilot in `data/review_queue/human_review_pilot_40.json` |
| **Practice Items** | 3 items | Calibration examples in `data/review_queue/practice_items.json` |
| **Private Session Generator** | Ready | `scripts/create_private_review_session.py` (generates uncompromised packs in `.blf-private/`) |
| **Provenance Graph Integrity** | 100% Traceable | 0 broken links from Utterance to Primary Source (`scripts/validate_provenance_graph.py`) |
| **Automated Tests** | 80 unit tests | 100% passing across 15 test suites |
| **Rule Test Coverage** | 100% (20/20) | Documented in `research/linguistic-knowledge/rule-test-coverage.md` |
| **Dataset Scale** | 0 production records | In research & knowledge modeling (no mass generation) |
| **Dataset License** | Undecided | Pending source-license and redistribution audit |

---

## 3. Active Components & Verification

- **Frozen Evidence Baseline**: Implemented in `research/phase-0-manifest.json` (Phase 0.3) with cryptographic SHA-256 checksums across all core registries and schemas.
- **Claim-Level & Artifact-Specific Source Auditor**: Implemented in `scripts/audit_sources.py` and `sources/registry/source-audit.jsonl` enforcing semantic identifier matching, author list validation, and artifact license precision.
- **Multi-Factor DOM Engine**: Implemented in `src/blf/linguistics/dom.py` with multi-dimensional `ObjectFeatures` and source-conflict awareness for specific inanimates (`এটাকে`, `বইটাকে`).
- **Structured Interrogative Valency Analyzer**: Implemented in `src/blf/linguistics/pragmatics.py` disambiguating *কি* vs *কী* using verb valency and argument structure with explicit `AMBIGUOUS` fallback.
- **Calibrated Verbal Conjugation**: Implemented in `src/blf/linguistics/morphology/verbal_conjugator.py` distinguishing indicative *হন* from imperative *হোন* and calibrating negative morphology (*দিইনি*, *নিইনি*, *শিখিনি*).
- **Corpus Attestation Layer**: Implemented in `schemas/v0_1/corpus_attestation.schema.json`, `src/blf/ontology/attestation.py`, `ontology/attestations/corpus_attestations.json`, and validated by `scripts/validate_attestations.py` and `scripts/audit_attestations.py`.
- **Private Session Architecture & Decoder**: Implemented in `scripts/create_private_review_session.py`, `scripts/decode_review_submissions.py`, with private mappings stored in `.blf-private/` (gitignored).
- **Dual-Target IAA Engine**: Implemented in `schemas/v0_1/human_review_decision.schema.json`, `schemas/v0_1/decoded_review_record.schema.json`, `schemas/v0_1/review_adjudication.schema.json`, `src/blf/quality/iaa.py`, and `scripts/compute_iaa.py`.
- **Gold-Readiness Gate**: Formalized in `research/gold-readiness-report.md` and `.json` with categorical evidence gates (`READY_FOR_CONTROLLED_HUMAN_REVIEW_PILOT`).

---

## 4. Known Limitations & Research Gaps

1. **Stage 1 Real Human Session Execution**: The private session generator (`scripts/create_private_review_session.py`) awaits invocation when actual native raters are selected prior to Phase 3 Gold seed scaling.
2. **Physical Page Audits**: Bibliographic citations for printed grammar books (Azad 1984, Thompson 2012, BA 2011) remain provisional until verified against physical scans.
3. **Dialect Representations**: Dialectal markers for Sylheti and Chittagonian are grounded in scholarly field literature; empirical spoken audio transcriptions will be integrated during Gold corpus expansion.
