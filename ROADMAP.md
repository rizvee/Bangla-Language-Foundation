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
[Phase 2: Formal Semantic Frames & Constrained Realization] [ACTIVE / PHASE 2A COMPLETE]
  ├─ Phase 2A: Semantic Frame Core & Realization Prototype (Completed)
  └─ Phase 2B: Full Ontology Graph & Cross-Framework Mapping (In Progress)
       │
       ▼
[Phase 3: Gold Seed Dataset (Linguistic Primitives)] [PLANNED]
       │
       ▼
[Phase 4: Collection & Normalization Pipelines]
       │
       ▼
[Phase 5: Multi-Layer Annotation & Quality Assurance]
       │
       ▼
[Phase 6: Constrained Synthetic Expansion]
       │
       ▼
[Phase 7: Pilot Foundation Dataset (25k–50k Utterances)]
       │
       ▼
[Phase 8: Benchmarking & Diagnostic Probes]
       │
       ▼
[Phase 9: V1 Open Release (250k–500k Utterances) & Research Publication]
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

### Phase 2: Formal Ontology & Constrained Realization `[Phase 2A Completed]`
- [x] **Phase 2A**: Author 24 core semantic frames (`ontology/frames/core_frames.json`) and prototype constrained realizer (`src/blf/generation/realizer.py`).
- [x] Generate diagnostic minimal-pair sentence families (`data/validation/sentence_families_diagnostic.json`).
- [x] Establish 100% complete end-to-end derivation provenance backward tracing.
- [ ] **Phase 2B**: Expand ontology graph and external UD/WordNet alignments.

### Phase 3: Gold Seed Dataset `[Planned]`
- [ ] Construct initial seed set of 1,000+ hand-curated canonical utterances across core everyday semantic frames.
- [ ] Perform double-blind expert linguist annotation and validation.
- [ ] Produce baseline validation fixtures for downstream automated QA.

### Phase 4: Ingestion & Normalization Pipelines `[Planned]`
- [ ] Implement production-grade Unicode NFC and Bengali orthographic normalization pipelines.
- [ ] Build deterministic deduplication and text cleaning modules.
- [ ] Establish automated provenance tracking and checksum verification for all pipeline artifacts.

### Phase 5: Multi-Layer Annotation & Quality Assurance `[Planned]`
- [ ] Author comprehensive annotation manuals for POS, dependency syntax, semantic frames, and pragmatics.
- [ ] Establish inter-annotator agreement metrics and ambiguity resolution workflows.
- [ ] Implement Gold/Silver promotion review queues.

### Phase 6: Constrained Synthetic Expansion `[Planned]`
- [ ] Design grammar-conditioned synthetic realization pipelines.
- [ ] Enforce strict anti-slop filters, pronoun distribution checks, and generation provenance attachment.
- [ ] Validate synthetic outputs against authentic spoken/written evidence.

### Phase 7: Pilot Foundation Dataset `[Planned]`
- [ ] Assemble pilot foundation dataset of 25,000–50,000 canonical utterances with realization variants.
- [ ] Conduct full distribution audit across registers, domains, and dialects.
- [ ] Publish pilot dataset card and internal validation report.

### Phase 8: Benchmarking & Diagnostic Probes `[Planned]`
- [ ] Design evaluation splits across syntactic parsing, semantic role labeling, translation, and code-mixing.
- [ ] Verify zero test-set contamination across public and internal benchmarks.
- [ ] Benchmark existing baseline NLP models on the BLF evaluation suite.

### Phase 9: V1 Open Release & Research Publication `[Planned]`
- [ ] Release V1 Foundation Dataset (250,000–500,000 structured utterances).
- [ ] Publish open dataset cards, documentation, and reproducibility artifacts.
- [ ] Submit peer-reviewed research paper detailing dataset methodology and findings.
