# Bangla Language Foundation (BLF)

**Bangla Language Foundation** is an open research, linguistics, natural language processing, and dataset-engineering initiative to build a Bangladesh-first structured foundation dataset for the Bangla language.

Rather than storing sentences as flat text strings with classification tags, BLF models language as a multi-layer realization of meaning, semantic frames, grammatical constructions, lexical choices, morphological inflections, pragmatic registers, and script variants.

---

## Key Highlights

- **Bangladesh-First Linguistic Scope**: Canonical baseline is Bangladesh Standard Bangla (BDSB), with explicit multidimensional support for colloquial varieties, regional dialects (Sylheti, Chatgaya, Noakhailla, Rangpuri, etc.), code-mixing, and Romanized Banglish.
- **Deep Linguistic Realization**:
  $$\text{Meaning} \longrightarrow \text{Semantic Frame} \longrightarrow \text{Grammatical Construction} \longrightarrow \text{Lexical Selection} \longrightarrow \text{Morphology} \longrightarrow \text{Canonical Sentence} \longrightarrow \text{Variant Realizations}$$
- **Tri-Tier Quality Architecture**: Strict physical and metadata separation across `GOLD` (authoritative human-verified), `SILVER` (cleaned and rule-validated), and `SYNTHETIC` (constrained model/rule generation with full provenance).
- **Anti-AI-Slop & Citation Discipline**: Automated linter and guardrails preventing synthetic translationese, repetitive syntax, pronoun overloading, and unverified citations.
- **Reproducibility & Verification**: Self-contained Python validation suite with zero external dependencies required for core testing.

---

## Project Structure

```
├── data/                  # Partitioned data directories (gold, silver, synthetic, raw)
├── ontology/              # Conceptual layers (frames, constructions, morphology, dialects)
├── schemas/               # Versioned JSON schemas (v0.1 draft)
├── sources/               # Machine-readable source registry and licensing metadata
├── research/              # Literature reviews, gap analyses, and methodology findings
├── annotations/           # Annotation guidelines and manifests
├── benchmarks/            # Evaluation splits and diagnostic task suites
├── configs/               # Validation and pipeline configurations
├── scripts/               # Validation, normalizer, and anti-slop check scripts
├── src/blf/               # Core Python library (models, normalizers, validators)
├── tests/                 # Automated unit test suite
├── docs/                  # Architectural documentation and research guides
├── CHANGELOG.md           # Project version history
├── CONTRIBUTING.md        # Contribution guidelines
├── CONTRIBUTORS.md        # Project contributors
├── CITATION.cff           # Citation metadata
├── ROADMAP.md             # Development roadmap across Phases 0–9
└── RESEARCH_STATUS.md     # Current research and dataset metrics
```

---

## Quick Start & Validation

### Prerequisites
- Python 3.10 or higher
- Git 2.40 or higher

### Installation
Clone the repository and install development dependencies:

```bash
git clone https://github.com/rizvee/Bangla-Language-Foundation.git
cd Bangla-Language-Foundation
pip install -r requirements.txt
```

### Running Verification Checks
Execute the test and validation suite locally:

```bash
# 1. Run unit test suite
python -m unittest discover tests -v

# 2. Validate JSON schemas and sample fixtures
python scripts/validate_schemas.py

# 3. Validate source registry integrity
python scripts/validate_sources.py

# 4. Run documentation consistency checks
python scripts/check_docs_consistency.py

# 5. Run anti-slop linter across documentation
python scripts/check_anti_slop.py --path docs/
```

---

## Documentation Navigation

| Document | Description |
|---|---|
| [Documentation Map](docs/index.md) | Complete directory and navigation index for all public project docs |
| [Architecture](docs/architecture.md) | Entity models, semantic layers, and annotation schema design |
| [Research Methodology](docs/research-methodology.md) | 5-stage research lifecycle from discovery to quality promotion |
| [Data Quality Model](docs/data-quality-model.md) | Tri-tier quality definitions, scoring, and promotion audits |
| [Provenance & Licensing](docs/provenance-and-licensing.md) | Source hierarchy (Tier A–E), copyright safeguards, and registry rules |
| [Reproducibility Guide](docs/reproducibility.md) | Deterministic environment setup, test runs, and build manifests |
| [Research Writing Policy](docs/research-writing-policy.md) | Scientific rigor standards and anti-AI-slop rules |
| [Roadmap](ROADMAP.md) | Long-term phase plan and milestone tracking |
| [Research Status](RESEARCH_STATUS.md) | Current phase status, verified sources, and schema metrics |

---

## Current Status

- **Phase**: Phase 0 — Research Source Landscape & Gap Analysis
- **Schema Version**: `v0.1-draft`
- **Source Registry**: Seeded with verified Tier A (Bangla Academy), Tier B (Descriptive Linguistics), and Tier D (Universal Dependencies) sources.
- **Active Focus**: Cataloging authoritative grammar references and compiling linguistic knowledge maps before dataset assembly.

---

## Contributing

Contributions from linguists, NLP researchers, native speakers, and engineers are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution workflows, annotation standards, and code quality expectations.

---

## License & Citation

- **Repository Code & Tooling**: Software tools and pipeline scripts are provided under the MIT License. See [LICENSE](LICENSE).
- **Dataset Artifacts**: Dataset licensing is currently **undecided and pending source-license and redistribution audits**. No public dataset release has been made yet.
- **Citation**: For citing this research software and repository scaffolding, refer to [CITATION.cff](CITATION.cff).
