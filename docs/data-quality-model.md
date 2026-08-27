# Data Quality Model & Promotion Architecture — BLF

## 1. Tri-Tier Quality Architecture

BLF categorizes all data entries into three strictly separated tiers:

```
┌────────────────────────────────────────────────────────┐
│                        GOLD                            │
│  Authoritative linguistic seeds & human-verified data  │
└───────────────────────────▲────────────────────────────┘
                            │ (Auditable Human QA Gate)
┌───────────────────────────┴────────────────────────────┐
│                       SILVER                           │
│  Cleaned real-world data passing strict rule validation│
└───────────────────────────▲────────────────────────────┘
                            │ (Deterministic Linguistic Validation)
┌───────────────────────────┴────────────────────────────┐
│                      SYNTHETIC                         │
│  Constrained rule/LLM generated with full provenance   │
└────────────────────────────────────────────────────────┘
```

---

## 2. Quality Tier Specifications

### 2.1 GOLD Tier
- **Definition**: Authoritative linguistic seed structures, manually authored sentences by qualified linguists, or real-world/synthetic data that has undergone double-blind human verification.
- **Criteria**: 100% adherence to Bangla Academy / verified linguistic rules, verified naturalness score $\ge 0.95$, complete morphological and semantic annotation.
- **Storage**: `data/gold/`

### 2.2 SILVER Tier
- **Definition**: Real-world contemporary sentences extracted from open-access verified sources, subjected to automated deduplication, normalization, and syntactic/semantic parsing with automated consistency checks.
- **Criteria**: Schema validity, Unicode normalization, zero character corruption, valid language and register tagging.
- **Storage**: `data/silver/`

### 2.3 SYNTHETIC Tier
- **Definition**: Sentences generated via rule engines or large language models conditioned on structured semantic frames and grammatical constructions.
- **Criteria**: Must carry comprehensive provenance metadata (`source_type`, `generator`, `prompt_hash`, `generation_timestamp`, `conditioning_inputs`). Must NEVER appear unlabeled or masquerade as human data.
- **Storage**: `data/synthetic/`

---

## 3. Auditable Promotion Workflow

Promotion between tiers requires passing explicit validation checkpoints:

1. **SYNTHETIC $\rightarrow$ SILVER**:
   - Automated schema validation pass.
   - Linguistic constraint check (correct honorific agreement, valid case markers).
   - Zero anti-slop violations.
2. **SILVER / SYNTHETIC $\rightarrow$ GOLD**:
   - Native speaker / linguist review.
   - Validation of naturalness, contextual appropriateness, and dialect authenticity.
   - Creation of a signed `PromotionAudit` record containing reviewer ID, timestamp, and review notes.
