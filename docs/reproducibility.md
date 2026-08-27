# Reproducibility & Pipeline Standards — BLF

## 1. Core Principles
1. **Deterministic Execution**: All normalization, tokenization, morphological decomposition, and dataset partitioning scripts must be 100% deterministic given fixed seeds and inputs.
2. **Explicit Dependency Management**: All Python dependencies are pinned in `pyproject.toml` and `requirements.txt`.
3. **Local Hardware Viability**: All baseline pipelines, tests, and validation scripts must run efficiently on standard consumer hardware without requiring multi-GPU clusters.
4. **Manifest-Driven Traceability**: Every dataset release artifact is accompanied by a cryptographically hashed manifest documenting exact source inputs, processing code versions, and generation parameters.

---

## 2. Environment Setup & Execution

### Clean Python Environment Setup
```bash
# Verify Python version (>= 3.10)
python --version

# Optional: create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Reproducible Test Execution
```bash
# Execute unit test suite
python -m unittest discover tests

# Execute linting and schema checks
python scripts/check_anti_slop.py --path docs/
python scripts/validate_schemas.py
python scripts/validate_sources.py
```
