# Linguistic Terminology Crosswalk — BLF

## 1. Overview & Objectives
This crosswalk maps foundational grammatical terminology across five frameworks:
1. **Traditional Bangla Grammar** (*Sanskrit-derived traditional Byakaran*)
2. **Bangla Academy Standard Terminology** (*Pramita Bangla Bhashar Byakaran*, 2011)
3. **Modern Descriptive Linguistics** (Thompson 2012, Chatterji 1926)
4. **Universal Dependencies (UD)** (CoNLL-U morphosyntactic features and dependency relations)
5. **BLF Canonical Ontology** (Formal computational representations)

---

## 2. Cross-Framework Alignment Table

| Traditional Term | Bangla Academy Term | Descriptive Linguistics Term | UD Equivalent | BLF Canonical Term | Mapping Type |
|---|---|---|---|---|---|
| **কর্তা (Karta)** | উদ্দেশ্য / কর্তা | Subject (Nominative / Ergative agent) | `nsubj` | `blf:subject_argument` | `EXACT_EQUIVALENT` |
| **কর্ম (Karma)** | কর্ম (Karma) | Direct Object (with Differential Object Marking) | `obj` | `blf:direct_object_dom` | `EXACT_EQUIVALENT` |
| **সম্প্রদান (Sampradan)** | গৌণ কর্ম (Gouno Karma) | Indirect Object / Recipient (Dative case) | `iobj` | `blf:indirect_object_dat` | `EXACT_EQUIVALENT` |
| **ক্রিয়া (Kriya)** | ক্রিয়াপদ (Kriyapod) | Finite Verb / Predicate Head | `root` / `verb` | `blf:finite_verb_head` | `EXACT_EQUIVALENT` |
| **যৌগিক ক্রিয়া (Jougik Kriya)** | যৌগিক ক্রিয়া | Compound Verb / Vector Verb Construction | `compound:svc` | `blf:compound_verb_aspectual` | `EXACT_EQUIVALENT` |
| **মিশ্র ক্রিয়া (Mishra Kriya)** | যুক্ত ক্রিয়া (Jukto Kriya) | Light Verb Construction (*kora/howa*) | `compound:lvc` | `blf:light_verb_construction` | `EXACT_EQUIVALENT` |
| **পদাশ্রিত নির্দেশক (Podashrito Nirdeshok)** | নির্দেশক (Nirdeshok) | Numeral Classifier / Definiteness Enclitic | `clf` / `det` | `blf:numeral_classifier` | `EXACT_EQUIVALENT` |
| **অনুসর্গ (Anusorgo)** | অনুসর্গ (Anusorgo) | Postposition (Genitive/Locative-governing) | `case` | `blf:postposition` | `EXACT_EQUIVALENT` |
| **পদক্রম (Podokrom)** | বাক্যের পদক্রম | Constituent Order (Canonical SOV + Scrambling) | `word_order` | `blf:constituent_order_sov` | `EXACT_EQUIVALENT` |
| **সম্বন্ধ পদ (Sombondho Pod)** | সম্বন্ধ পদ | Genitive Modifier / Possessive dependent (-r/-er) | `nmod:poss` | `blf:genitive_modifier` | `EXACT_EQUIVALENT` |
| **অধিকরণ কারক (Odhikoron Karok)** | অধিকরণ (স্থান/কালবাচক) | Locative / Spatial / Temporal Oblique (-e/-te/-y) | `obl:loc` / `obl:tmod` | `blf:locative_argument` | `EXACT_EQUIVALENT` |
| **নঞর্থক অব্যয় (Nojorthok Abyoy)** | না-বাচক পদ | Clause-final / Post-verbal Negator (*na, ni, nei, noy*) | `advmod:neg` | `blf:clause_final_negator` | `EXACT_EQUIVALENT` |
| **মর্যাদা ভেদ (Morjyada Bhed)** | মর্যাদাক্রম | Honorificity Tier (Honorific, Familiar, Intimate) | `Polite=Form/Infm/Elev` | `blf:honorificity_tier` | `EXACT_EQUIVALENT` |
| **অসমাপিকা ক্রিয়া (Asamapika Kriya)**| অসমাপিকা ক্রিয়া | Non-Finite Participle (Conjunctive, Conditional) | `advcl` / `xcomp` | `blf:non_finite_participle` | `EXACT_EQUIVALENT` |

For complete machine-readable field records, definitions, and confidence metadata, see [terminology-crosswalk.json](terminology-crosswalk.json).
