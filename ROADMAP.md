# Development Roadmap — BLF

This roadmap outlines the planned research and engineering phases for the **Bangla Language Foundation (BLF)** project.

---

## Phase Overview & Current Status

```
[Phase 0: Source Landscape & Evidence Baseline]  [COMPLETED / FROZEN]
       │
       ▼
[Phase 1: Linguistic Knowledge, Paradigms & Constructions] [COMPLETED]
  ├─ Phase 1A: Evidence-to-Knowledge Layer (Completed)
  ├─ Phase 1B: Morphosyntactic Paradigm Engine (Completed)
  ├─ Phase 1C: Construction Grammar & Complex Predicates (Completed)
  └─ Phase 1D: Conversational Register, Deixis & Pragmatics (Completed)
       │
       ▼
[Phase 2: Formal Semantic Frames & Cross-Framework Ontology] [COMPLETED]
  ├─ Phase 2A: Semantic Frame Core & Realization Prototype (Completed)
  └─ Phase 2B: Full Ontology Graph & UD Crosswalk Mapping (Completed)
       │
       ▼
[Phase 3: Gold Seed Dataset & Controlled Human Review] [PLANNED / DEFERRED TO PILOT]
       │
       ▼
[Phase 4: Ingestion, Reversible Normalization & Dedup Engine] [INFRASTRUCTURE COMPLETED]
       │
       ▼
[Phase 5: Multi-Layer Annotation OS & Quality Workflow] [INFRASTRUCTURE COMPLETED]
       │
       ▼
[Phase 6: Constrained Synthetic Generation Pipeline] [INFRASTRUCTURE COMPLETED / TEST ONLY]
       │
       ▼
[Phase 7: Pilot Dataset Assembly & Distribution Audit] [INFRASTRUCTURE COMPLETED]
       │
       ▼
[Phase 8: Benchmarking Probes & Contamination Checker] [INFRASTRUCTURE COMPLETED]
       │
       ▼
[Phase 9: V1 Open Release & Research Publication] [PLANNED]
```

---

## Phase Details

### Phase 0: Research Source Landscape & Gap Analysis `[Completed]`
- [x] Establish research operating system, schemas, and validation suite.
- [x] Conduct comprehensive literature survey of Tier A (Bangla Academy) and Tier B (Academic Grammars) references.
- [x] Catalog existing open Bangla NLP corpora and identify domain/syntactic representation gaps.
- [x] Produce machine-readable evidence matrix (`research/dataset-landscape/evidence-matrix.json`) and 10-dimensional gap analysis.
- [x] Freeze verified evidence baseline with cryptographic SHA-256 manifest (`research/phase-0-manifest.json`).

### Phase 1: Linguistic Knowledge, Paradigms & Constructions `[Completed]`
- [x] **Phase 1A**: Operationalize atomic linguistic claims (36), declarative rules (20), examples (22), and terminology crosswalk.
- [x] **Phase 1B**: Implement deterministic morphosyntactic paradigm engine (nominal allomorphy, pronominal honorific matrices, verbal conjugator).
- [x] **Phase 1C**: Author construction grammar catalog (22 constructions) and complex predicate engine (8 vector verbs & LVCs).
- [x] **Phase 1D**: Formalize 3-tier social deixis (`আপনি`/`তুমি`/`তুই`), 17 dialogue acts, and particle semantics.

### Phase 2: Formal Ontology & Constrained Realization `[Completed]`
- [x] **Phase 2A**: Author 24 core semantic frames (`ontology/frames/core_frames.json`) and prototype constrained realizer (`src/blf/generation/realizer.py`).
- [x] Generate diagnostic minimal-pair sentence families (`data/validation/sentence_families_diagnostic.json`).
- [x] Establish 100% complete end-to-end derivation provenance backward tracing.
- [x] **Phase 2B**: Build typed in-memory directed graph `OntologyGraph` (`src/blf/ontology/graph.py`), Universal Dependencies (UD) crosswalk for BRU and PUD (`src/blf/ontology/ud_crosswalk.py`), and external lexical adapter interfaces (`src/blf/ontology/lexical_crosswalk.py`).

