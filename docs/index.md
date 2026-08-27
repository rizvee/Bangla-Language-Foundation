# Bangla Language Foundation (BLF) — Documentation Index

Welcome to the documentation map for the **Bangla Language Foundation (BLF)** research and dataset engineering project.

---

## 1. Project Overview & Governance
- [Project Readme](../README.md): High-level overview, mission, quick start, and installation.
- [Changelog](../CHANGELOG.md): Version history and release notes.
- [Contributing Guidelines](../CONTRIBUTING.md): Scientific integrity standards, contribution areas, and PR checklist.
- [Contributors](../CONTRIBUTORS.md): Project authors and maintainers.
- [Citation Metadata](../CITATION.cff): Academic and dataset citation format.
- [Development Roadmap](../ROADMAP.md): Phases 0 through 9 milestone tracker.
- [Research Status](../RESEARCH_STATUS.md): Current verifiable research and repository metrics.

---

## 2. Architecture & Linguistic Design
- [Data Architecture](architecture.md): Conceptual layers, entity relationships (Lexeme, Construction, Frame, Utterance, Sentence Family), and annotation specifications.
- [Data Quality Model](data-quality-model.md): Specifications for `GOLD`, `SILVER`, and `SYNTHETIC` quality tiers, scoring criteria, and auditable promotion workflows.

---

## 3. Methodology & Scientific Standards
- [Research Methodology](research-methodology.md): The 5-stage research lifecycle from source discovery to quality promotion.
- [Provenance & Licensing Policy](provenance-and-licensing.md): Source hierarchy (Tier A–E), copyright safeguards, and registry metadata invariants.
- [Research Writing Policy](research-writing-policy.md): Standards for scientific clarity, citation authenticity, and anti-AI-slop rules.
- [Reproducibility Guide](reproducibility.md): Deterministic environment setup, test suite execution, and manifest traceability.

---

## 4. Documentation & Research Templates
- [Dataset Card Template](templates/DATASET_CARD_TEMPLATE.md): Standard template for published dataset releases.
- [Source Review Template](templates/SOURCE_REVIEW_TEMPLATE.md): Template for bibliographic evaluation and source ingestion.
- [Research Note Template](templates/RESEARCH_NOTE_TEMPLATE.md): Structured format for recording linguistic findings and experimental notes.
- [Decision Template](templates/DECISION_TEMPLATE.md): Architectural and research decision record (ADR) template.

---

## 5. Schemas & Data Reference
- [Utterance Schema](../schemas/v0_1/utterance.schema.json): JSON Schema for structured utterance records.
- [Sentence Family Schema](../schemas/v0_1/sentence_family.schema.json): JSON Schema for sentence family groupings.
- [Source Schema](../schemas/v0_1/source.schema.json): JSON Schema for research source registry entries.
- [Synthetic Provenance Schema](../schemas/v0_1/synthetic_provenance.schema.json): JSON Schema for synthetic data generation metadata.
- [Source Registry](../sources/registry/sources.json): Verified research source entries.
