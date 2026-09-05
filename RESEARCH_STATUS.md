# Research & Dataset Status — BLF

Last Updated: 2026-09-05

---

## 1. Project Phase
- **Current Phase**: Phase 2A.2e — Forensic Linguistic Calibration Patch (Complete)
- **Milestone State**: CALIBRATED_FOR_HUMAN_REVIEW
- **Primary Branch**: `main`
- **Gold-Readiness Verdict**: `READY_FOR_CONTROLLED_HUMAN_REVIEW_PILOT` (Gold gate remains strictly closed pending real human reviewer evaluations)

---

## 2. Quantitative Metrics (Verifiable State)

| Metric | Current Value | Notes |
|---|---|---|
| **Schemas Authoring** | 19 schemas (`v0.1-draft-2.0`) | Utterance, Sentence Family, Source, Synthetic Provenance, Linguistic Evidence, Linguistic Claim, Linguistic Rule, Linguistic Example, Inflectional Paradigm, Linguistic Construction, Complex Predicate, Dialogue Act, Semantic Frame, Corpus Attestation, Human Review Submission, Reviewer Submission Bundle, Reviewer Consent Record, Decoded Review Record, Review Adjudication |
| **Verified Sources in Registry** | 16 references | Tier A (4), Tier B (4), Tier D (8) with artifact breakdowns |
| **Partially Verified Sources** | 1 reference | BPCC Bengali Parallel Component |
| **Quarantined Sources** | 4 references | Recorded in `sources/registry/source-audit.jsonl` |
| **Linguistic Evidence Items** | 21 items | 100% verified against primary sources (`ontology/evidence/pilot_evidence.json`) |
| **Atomic Linguistic Claims** | 36 claims | 100% evidence-grounded across 5 levels (`ontology/claims/pilot_claims.json`) |
| **Declarative Linguistic Rules** | 20 rules | 100% claim-supported and unit-tested (`ontology/rules/pilot_rules.json`) |
| **Provenance-Backed Examples** | 22 examples | Source-cited and verified (`ontology/examples/pilot_examples.json`) |
| **Inflectional Paradigms** | 14 paradigms | Nouns (4), Pronouns (5), Verbs (5 including `PARADIGM-VERB-HO`) (`ontology/paradigms/`) |
| **Syntactic Constructions** | 22 constructions | SOV, SV, Ditransitive, Copular, Existential, Polar Ki, Imperatives (`ontology/constructions/`) |
| **Complex Predicates** | 8 predicates | Graded vector compatibility (`ALLOWED`, `CONTEXT_DEPENDENT`, `UNSUPPORTED`) for `phela`, `neoa`, `dewa`, `utha` (`ontology/complex_predicates/`) |
| **Pragmatic Dialogue Acts** | 17 dialogue acts | Speech acts, honorificity constraints, clitics (`ontology/pragmatics/`) |
| **Pragmatic Particles** | 7 particles | Polyfunctional senses for `যে` (complementizer, mirative, clause-final evaluative, emphatic stance), focus clitics (`-i`, `-o`), discourse markers (`to`, `na`, `ba`, `ki`) |
| **Semantic Frames** | 24 core frames | Source-grounded communicative frames across everyday domains (`ontology/frames/`) |
| **Corpus Attestations** | 12 attestations | Audited & classified as `PROVISIONAL` with quarantined unindexed splits (`ontology/attestations/`) |
| **Diagnostic Candidate Pack** | 156 items | Epistemically labeled in `data/review_queue/linguistic_review_pack.json` marked `PENDING_HUMAN_REVIEW` |
| **Human Review Pilot** | 40 items | Canonical research pilot in `data/review_queue/human_review_pilot_40.json` (items 015, 016, 023, 030, 040 calibrated) |
| **Practice Items** | 3 de-primed items | Calibration examples teaching interface mechanics only in `data/review_queue/practice_items.json` |
| **Private Session Generator** | Hardened (v2.0.0) | `scripts/create_private_review_session.py` (enforces consent gate, 128-bit seeds, templates in `.blf-private/`) |
| **Submission Decoder** | Fail-Closed (v2.0.0) | `scripts/decode_review_submissions.py` (bundle schema, candidate key enforcement, SHA-256 raw hashing) |
| **Dual-Target IAA Engine** | Operational | `src/blf/quality/iaa.py` and `scripts/compute_iaa.py` (candidate-level Kappa & preferred set agreement) |
| **Provenance Graph Integrity** | 100% Traceable | 0 broken links from Utterance to Primary Source (`scripts/validate_provenance_graph.py`) |
| **Automated Tests** | 95 unit tests | 100% passing across 16 test suites |
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
- **Review Capture Integrity & Gating (Phase 2A.2d)**: Formalized in `schemas/v0_1/reviewer_submission_bundle.schema.json` and `schemas/v0_1/reviewer_consent.schema.json`. Private sessions enforce consent gates, 128-bit private seeds, dynamic UTC timestamps, and leak-free submission templates.
- **Fail-Closed Review Decoder & Immutability**: Implemented in `scripts/decode_review_submissions.py` computing cryptographic SHA-256 hashes of raw submissions and validating decoded records against `decoded_review_record.schema.json`.
- **Dual-Target IAA Engine & Decision Protocol**: Implemented in `src/blf/quality/iaa.py` and `scripts/compute_iaa.py` computing pooled candidate-level Cohen's Kappa, confusion matrices, and preferred set agreements under pre-registered decision rules in `docs/pilot-decision-protocol.md`.
- **Forensic Linguistic Calibration (Phase 2A.2e)**: Calibrated classifier morphotactics (removed global substring blacklist; modeled attested N+টা+গুলো and N+গুলা+CASE without premature standard claims); implemented graded aspectual vector selection (distinguished auto-generation safety from linguistic impossibility); separated Wh-orthography from argument structure construction (Item 030); expanded polyfunctional particle *যে* into 4 evidence-backed senses; calibrated diagnostic items 015, 016, 023, 030, and 040.
- **Gold-Readiness Gate**: Formalized in `research/gold-readiness-report.md` and `.json` with categorical evidence gates (`READY_FOR_CONTROLLED_HUMAN_REVIEW_PILOT`).

---

## 4. Known Limitations & Research Gaps

1. **Reviewer Selection & Consent**: Reviewer status is currently UNKNOWN / NOT YET PROVIDED. Running `create_private_review_session.py` in `REAL` mode strictly fails closed until authenticated native raters provide explicit consent.
2. **Physical Page Audits**: Bibliographic citations for printed grammar books (Azad 1984, Thompson 2012, BA 2011) remain provisional until verified against physical scans.
3. **Dialect Representations**: Dialectal markers for Sylheti and Chittagonian are grounded in scholarly field literature; empirical spoken audio transcriptions will be integrated during Gold corpus expansion.

