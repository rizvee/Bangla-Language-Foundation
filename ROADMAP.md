# Development Roadmap — BLF

This roadmap outlines the planned research and engineering phases for the **Bangla Language Foundation (BLF)** project.

---

## Phase Overview & Current Status

```
[Phase 0: Source Landscape & Gap Analysis]  <-- CURRENT ACTIVE PHASE
       │
       ▼
[Phase 1: Source Registry & Linguistic Knowledge Map]
       │
       ▼
[Phase 2: Formal Ontology & Schemas v0.1]
       │
       ▼
[Phase 3: Gold Seed Dataset (Linguistic Primitives)]
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

### Phase 0: Research Source Landscape & Gap Analysis `[In Progress]`
- [x] Establish research operating system, schemas, and validation suite.
- [ ] Conduct comprehensive literature survey of Tier A (Bangla Academy) and Tier B (Academic Grammars) references.
- [ ] Catalog existing open Bangla NLP corpora and identify domain/syntactic representation gaps.

### Phase 1: Source Registry & Linguistic Knowledge Map `[Planned]`
- [ ] Expand `sources/registry/sources.json` to 25+ verified linguistic references.
- [ ] Compile systematic rules for constituent ordering, pro-drop, compound verbs, and postpositional clitics.
- [ ] Define cross-dialectal phonetic and morphosyntactic mapping rules for major regional varieties (Sylheti, Chatgaya, Noakhailla, Rangpuri).

### Phase 2: Formal Ontology & Schemas v0.1 `[Planned]`
- [ ] Author formal FrameNet-style semantic frame catalog in `ontology/semantic-frames/`.
- [ ] Finalize production-ready JSON schemas for lexical, morphological, constructional, and dialogue entities.
- [ ] Implement automated schema migration and validation tooling.

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
