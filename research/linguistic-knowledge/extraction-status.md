# Linguistic Knowledge Extraction Status — Phase 1A Pilot

## 1. Summary Metrics

| Entity Category | Count | Status | Schema Conformance |
|---|---|---|---|
| **Linguistic Evidence Items** | 20 items | 100% Verified against primary sources | `linguistic_evidence.schema.json` |
| **Atomic Linguistic Claims** | 36 claims | 100% Evidence-grounded | `linguistic_claim.schema.json` |
| **Declarative Linguistic Rules** | 20 rules | 100% Claim-supported | `linguistic_rule.schema.json` |
| **Provenance-Backed Examples** | 22 examples | Source-cited and verified | `linguistic_example.schema.json` |
| **Terminology Crosswalk Items** | 14 mappings | Aligned across 5 frameworks | `terminology-crosswalk.json` |
| **Documented Framework Conflicts** | 3 relations | Resolved with canonical BLF modeling | `conflicts.json` |

---

## 2. Claims Breakdown by Linguistic Level

| Linguistic Level | Number of Claims | Key Focus Areas |
|---|---|---|
| `SYNTAX` | 10 claims | Constituent Order (SOV), Scrambling, Pro-Drop, Dative Subjects, Wh-in-situ, Polar Questions, Conditionals, Correlatives |
| `MORPHOSYNTAX` | 13 claims | Differential Object Marking (-ke), Honorificity agreement, Classifier selection, Postpositions, Plurality animacy, Case allomorphy |
| `MORPHOLOGY` | 4 claims | Present, Present Continuous, Past Continuous, Past Habitual, Future verbal paradigms |
| `SEMANTICS` | 7 claims | Aspectual Vector Verbs (phela, neoa, dewa, utha, bosha), Copular Negation (nei vs noy) |
| `PRAGMATICS` | 2 claims | Focus clitic -i, Additive clitic -o, Information structure |

---

## 3. Sources Accessed in Phase 1A Pilot
1. `BA-GRAM-2011`: *Pramita Bangla Bhashar Byakaran* (2 Vols., Bangla Academy, Dhaka, 2011, LCCN 2012323386).
2. `THOMPSON-GRAM-2012`: *Bengali: A Comprehensive Grammar* (Routledge, 2012, ISBN 978-0-415-41139-4).
3. `AZAD-SYNTAX-1984`: *Bakkototto* (Bangla Academy, Dhaka, 1984, LCCN 85901372).

---

## 4. Review Queue & Verification State
- `SOURCE_VERIFIED`: 36 claims (100% of pilot claims).
- `HUMAN_APPROVED`: 0 claims (Reserved exclusively for authenticated human linguist sign-off).
- `AUTO_EXTRACTED`: 0 claims in active registry (All validated and elevated to SOURCE_VERIFIED).
