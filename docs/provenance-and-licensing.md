# Provenance & Licensing Policy — BLF

## 1. Core Licensing Principles
1. **No Verbatim Ingestion of Copyrighted Works**: BLF extracts linguistic rules, morphological paradigms, grammar constraints, and statistical distributions from reference works, but strictly prohibits bulk verbatim reproduction of copyrighted prose.
2. **Public Domain Verification**: Public domain works are verified based on jurisdiction and year of publication before text ingestion.
3. **Open Dataset Attribution**: Open-access external corpora (CC-BY, MIT, etc.) ingested into the pipeline must preserve full original attribution, license text, and upstream URLs.
4. **Unknown License Policy**: An unspecified or unclear license is treated as proprietary/restricted. Data with unknown licensing terms will not be redistributed.

---

## 2. Source Registry Fields & Standards
Every entry in `sources/registry/sources.json` must provide:
- `source_id`: Unique stable identifier (e.g., `BA-GRAM-2011`).
- `title`: Full official publication title.
- `author` / `organization`: Primary creators.
- `source_tier`: `TIER_A` through `TIER_E`.
- `year`: Publication year.
- `license`: Canonical SPDX license identifier (e.g. `CC-BY-4.0`, `MIT`, `Public-Domain`, `All-Rights-Reserved`).
- `redistribution_status`: `open_redistribution`, `derived_features_only`, or `restricted_internal`.
- `checksum`: SHA-256 hash of the referenced digital artifact where available.
- `verification_status`: `VERIFIED`, `PROVISIONAL`, or `UNVERIFIED`.
- `citation`: Full bibliographic citation.

---

## 3. Data Transformation & Dataset Licensing Status
- **Repository Code & Tooling**: Software tools and pipeline scripts in this repository are provided under the MIT License.
- **Dataset Artifacts**: Dataset licensing is currently **UNDECIDED / PENDING SOURCE-LICENSE AND REDISTRIBUTION AUDIT**. No public dataset license (e.g., CC-BY-4.0) has been finalized, and no dataset release has yet been published.
- **Third-Party Data**: Any ingested third-party reference data strictly retains its original upstream license and redistribution restrictions. Feature extraction (such as extracting abstract grammar rules, phonological patterns, or POS paradigms) is conducted in compliance with applicable fair-use and copyright laws without bulk reproduction of copyrighted prose.
