# Data License Decision Document — Bangla Language Foundation

## 1. Status
- **Current Decision Status**: `DECISION_PENDING`
- **Effective Stage**: Pre-Human Foundation Freeze
- **Authority**: BLF Steering / Rizvee

## 2. Executive Context & Boundary Definition
The Bangla Language Foundation (BLF) repository consists of distinct IP and content layers with distinct legal boundaries:

1. **Software & Infrastructure**: Pipeline parsers, normalizers, deduplication engines, validators, and benchmark probes.
2. **Ontological Structures & Schemas**: Semantic frame definitions, construction templates, inflectional paradigms, and JSON schema specifications created by BLF.
3. **Third-Party Linguistic Attestations**: Citations, brief illustrative sentences, and rule citations from published academic grammars and dictionaries.
4. **Third-Party External Corpora**: Public datasets (Common Voice, IndicCorp, BPCC) referenced in source registries.

## 3. Evaluated License Options for Dataset & Ontology Layer
| License Option | Permissiveness | Copyleft | Commercial Use | Evaluation & Tradeoffs |
|---|---|---|---|---|
| **CC BY 4.0** | High | None | Yes | Maximizes downstream adoption across academic and industrial research. Risk: Downstream modifications not contributed back. |
| **CC BY-SA 4.0** (Recommended) | Moderate | ShareAlike | Yes | Ensures linguistic improvements, extensions, and corrections remain open to the Bangla community. |
| **CC BY-NC-SA 4.0** | Restrictive | ShareAlike | No | Prevents commercial exploitation, but restricts industrial researchers from validating models on the benchmark. |
| **OpenRAIL-M** | Permissive with Behavioral Restrictions | None | Conditional | Restricts malicious or non-consensual deployment while allowing open research. |

## 4. Third-Party Source Handling & Fair-Use Boundaries
- **Reference Grammars & Dictionaries** (`BA-GRAM-2011`, `BA-REGDICT-1965`, `ODBL-SKC-1926`, `AZAD-SYNTAX-1984`, `THOMPSON-GRAM-2012`):
  - Abstracted grammatical rules, phonological constraints, and lexical category tags are non-copyrightable facts under intellectual property law.
  - Short illustrative sentence citations are included strictly under nominative fair use for scientific documentation.
  - No continuous text passages or whole pages are ingested or redistributed.
- **Quarantined Sources**:
  - Datasets with unclear licensing or historical contamination (`SENTIRABANGLA-2022`, `BANGLISH-TRANSLIT-2021`, `UD-BN-BENGAL-2023`, `CHATGAYA-PHONO-2018`) remain quarantined; zero records from these sources enter production or benchmark splits.

## 5. Decision Roadmap & Finalization Criteria
Final selection of the official public dataset license will occur following:
1. Completion of the Phase 2A controlled human review pilot.
2. Formal audit of human reviewer consent forms and release agreements.
3. Final publication approval by the project maintainer.

Until formal sign-off, all linguistic dataset artifacts remain marked as `DECISION_PENDING` and are not distributed publicly.