### Phase 3: Gold Seed Dataset & Controlled Human Review `[Planned]`
- [ ] Recruit eligible native-speaker linguistic reviewers and execute informed consent agreements.
- [ ] Execute double-blind, air-gapped evaluation on the canonical 40-item pilot queue (`data/review_queue/human_review_pilot_40.json`).
- [ ] Compute official candidate-level Cohen's Kappa, Fleiss' Kappa, and preferred set agreements.
- [ ] Adjudicate disagreements under pre-registered protocol and promote initial Gold seed records.

### Phase 4: Ingestion, Reversible Normalization & Dedup Engine `[Infrastructure Completed]`
- [x] Implement reversible Unicode NFC and punctuation normalization tracking step-level offsets (`src/blf/pipeline/normalization.py`).
- [x] Enforce ZWJ/ZWNJ ligature preservation policy for legitimate Bengali consonant conjuncts.
- [x] Build conservative text cleaner preserving Bengali diacritics and signs while removing corrupted control codes (`src/blf/pipeline/cleaning.py`).
- [x] Implement 4-tier deduplication engine across exact, normalized, morphosyntactic, and semantic near-duplicates (`src/blf/pipeline/deduplication.py`).
- [x] Author pipeline provenance manifest tracking (`src/blf/pipeline/manifest.py`).

### Phase 5: Multi-Layer Annotation OS & Quality Workflow `[Infrastructure Completed]`
- [x] Define multi-layer annotation bundle models covering tokenization, syntax, frames, pragmatics, and dialects (`src/blf/annotation/layers.py`).
- [x] Implement monotonic lifecycle state machine with strict promotion invariants (`src/blf/annotation/state_machine.py`).
- [x] Build generic conflict queue and arbitrator adjudication resolvers (`src/blf/annotation/adjudication.py`).
- [x] Implement multi-rater agreement metrics for Fleiss' Kappa and Krippendorff's Alpha failing closed on missing data (`src/blf/quality/advanced_iaa.py`).

### Phase 6: Constrained Synthetic Generation Pipeline `[Infrastructure Completed / Test-Only]`
- [x] Construct generation pipeline enforcing frame selectional restrictions (`[+Animate]`, `[+Edible]`, `[+Liquid]`) and anti-Cartesian argument filtering (`src/blf/generation/pipeline.py`).
- [x] Attach mandatory synthetic provenance complying with `synthetic_provenance.schema.json`.
- [x] Enforce execution tag `SYNTHETIC_SOFTWARE_TEST_ONLY` and zero-production-data release invariant.

### Phase 7: Pilot Dataset Assembly & Distribution Audit `[Infrastructure Completed]`
- [x] Build leakage-safe dataset splitter co-locating all sentence family variants in the same partition (`src/blf/dataset/split_policy.py`).
- [x] Implement distribution auditor measuring coverage across registers, dialects, frames, and constructions (`src/blf/dataset/distribution_audit.py`).
- [x] Author standardized dataset card template (`docs/dataset-card-template.md`).

### Phase 8: Benchmarking Probes & Contamination Checker `[Infrastructure Completed]`
- [x] Develop unit-level diagnostic linguistic probes for DOM, complex predicates, negation placement, honorific agreement, and morphotactics (`src/blf/benchmarks/probes.py`).
- [x] Implement train-test contamination auditor detecting exact matches, n-gram overlap, and sentence family leakage (`src/blf/benchmarks/contamination.py`).
- [x] Implement BLF-Bench runner reporting structured evaluation contracts without fabricating empirical model numbers (`src/blf/benchmarks/runner.py`).

### Phase 9: V1 Open Release & Research Publication `[Planned]`
- [x] Formulate data licensing evaluation in `docs/DATA_LICENSE_DECISION.md` (marked `DECISION_PENDING`).
- [x] Author machine-readable source redistribution matrix across all 23 sources (`sources/licensing/redistribution_matrix.json`).
- [x] Produce unreleased build manifest in `release/release_manifest.json` confirming 0 Gold records.
- [x] Author comprehensive methodology paper draft skeleton in `papers/methodology_paper_skeleton.md` with explicit empirical placeholders.
- [ ] Execute formal public dataset and methodology paper publication following completion of human reviewer pilot.
