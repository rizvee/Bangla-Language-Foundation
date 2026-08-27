# Contributing to Bangla Language Foundation (BLF)

Thank you for your interest in contributing to the **Bangla Language Foundation (BLF)** project. We welcome contributions from linguists, NLP engineers, dataset creators, native speakers, and researchers.

---

## 1. Code of Conduct & Research Integrity

All contributors are expected to uphold rigorous scientific standards:
- **No Plagiarism or Verbatim Copyright Ingestion**: Do not submit copyrighted text extracted from books, newspapers, or websites. Extract only abstract grammatical rules, morphological patterns, and proper citations.
- **Evidence-Led Claims**: Any linguistic rule, dialect mapping, or syntactic classification must cite verifiable sources or native speaker linguistic evidence.
- **Anti-AI-Slop Standard**: Documentation and research notes must be concise, factual, and free of generic AI-generated filler. Review [Research Writing Policy](docs/research-writing-policy.md) before writing.
- **No Unlabeled Synthetic Data**: If contributing synthetic or model-assisted examples, complete generation provenance metadata is mandatory. Synthetic data must never masquerade as human-authored Gold data.

---

## 2. Contribution Areas

You can contribute in several key areas:
1. **Linguistic Ontology & Grammar**: Formalizing semantic frames, argument structures, and inflectional paradigms for Bangladesh Standard Bangla and regional varieties.
2. **Source Registry & Literature Review**: Adding verified citations and bibliographic reviews of linguistic grammar manuals, dialect dictionaries, and open treebanks to `sources/registry/sources.json`.
3. **Data Engineering & Pipelines**: Improving Unicode normalization, tokenization, deduplication, and schema validation scripts.
4. **Documentation & Benchmarks**: Writing methodology notes, dataset cards, or diagnostic benchmark probes.

---

## 3. Development & Pull Request Workflow

### Local Development Setup
```bash
# Clone the repository
git clone https://github.com/rizvee/Bangla-Language-Foundation.git
cd Bangla-Language-Foundation

# Install development dependencies
pip install -r requirements.txt
```

### Pre-Submission Verification Checklist
Before submitting a pull request, verify that all local checks pass:

```bash
# 1. Run unit test suite
python -m unittest discover tests -v

# 2. Validate schemas and fixtures
python scripts/validate_schemas.py

# 3. Validate source registry
python scripts/validate_sources.py

# 4. Check documentation consistency
python scripts/check_docs_consistency.py

# 5. Run anti-slop check on documentation
python scripts/check_anti_slop.py --path docs/
```

### Pull Request Guidelines
- Branch naming: `feat/your-feature`, `fix/issue-description`, `research/topic-name`.
- Commit messages: Use clear conventional commits (`feat: ...`, `fix: ...`, `docs: ...`, `test: ...`, `research: ...`).
- PR Description: Clearly describe the motivation, evidence basis, changed files, and validation command outputs.
