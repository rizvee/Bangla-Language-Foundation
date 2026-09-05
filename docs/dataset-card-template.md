# Dataset Card Template — BLF Evaluation Benchmark

## 1. Dataset Summary
- **Dataset Name**: Bangla Language Foundation Benchmark (BLF-Bench)
- **Version**: 0.1.0-draft
- **Language Varieties**: Bangladeshi Standard Bengali (BDSB), Regional Dialects (Dhaka Colloquial, Sylheti, Chittagonian, Rajbanshi, Varendra, Barisal)
- **Primary Domain**: Morphosyntax, Differential Object Marking, Complex Predicates, Discourse Particles, Syntactic Constructions
- **Status**: Research Instrumentation Prototype (0 Production Gold Records Released)

## 2. Dataset Structure
Each record adheres to `schemas/v0_1/utterance.schema.json`.

| Field Name | Type | Description |
|---|---|---|
| `utterance_id` | string | Unique persistent identifier |
| `text` | string | Normalized Bengali text string |
| `raw_text` | string | Exact pre-normalization raw string |
| `language_variety` | string | Variety or dialect enum |
| `register` | string | Register level (formal standard, colloquial, etc.) |
| `grammaticality` | string | Grammatical acceptability status |
| `quality_tier` | string | Quality tier: `GOLD`, `SILVER`, `SYNTHETIC` |
| `sentence_family_id` | string | Identifies sentence family to prevent split contamination |
| `layers` | object | Multi-layer annotations (tokens, syntax, semantics, pragmatics) |
| `provenance` | object | Complete backward derivation metadata |

## 3. Subsets and Split Methodology
- **Grouping Rule**: Zero-contamination grouping by `sentence_family_id`. All structural and stylistic variants derived from the same base proposition are co-located in the same partition.
- **Partitions**:
  - **Train**: 70% of sentence families
  - **Development (Validation)**: 15% of sentence families
  - **Evaluation Test**: 15% of sentence families

## 4. Annotations and Provenance
- **Annotation Method**: Controlled multi-annotator review protocol with explicit double-blind evaluation.
- **IAA Requirements**: Pooled Cohen's Kappa, Fleiss' Kappa, and Krippendorff's Alpha computed across concurrent reviewer assignments.
- **Promotion Gate**: Minimum threshold of agreement required before promotion from `HUMAN_PILOT_VERIFIED` to `GOLD`.

## 5. Sociolinguistic Scope and Dialect Coverage
- Stratified sampling across formal written, informal spoken, colloquial urban, and regional dialect varieties.
- Explicit dialect boundary markers recorded in morphological feature vectors.

## 6. Licensing and Distribution Policy
- **Linguistic Annotations & Ontological Graphs**: CC BY-SA 4.0
- **Software & Validation Infrastructure**: Apache 2.0
- **Third-Party Attestations**: Referenced under nominative fair-use and academic citation standards; raw copyrighted source corpora are not redistributed.
