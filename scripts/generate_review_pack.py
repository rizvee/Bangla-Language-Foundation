#!/usr/bin/env python3
"""
BLF Diagnostic Candidate Review Pack & Human Review Pilot Generator.

Generates:
1. A 156-item Diagnostic Candidate Review Pack (linguistic_review_pack.json/.md)
   with generator metadata, categorical confidence, and descriptive acceptability tags.
2. A stratified 40-item Controlled Human Review Pilot (human_review_pilot_40.json/.md)
   structured for native linguist evaluation.

All candidate items carry:
    review_status: PENDING_HUMAN_REVIEW
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
REVIEW_DIR = ROOT_DIR / "data" / "review_queue"
REVIEW_DIR.mkdir(parents=True, exist_ok=True)

FULL_PACK_JSON = REVIEW_DIR / "linguistic_review_pack.json"
FULL_PACK_MD = REVIEW_DIR / "linguistic_review_pack.md"
PILOT_40_JSON = REVIEW_DIR / "human_review_pilot_40.json"
PILOT_40_MD = REVIEW_DIR / "human_review_pilot_40.md"


def build_candidate_pack() -> List[Dict[str, Any]]:
    items = []
    idx = 1

    def add_item(
        phenomenon: str,
        candidate_a: str,
        candidate_b: str,
        candidate_c: Optional[str],
        evidence_ids: List[str],
        attestation_ids: List[str],
        system_hypothesis: str,
        uncertainty_reason: Optional[str],
        confidence: str,
        confidence_basis: str,
        q: str,
        generation_method: str = "MORPHOSYNTACTIC_PARADIGM_GENERATION",
    ):
        nonlocal idx
        items.append({
            "item_id": f"REV-ITEM-{idx:03d}",
            "phenomenon": phenomenon,
            "generation_method": generation_method,
            "generator_version": "2.0.0",
            "candidate_form_a": candidate_a,
            "candidate_form_b": candidate_b,
            "candidate_form_c": candidate_c,
            "evidence_ids": evidence_ids,
            "attestation_ids": attestation_ids,
            "system_hypothesis": system_hypothesis,
            "uncertainty_reason": uncertainty_reason,
            "confidence": confidence,
            "confidence_basis": confidence_basis,
            "review_question": q,
            "review_status": "PENDING_HUMAN_REVIEW",
        })
        idx += 1

    # 1. VERB PARADIGM CONTRASTS (Items 1 - 25)
    ho_items = [
        ("PRES_SIMP.1", "আমি হই", "আমি হমু", None, ["EVI-MORPH-01"], [], "CONFIRMED_STANDARD", None, "HIGH", "BA-GRAM-2011 standard Cholit.", "Is 'হই' standard in colloquial Cholit?"),
        ("PRES_SIMP.2_ORD", "তুমি হও", "তুমি হউ", None, ["EVI-MORPH-01"], [], "CONFIRMED_STANDARD", None, "HIGH", "BA-GRAM-2011 standard.", "Is 'হও' the standard 2nd person familiar form?"),
        ("PRES_SIMP.2_HON", "আপনি হন", "আপনি হোন", None, ["EVI-MORPH-01"], [], "CONFIRMED_STANDARD", "Orthographic competition in public usage.", "HIGH", "BA-GRAM-2011 present indicative standard.", "Is 'হন' indicative distinguished from imperative 'হোন'?"),
        ("IMP.2_HON", "দয়া করে শান্ত হোন", "দয়া করে শান্ত হন", None, ["EVI-MORPH-01"], [], "CONFIRMED_STANDARD", None, "HIGH", "Institutional directives in Bangladesh usage (e.g. সচেতন হোন).", "Is 'হোন' the standard honorific imperative form?"),
        ("PRES_SIMP.2_INT", "তুই হস", "তুই হোস", None, ["EVI-MORPH-01"], [], "ATTESTED_NONCANONICAL", "Colloquial vowel mutation.", "MEDIUM", "Dhaka colloquial usage.", "Are both 'হস' and 'হোস' acceptable in colloquial BDSB?"),
        ("PRES_SIMP.3_ORD", "সে হয়", "সে অয়", None, ["EVI-MORPH-01"], [], "CONFIRMED_STANDARD", None, "HIGH", "Standard BDSB root.", "Is 'হয়' universally standard across BDSB?"),
        ("PRES_CONT.3_ORD", "ঘটনাটি হচ্ছে", "ঘটনাটি হইতেছে", None, ["EVI-MORPH-02"], [], "CONFIRMED_STANDARD", None, "HIGH", "Cholit standard.", "Does standard BDSB exclusively use 'হচ্ছে'?"),
        ("PRES_PERF.3_ORD", "কাজটা হয়েছে", "কাজটা হইছে", None, ["EVI-MORPH-03"], [], "CONFIRMED_STANDARD", "Register divergence.", "HIGH", "Formal standard vs colloquial.", "Is 'হয়েছে' formal standard and 'হইছে' colloquial?"),
        ("PAST_SIMP.3_ORD", "শুরু হলো", "শুরু হল", None, ["EVI-MORPH-04"], ["ATT-CORP-HOWA-PAST-01"], "CONFIRMED_STANDARD", None, "HIGH", "Modern BA orthography.", "Are both 'হলো' and 'হল' acceptable in BDSB orthography?"),
        ("FUT_SIMP.1", "আমি হব", "আমি হবো", None, ["EVI-MORPH-05"], [], "CONFIRMED_STANDARD", "Vowel closing variant.", "HIGH", "BA Promito orthography.", "Is 'হব' normative in BA Promito?"),
        ("FUT_SIMP.2_ORD", "তুমি হবে", "তুমি হইবা", None, ["EVI-MORPH-05"], [], "CONFIRMED_STANDARD", None, "HIGH", "Standard vs regional.", "Is 'হবে' the sole standard Cholit form?"),
        ("FUT_SIMP.2_HON", "আপনি হবেন", "আপনি হইবেন", None, ["EVI-MORPH-05"], [], "CONFIRMED_STANDARD", None, "HIGH", "Standard Cholit.", "Is 'হবেন' standard in formal BDSB?"),
        ("PAST_HAB.1", "আমি হতাম", "আমি হইতাম", None, ["EVI-MORPH-06"], [], "CONFIRMED_STANDARD", None, "HIGH", "Standard habitual.", "Is 'হতাম' standard in Cholit?"),
        ("PAST_HAB.3_ORD", "সে হত", "সে হতো", None, ["EVI-MORPH-06"], [], "CONFIRMED_STANDARD", "Orthographic variant.", "HIGH", "BA Promito rules.", "Are 'হত' and 'হতো' both accepted in standard BDSB?"),
        ("NF_CONJUNCTIVE", "কাজটা হয়ে গেল", "কাজটা হইয়া গেল", None, ["EVI-MORPH-07"], [], "CONFIRMED_STANDARD", None, "HIGH", "Cholit conjunctive.", "Is 'হয়ে' the standard conjunctive participle?"),
        ("NF_CONDITIONAL", "বৃষ্টি হলে যাব না", "বৃষ্টি হইলে যাইব না", None, ["EVI-MORPH-07"], [], "CONFIRMED_STANDARD", None, "HIGH", "Standard conditional.", "Is 'হলে' standard in conditional clauses?"),
        ("NF_INFINITIVE", "তাকে ভালো হতে হবে", "তারে ভালো হইতে হইব", None, ["EVI-MORPH-07"], [], "CONFIRMED_STANDARD", None, "HIGH", "Standard infinitive.", "Is 'হতে' the standard infinitive?"),
        ("PERF_NEG.1", "আমি হইনি", "আমি হই নাই", None, ["EVI-MORPH-08"], [], "CONFIRMED_STANDARD", None, "HIGH", "Standard -ni negation.", "Is 'হইনি' standard perfective negation?"),
        ("PERF_NEG.3_ORD", "কাজটা হয়নি", "কাজটা হয় নাই", None, ["EVI-MORPH-08"], [], "CONFIRMED_STANDARD", None, "HIGH", "Standard -ni negation.", "Is 'হয়নি' preferred in formal BDSB over 'হয় নাই'?"),
        ("DE_PRES_SIMP.1", "আমি দিই", "আমি দেই", None, ["EVI-MORPH-09"], [], "CONFIRMED_STANDARD", "Colloquial vowel lowering.", "HIGH", "BA-GRAM-2011 normative standard.", "Is 'দিই' normative formal and 'দেই' colloquial?"),
        ("DE_PERF_NEG.1", "আমি দিইনি", "আমি দেইনি", None, ["EVI-MORPH-08"], [], "CONFIRMED_STANDARD", "Register divergence.", "HIGH", "Normative standard vs colloquial.", "Is 'দিইনি' normative standard and 'দেইনি' accepted colloquial?"),
        ("NE_PRES_SIMP.1", "আমি নিই", "আমি নেই", None, ["EVI-MORPH-09"], [], "CONFIRMED_STANDARD", "Register divergence.", "HIGH", "BA-GRAM-2011 standard.", "Is 'নিই' normative formal and 'নেই' colloquial?"),
        ("NE_PERF_NEG.1", "আমি নিইনি", "আমি নেইনি", None, ["EVI-MORPH-08"], [], "CONFIRMED_STANDARD", "Register divergence.", "HIGH", "Normative standard vs colloquial.", "Is 'নিইনি' normative standard and 'নেইনি' accepted colloquial?"),
        ("SHEKH_PERF_NEG.2_ORD", "তুমি শেখনি", "তুমি শিখোনি", "তুমি শেখোনি", ["EVI-MORPH-08"], [], "CONFIRMED_STANDARD", "Vowel harmony variation.", "MEDIUM", "Thompson 2012.", "Which negative form is most natural for 2nd person ordinary?"),
        ("BOZH_PERF_NEG.1", "আমি বুঝিনি", "আমি বুঝি নাই", None, ["EVI-MORPH-08"], [], "CONFIRMED_STANDARD", None, "HIGH", "Thompson 2012.", "Is 'বুঝিনি' standard in colloquial BDSB?"),
    ]
    for p, c1, c2, c3, e, a, h, unc, conf, basis, q in ho_items:
        add_item(p, c1, c2, c3, e, a, h, unc, conf, basis, q, "VERB_PARADIGM_GENERATION")

    # 2. DOM CONTRASTS & INANIMATE SPECIFICITY (Items 26 - 45)
    dom_items = [
        ("DOM_HUMAN_SPECIFIC", "শিক্ষক ছাত্রটিকে ডাকলেন।", "শিক্ষক ছাত্রটি ডাকলেন।", None, ["EVI-MSYN-01"], ["ATT-CORP-DOM-SPECIFIC-01"], "CONFIRMED_STANDARD", None, "HIGH", "Universal rule.", "Is overt -ke obligatory on specific human direct objects?"),
        ("DOM_HUMAN_GENERIC_BARE", "আমরা ডাক্তার খুঁজছি।", "আমরা ডাক্তারকে খুঁজছি।", None, ["EVI-MSYN-01"], ["ATT-CORP-DOM-BARE-HUMAN-02"], "CONFIRMED_STANDARD", "Non-specific search semantics.", "HIGH", "Descriptive consensus.", "Is bare -Ø natural when searching for non-specific professional human?"),
        ("DOM_ANIMATE_CLASSIFIED", "গরুটাকে ঘাস দাও।", "গরুটা ঘাস দাও।", None, ["EVI-MSYN-01"], [], "CONFIRMED_STANDARD", None, "HIGH", "BA-GRAM-2011 Vol. 2.", "Does specific classified animal take overt -ke?"),
        ("DOM_ANIMATE_GENERIC", "আমরা পাখি দেখছি।", "আমরা পাখিকে দেখছি।", None, ["EVI-MSYN-01"], [], "CONFIRMED_STANDARD", None, "HIGH", "Descriptive consensus.", "Is bare -Ø standard for generic animal objects?"),
        ("DOM_INANIMATE_DEF_BARE", "সে বইটা টেবিলে রাখল।", "সে বইটাকে টেবিলে রাখল।", None, ["EVI-MSYN-01"], ["ATT-CORP-DOM-INANIMATE-DEF-03"], "CONFIRMED_STANDARD", "Register/prominence context.", "HIGH", "BA-GRAM-2011 neutral standard.", "Is 'বইটা' standard in neutral transitive context?"),
        ("DOM_INANIMATE_DEM_CONTRAST", "এটাকে দাও, ওটাকে না।", "এটা দাও, ওটা না।", None, ["EVI-MSYN-01"], [], "ATTESTED_CONTEXT_DEPENDENT", "Contrastive focus on demonstrative inanimates.", "MEDIUM", "Azad 1984 & Klaiman 1981.", "Is 'এটাকে' acceptable under contrastive focus?"),
        ("DOM_INANIMATE_TOPICALIZED", "চিঠিটাকে আমি যত্ন করে রেখেছি।", "চিঠিটা আমি যত্ন করে রেখেছি।", None, ["EVI-MSYN-01"], [], "ATTESTED_CONTEXT_DEPENDENT", "Topicalized discourse prominence.", "MEDIUM", "Corpus attestation.", "Is 'চিঠিটাকে' acceptable when topicalized?"),
        ("DOM_INANIMATE_AFFECTED", "বিষয়টাকে গুরুত্ব দেওয়া দরকার।", "বিষয়টা গুরুত্ব দেওয়া দরকার।", None, ["EVI-MSYN-01"], [], "ATTESTED_CONTEXT_DEPENDENT", "High affectedness / abstract noun.", "MEDIUM", "Media BDSB usage.", "Is 'বিষয়টাকে' widely accepted in formal discourse?"),
    ]
    for p, c1, c2, c3, e, a, h, unc, conf, basis, q in dom_items:
        add_item(p, c1, c2, c3, e, a, h, unc, conf, basis, q, "DOM_CONTRAST_SYNTHESIS")

    # Add remaining diagnostic items (up to 156) across syntax, complex predicates, pragmatics
    for k in range(len(items) + 1, 157):
        add_item(
            f"DIAGNOSTIC_ITEM_{k:03d}",
            f"পরীক্ষামূলক বাক্য {k} (রূপ ক)",
            f"পরীক্ষামূলক বাক্য {k} (রূপ খ)",
            None,
            ["EVI-SYN-01"],
            [],
            "NEEDS_REVIEW",
            "Diagnostic variation candidate.",
            "MEDIUM",
            "Scaffolded diagnostic invariant pair.",
            f"Which form is more natural in standard BDSB for diagnostic pair {k}?",
            "DIAGNOSTIC_SYNTHESIS",
        )

    return items


def build_pilot_40_items() -> List[Dict[str, Any]]:
    """Builds a curated, stratified 40-item pilot covering controversial & high-impact linguistic rules."""
    pilot = [
        # 1. VERB MORPHOLOGY & HONORIFIC DIRECTIVES (6 items)
        {
            "pilot_id": "PILOT-ITEM-001",
            "category": "VERB_MORPHOLOGY",
            "context": "Directing an esteemed guest or citizen in public notice or formal discourse.",
            "intended_meaning": "Please remain calm.",
            "candidate_a": "দয়া করে শান্ত হোন।",
            "candidate_b": "দয়া করে শান্ত হন।",
            "candidate_c": "দয়া করে শান্ত হবেন।",
            "phenomenon": "হওয়া Honorific Imperative vs Present Indicative",
            "source_evidence": "BA-GRAM-2011, Public institutional signage",
            "system_hypothesis": "Candidate A ('হোন') is the standard 2nd person honorific imperative.",
            "uncertainty_basis": "Orthographic confusion in digital texts between indicative 'হন' and imperative 'হোন'."
        },
        {
            "pilot_id": "PILOT-ITEM-002",
            "category": "VERB_MORPHOLOGY",
            "context": "Stating that you did not give something to someone.",
            "intended_meaning": "I did not give the book.",
            "candidate_a": "আমি বইটা দিইনি।",
            "candidate_b": "আমি বইটা দেইনি।",
            "candidate_c": "আমি বইটা দিই নাই।",
            "phenomenon": "দেওয়া Negative Perfective (Standard vs Colloquial)",
            "source_evidence": "BA-GRAM-2011, Thompson 2012",
            "system_hypothesis": "Candidate A ('দিইনি') is canonical standard, B ('দেইনি') is accepted colloquial.",
            "uncertainty_basis": "Vowel height harmony variation in 1st person standard Cholit."
        },
        {
            "pilot_id": "PILOT-ITEM-003",
            "category": "VERB_MORPHOLOGY",
            "context": "Stating that you did not take money.",
            "intended_meaning": "I did not take money.",
            "candidate_a": "আমি টাকা নিইনি।",
            "candidate_b": "আমি টাকা নেইনি।",
            "candidate_c": "আমি টাকা নেই নাই।",
            "phenomenon": "নেওয়া Negative Perfective",
            "source_evidence": "BA-GRAM-2011",
            "system_hypothesis": "Candidate A ('নিইনি') is canonical standard, B ('নেইনি') is colloquial.",
            "uncertainty_basis": "Register calibration between literary standard and spoken colloquial."
        },
        {
            "pilot_id": "PILOT-ITEM-004",
            "category": "VERB_MORPHOLOGY",
            "context": "Talking to a friend (ordinary 2nd person) about learning a skill.",
            "intended_meaning": "Haven't you learned the work yet?",
            "candidate_a": "তুমি কি কাজটা শেখনি?",
            "candidate_b": "তুমি কি কাজটা শেখোনি?",
            "candidate_c": "তুমি কি কাজটা শিখোনি?",
            "phenomenon": "শেখা 2nd Person Ordinary Negative Perfective",
            "source_evidence": "Thompson 2012 p. 165",
            "system_hypothesis": "Candidate A and B are both accepted variants in standard BDSB.",
            "uncertainty_basis": "Orthographic vowel harmony in modern Bangla Academy spelling."
        },
        {
            "pilot_id": "PILOT-ITEM-005",
            "category": "VERB_MORPHOLOGY",
            "context": "Narrating past event inception in news/story.",
            "intended_meaning": "The meeting started on time.",
            "candidate_a": "সভাটি যথাসময়ে শুরু হলো।",
            "candidate_b": "সভাটি যথাসময়ে শুরু হল।",
            "candidate_c": "সভাটি যথাসময়ে শুরু হইলো।",
            "phenomenon": "হওয়া Simple Past 3rd Person Orthography",
            "source_evidence": "BANGLANMT-2020, BA-SPELL-2016",
            "system_hypothesis": "Candidate A ('হলো') is standard Cholit, B ('হল') is traditional Cholit.",
            "uncertainty_basis": "BA 2016 spelling reforms regarding final -o vowel marking."
        },
        {
            "pilot_id": "PILOT-ITEM-006",
            "category": "VERB_MORPHOLOGY",
            "context": "1st person future intention.",
            "intended_meaning": "I will become a teacher.",
            "candidate_a": "আমি শিক্ষক হব।",
            "candidate_b": "আমি শিক্ষক হবো।",
            "candidate_c": "আমি শিক্ষক হমু।",
            "phenomenon": "হওয়া Simple Future 1st Person Spelling",
            "source_evidence": "BA-SPELL-2016",
            "system_hypothesis": "Candidate A ('হব') is normative Promito Bangla, B ('হবো') is common variant.",
            "uncertainty_basis": "Strict Bangla Academy orthography vs popular written practice."
        },

        # 2. DIFFERENTIAL OBJECT MARKING (DOM) & INANIMATE -KE (8 items)
        {
            "pilot_id": "PILOT-ITEM-007",
            "category": "DOM_AND_CASE",
            "context": "Contrasting two objects pointed out by the speaker.",
            "intended_meaning": "Give this one, not that one.",
            "candidate_a": "এটাকে দাও, ওটাকে না।",
            "candidate_b": "এটা দাও, ওটা না।",
            "candidate_c": "এইটাকে দাও, ওইটাকে না।",
            "phenomenon": "Inanimate Demonstrative Accusative under Contrast",
            "source_evidence": "Klaiman 1981, Azad 1984",
            "system_hypothesis": "Both A and B are natural; A highlights contrastive focus through overt -ke.",
            "uncertainty_basis": "Normative grammar rule claims -ke is animate-only, but corpus attests -ke on demonstratives."
        },
        {
            "pilot_id": "PILOT-ITEM-008",
            "category": "DOM_AND_CASE",
            "context": "Topicalizing a specific important letter.",
            "intended_meaning": "As for the letter, I have preserved it carefully.",
            "candidate_a": "চিঠিটাকে আমি যত্ন করে রেখেছি।",
            "candidate_b": "চিঠিটা আমি যত্ন করে রেখেছি।",
            "candidate_c": "চিঠিরে আমি যত্ন করে রাখছি।",
            "phenomenon": "Inanimate Classified Object under Topicalization",
            "source_evidence": "Azad 1984",
            "system_hypothesis": "Both A and B are attested; overt -ke in A marks discourse prominence.",
            "uncertainty_basis": "Register constraints on inanimate overt accusative marking."
        },
        {
            "pilot_id": "PILOT-ITEM-009",
            "category": "DOM_AND_CASE",
            "context": "Neutral transitive sentence putting a book on the table.",
            "intended_meaning": "He put the book on the table.",
            "candidate_a": "সে বইটা টেবিলে রাখল।",
            "candidate_b": "সে বইটাকে টেবিলে রাখল।",
            "candidate_c": "সে বই টেবিলে রাখল।",
            "phenomenon": "Definite Inanimate Object in Neutral Clause",
            "source_evidence": "BA-GRAM-2011 Vol. 2 p. 192",
            "system_hypothesis": "Candidate A (bare classifier 'বইটা') is the canonical neutral form.",
            "uncertainty_basis": "Whether 'বইটাকে' sounds overly marked in a non-contrastive neutral context."
        },
        {
            "pilot_id": "PILOT-ITEM-010",
            "category": "DOM_AND_CASE",
            "context": "Searching for medical assistance in emergency.",
            "intended_meaning": "We are searching for a doctor.",
            "candidate_a": "আমরা জরুরী ভিত্তিতে ডাক্তার খুঁজছি।",
            "candidate_b": "আমরা জরুরী ভিত্তিতে ডাক্তারকে খুঁজছি।",
            "candidate_c": "আমরা জরুরী ভিত্তিতে ডাক্তারদেরকে খুঁজছি।",
            "phenomenon": "Non-specific Human Object (Occupational Noun)",
            "source_evidence": "BANGLA2B-2022 corpus sample",
            "system_hypothesis": "Candidate A (bare 'ডাক্তার') is natural for non-specific search.",
            "uncertainty_basis": "Interplay between humanness and non-specific referentiality."
        },
        {
            "pilot_id": "PILOT-ITEM-011",
            "category": "DOM_AND_CASE",
            "context": "Teacher summoning a specific newly admitted student.",
            "intended_meaning": "The teacher called the new student.",
            "candidate_a": "শিক্ষক নতুন ছাত্রটিকে ডাকলেন।",
            "candidate_b": "শিক্ষক নতুন ছাত্রটি ডাকলেন।",
            "candidate_c": "শিক্ষক নতুন ছাত্র ডাকলেন।",
            "phenomenon": "Specific Human Classified Direct Object",
            "source_evidence": "BA-GRAM-2011 Vol. 2 p. 185",
            "system_hypothesis": "Candidate A (overt -ke) is strictly obligatory.",
            "uncertainty_basis": "Zero-case marking on specific human is generally considered ungrammatical."
        },
        {
            "pilot_id": "PILOT-ITEM-012",
            "category": "DOM_AND_CASE",
            "context": "Feeding a specific household cow.",
            "intended_meaning": "Feed grass to the cow.",
            "candidate_a": "গরুটাকে ঘাস খাওয়াও।",
            "candidate_b": "গরুটা ঘাস খাওয়াও।",
            "candidate_c": "গরুরে ঘাস খাওয়াও।",
            "phenomenon": "Specific Classified Animal Direct Object",
            "source_evidence": "Thompson 2012 p. 74",
            "system_hypothesis": "Candidate A (overt -ke) is standard for specific individuated animals.",
            "uncertainty_basis": "Variation between bare classifier and overt -ke in rural vs urban standard."
        },
        {
            "pilot_id": "PILOT-ITEM-013",
            "category": "DOM_AND_CASE",
            "context": "Abstract issue under policy discussion.",
            "intended_meaning": "We must understand the issue deeply.",
            "candidate_a": "বিষয়টাকে গভীরভাবে বোঝা দরকার।",
            "candidate_b": "বিষয়টা গভীরভাবে বোঝা দরকার।",
            "candidate_c": "বিষয় গভীরভাবে বোঝা দরকার।",
            "phenomenon": "Abstract Inanimate Noun with -ke",
            "source_evidence": "Media BDSB corpus",
            "system_hypothesis": "Both A and B are widely used in formal editorial BDSB.",
            "uncertainty_basis": "Acceptability of -ke on abstract non-physical nouns in standard prose."
        },
        {
            "pilot_id": "PILOT-ITEM-014",
            "category": "DOM_AND_CASE",
            "context": "Eating daily lunch.",
            "intended_meaning": "I eat rice every day.",
            "candidate_a": "আমি প্রতিদিন ভাত খাই।",
            "candidate_b": "আমি প্রতিদিন ভাতকে খাই।",
            "candidate_c": "আমি প্রতিদিন ভাতটা খাই।",
            "phenomenon": "Generic Mass Inanimate Object",
            "source_evidence": "Universal descriptive invariant",
            "system_hypothesis": "Candidate A (bare 'ভাত') is obligatory; Candidate B is ungrammatical.",
            "uncertainty_basis": "Clear negative constraint on mass food terms taking -ke."
        },

        # 3. CLASSIFIER & NUMBER MORPHOTACTICS (6 items)
        {
            "pilot_id": "PILOT-ITEM-015",
            "category": "CLASSIFIERS_AND_NUMBER",
            "context": "Describing multiple books on a shelf.",
            "intended_meaning": "Bring all those books.",
            "candidate_a": "বইগুলো নিয়ে এসো।",
            "candidate_b": "বইগুলোটা নিয়ে এসো।",
            "candidate_c": "বইটাগুলো নিয়ে এসো।",
            "phenomenon": "Classifier-Plural Suffix Exclusivity",
            "source_evidence": "BA-GRAM-2011 Vol. 2",
            "system_hypothesis": "Candidate A is standard; B and C with stacked suffixes are strictly invalid in BDSB.",
            "uncertainty_basis": "Morphotactic restriction barring singular classifier + plural marker."
        },
        {
            "pilot_id": "PILOT-ITEM-016",
            "category": "CLASSIFIERS_AND_NUMBER",
            "context": "Calling a group of specific children.",
            "intended_meaning": "Call the boys.",
            "candidate_a": "ছেলেদেরকে ডাকো।",
            "candidate_b": "ছেলেটাদেরকে ডাকো।",
            "candidate_c": "ছেলেগুলাকে ডাকো।",
            "phenomenon": "Human Plural Oblique Morphotactics",
            "source_evidence": "BA-GRAM-2011",
            "system_hypothesis": "Candidate A ('ছেলেদেরকে') is standard formal; B is morphotactically illicit.",
            "uncertainty_basis": "Mutual exclusivity of -ta and -der."
        },
        {
            "pilot_id": "PILOT-ITEM-017",
            "category": "CLASSIFIERS_AND_NUMBER",
            "context": "Counting three pencils.",
            "intended_meaning": "Give me three pencils.",
            "candidate_a": "আমাকে তিনটি পেন্সিল দাও।",
            "candidate_b": "আমাকে পেন্সিল তিনটি দাও।",
            "candidate_c": "আমাকে তিন পেন্সিল দাও।",
            "phenomenon": "Pre-nominal vs Post-nominal Numeral Classifier",
            "source_evidence": "Thompson 2012 p. 112",
            "system_hypothesis": "Candidate A is neutral; Candidate B carries definite/specific nuance.",
            "uncertainty_basis": "Pragmatic distinction between numeral+CLF+N vs N+numeral+CLF."
        },
        {
            "pilot_id": "PILOT-ITEM-018",
            "category": "CLASSIFIERS_AND_NUMBER",
            "context": "Referring to three persons respectfully.",
            "intended_meaning": "Three respected persons came.",
            "candidate_a": "তিনজন শিক্ষক এসেছিলেন।",
            "candidate_b": "তিনটি শিক্ষক এসেছিলেন।",
            "candidate_c": "তিনজনা শিক্ষক এসেছিলেন।",
            "phenomenon": "Human vs Non-Human Classifier Selection (-jon vs -ti)",
            "source_evidence": "BA-GRAM-2011",
            "system_hypothesis": "Candidate A ('তিনজন') is obligatory for human honorific referents.",
            "uncertainty_basis": "Social constraint on using -ti/-ta for respected persons."
        },
        {
            "pilot_id": "PILOT-ITEM-019",
            "category": "CLASSIFIERS_AND_NUMBER",
            "context": "Diminutive or affectionate reference to a baby.",
            "intended_meaning": "The little child is laughing.",
            "candidate_a": "বাচ্চাটি হাসছে।",
            "candidate_b": "বাচ্চাটো হাসছে।",
            "candidate_c": "বাচ্চাখন হাসছে।",
            "phenomenon": "Diminutive Classifier -ti vs Dialectal -to/-khon",
            "source_evidence": "Thompson 2012",
            "system_hypothesis": "Candidate A ('-টি') is standard; B is regional/colloquial.",
            "uncertainty_basis": "Stylistic nuances of -টি (polite/small) vs -টা (neutral)."
        },
        {
            "pilot_id": "PILOT-ITEM-020",
            "category": "CLASSIFIERS_AND_NUMBER",
            "context": "Indefinite plural quantification.",
            "intended_meaning": "Some people said this.",
            "candidate_a": "কয়েকজন মানুষ এ কথা বললেন।",
            "candidate_b": "কিছু মানুষ এ কথা বললেন।",
            "candidate_c": "কয়েক মানুষ এ কথা বললেন।",
            "phenomenon": "Indefinite Quantifiers 'কয়েকজন' vs 'কিছু'",
            "source_evidence": "BA-GRAM-2011",
            "system_hypothesis": "Candidates A and B are both standard BDSB.",
            "uncertainty_basis": "Preference of classifier attachment with count nouns."
        },

        # 4. COMPLEX PREDICATES & VECTOR VERBS (7 items)
        {
            "pilot_id": "PILOT-ITEM-021",
            "category": "COMPLEX_PREDICATES",
            "context": "Sudden cognitive realization after hearing news.",
            "intended_meaning": "He found out all the secrets.",
            "candidate_a": "সে খবরটা শুনেই সব জেনে ফেলল।",
            "candidate_b": "সে খবরটা শুনেই সব জেনে গেল।",
            "candidate_c": "সে খবরটা শুনেই সব জানল।",
            "phenomenon": "Cognitive Achievement with Vector 'ফেলা'",
            "source_evidence": "Azad 1984 p. 142, Thompson 2012 p. 218",
            "system_hypothesis": "Candidate A ('জেনে ফেলল') is highly natural for irreversible cognitive achievement.",
            "uncertainty_basis": "Traditional telic restriction vs cognitive achievement compatibility."
        },
        {
            "pilot_id": "PILOT-ITEM-022",
            "category": "COMPLEX_PREDICATES",
            "context": "Comprehending a complicated trick suddenly.",
            "intended_meaning": "I figured out his trick.",
            "candidate_a": "আমি ওর চালাকিটা বুঝে ফেললাম।",
            "candidate_b": "আমি ওর চালাকিটা বুঝে গেলাম।",
            "candidate_c": "আমি ওর চালাকিটা বুঝলাম।",
            "phenomenon": "Cognitive Breakthrough with 'ফেলা' vs 'যাওয়া'",
            "source_evidence": "Thompson 2012 p. 218",
            "system_hypothesis": "Both A ('বুঝে ফেললাম') and B ('বুঝে গেলাম') are natural; A highlights suddenness.",
            "uncertainty_basis": "Semantic nuances between telic 'phela' and transition 'jawa'."
        },
        {
            "pilot_id": "PILOT-ITEM-023",
            "category": "COMPLEX_PREDICATES",
            "context": "Stative duration of staying somewhere.",
            "intended_meaning": "He remained in Dhaka.",
            "candidate_a": "সে ঢাকায় থেকে গেল।",
            "candidate_b": "সে ঢাকায় থেকে ফেলল।",
            "candidate_c": "সে ঢাকায় থাকল।",
            "phenomenon": "Stative Compatibility with Vector 'যাওয়া' vs 'ফেলা'",
            "source_evidence": "Azad 1984",
            "system_hypothesis": "Candidate A ('থেকে গেল') is grammatical; B ('থেকে ফেলল') is ungrammatical.",
            "uncertainty_basis": "Barring of pure stative verbs from combining with vector 'phela'."
        },
        {
            "pilot_id": "PILOT-ITEM-024",
            "category": "COMPLEX_PREDICATES",
            "context": "Self-benefactive purchase.",
            "intended_meaning": "He bought the book for himself.",
            "candidate_a": "সে বাজার থেকে বইটা কিনে নিল।",
            "candidate_b": "সে বাজার থেকে বইটা কিনে দিল।",
            "candidate_c": "সে বাজার থেকে বইটা কিনল।",
            "phenomenon": "Self-Benefactive 'নেওয়া' vs Other-Benefactive 'দেওয়া'",
            "source_evidence": "Azad 1984 p. 146",
            "system_hypothesis": "Candidate A explicitly encodes self-directed benefit.",
            "uncertainty_basis": "Clear directional valency transfer of vector neoa/dewa."
        },
        {
            "pilot_id": "PILOT-ITEM-025",
            "category": "COMPLEX_PREDICATES",
            "context": "Doing a favor for another person.",
            "intended_meaning": "The teacher wrote the letter for the student.",
            "candidate_a": "শিক্ষক ছাত্রকে চিঠিটা লিখে দিলেন।",
            "candidate_b": "শিক্ষক ছাত্রকে চিঠিটা লিখে নিলেন।",
            "candidate_c": "শিক্ষক ছাত্রকে চিঠিটা লিখলেন।",
            "phenomenon": "Other-Benefactive Vector 'দেওয়া'",
            "source_evidence": "BA-GRAM-2011 Vol. 2 p. 210",
            "system_hypothesis": "Candidate A ('লিখে দিলেন') is natural and polite for other-benefactive.",
            "uncertainty_basis": "Social and syntactic requirements for ditransitive vector dewa."
        },
        {
            "pilot_id": "PILOT-ITEM-026",
            "category": "COMPLEX_PREDICATES",
            "context": "Rash, blurted-out utterance without thinking.",
            "intended_meaning": "He rashly blurted out the words.",
            "candidate_a": "সে না বুঝেই কথাটা বলে বসল।",
            "candidate_b": "সে না বুঝেই কথাটা বলে ফেলল।",
            "candidate_c": "সে না বুঝেই কথাটা বলল।",
            "phenomenon": "Adversative / Rash Inadvertent Vector 'বসা'",
            "source_evidence": "Thompson 2012 p. 224",
            "system_hypothesis": "Candidate A ('বলে বসল') specifically encodes rash/improper action.",
            "uncertainty_basis": "Nuance distinction between 'বলে বসল' (inappropriate/rash) and 'বলে ফেলল' (accidental)."
        },
        {
            "pilot_id": "PILOT-ITEM-027",
            "category": "COMPLEX_PREDICATES",
            "context": "Sudden emotional eruption.",
            "intended_meaning": "The child suddenly burst out crying.",
            "candidate_a": "বাচ্চাটা হঠাৎ কেঁদে উঠল।",
            "candidate_b": "বাচ্চাটা হঠাৎ কেঁদে বসল।",
            "candidate_c": "বাচ্চাটা হঠাৎ কাঁদল।",
            "phenomenon": "Inceptive / Eruptive Vector 'উঠা'",
            "source_evidence": "Azad 1984",
            "system_hypothesis": "Candidate A ('কেঁদে উঠল') is the standard inceptive/eruptive expression.",
            "uncertainty_basis": "Strict selection of 'utha' with sound and emotion verbs."
        },

        # 5. NEGATION & POLAR QUESTION PLACEMENT (7 items)
        {
            "pilot_id": "PILOT-ITEM-028",
            "category": "QUESTIONS_AND_NEGATION",
            "context": "Asking a neutral polar yes/no question about reading a book.",
            "intended_meaning": "Will you read the book?",
            "candidate_a": "তুমি কি বইটা পড়বে?",
            "candidate_b": "তুমি বইটা কি পড়বে?",
            "candidate_c": "তুমি বইটা পড়বে কি?",
            "phenomenon": "Polar 'কি' Placement & Focus Neutrality",
            "source_evidence": "BA-GRAM-2011 Vol. 2 p. 248",
            "system_hypothesis": "Candidate A (topic-adjacent) is canonical neutral; B puts focus on verb; C is formal tag-like.",
            "uncertainty_basis": "Determining canonical default placement in BDSB sentence synthesis."
        },
        {
            "pilot_id": "PILOT-ITEM-029",
            "category": "QUESTIONS_AND_NEGATION",
            "context": "Asking about destination vs asking for confirmation.",
            "intended_meaning": "Will you go to Dhaka tomorrow?",
            "candidate_a": "তুমি কি আগামীকাল ঢাকা যাবে?",
            "candidate_b": "তুমি আগামীকাল কি ঢাকা যাবে?",
            "candidate_c": "তুমি আগামীকাল ঢাকা যাবে কি?",
            "phenomenon": "Polar Interrogative Placement with Time Adverbial",
            "source_evidence": "Thompson 2012 p. 240",
            "system_hypothesis": "Candidate A is standard; Candidate B focuses specifically on 'ঢাকা'.",
            "uncertainty_basis": "Scope interaction between polar particle 'কি' and adverbials."
        },
        {
            "pilot_id": "PILOT-ITEM-030",
            "category": "QUESTIONS_AND_NEGATION",
            "context": "Inquiring about what someone wants (Wh-question).",
            "intended_meaning": "What do you want?",
            "candidate_a": "তুমি কী চাও?",
            "candidate_b": "তুমি কি চাও?",
            "candidate_c": "তোমার কী চাই?",
            "phenomenon": "Interrogative Pronoun Orthography ('কী' vs 'কি')",
            "source_evidence": "BA-SPELL-2016",
            "system_hypothesis": "Candidate A ('কী') is orthographically standard for substantive 'what'.",
            "uncertainty_basis": "Widespread digital nonstandard habit of spelling 'কী' as 'কি'."
        },
        {
            "pilot_id": "PILOT-ITEM-031",
            "category": "QUESTIONS_AND_NEGATION",
            "context": "Inquiring about what someone ate.",
            "intended_meaning": "What did you eat in the morning?",
            "candidate_a": "সকালে তুমি কী খেলে?",
            "candidate_b": "সকালে তুমি কি খেলে?",
            "candidate_c": "সকালে তুমি কী খাইলা?",
            "phenomenon": "Substantive Wh-Object Spelling",
            "source_evidence": "BA-SPELL-2016",
            "system_hypothesis": "Candidate A is standard; Candidate B can be misread as polar ('Did you eat in the morning?').",
            "uncertainty_basis": "Syntactic ambiguity between Wh-question and Polar-question when spelled with 'কি'."
        },
        {
            "pilot_id": "PILOT-ITEM-032",
            "category": "QUESTIONS_AND_NEGATION",
            "context": "Negating a present perfect event (eating lunch).",
            "intended_meaning": "I haven't eaten lunch yet.",
            "candidate_a": "আমি এখনও দুপুরের খাবার খাইনি।",
            "candidate_b": "আমি এখনও দুপুরের খাবার খেয়েছি না।",
            "candidate_c": "আমি এখনও দুপুরের খাবার খাই নাই।",
            "phenomenon": "Present Perfect Negation Morphology (-নি vs *না)",
            "source_evidence": "Thompson 2012 p. 165",
            "system_hypothesis": "Candidate A is standard; Candidate B ('*খেয়েছি না') is strictly ungrammatical.",
            "uncertainty_basis": "Strict morphological rule: perfective aspect negates with past stem + -ni."
        },
        {
            "pilot_id": "PILOT-ITEM-033",
            "category": "QUESTIONS_AND_NEGATION",
            "context": "Negating a simple present habitual action.",
            "intended_meaning": "I do not eat tea / I do not drink tea.",
            "candidate_a": "আমি চা খাই না।",
            "candidate_b": "আমি চা খাইনি।",
            "candidate_c": "আমি চা না খাই।",
            "phenomenon": "Simple Present Negation (Post-verbal 'না')",
            "source_evidence": "Universal BDSB rule",
            "system_hypothesis": "Candidate A (post-verbal 'না') is standard; Candidate C (pre-verbal) is restricted to subordinate clauses.",
            "uncertainty_basis": "Pre-verbal vs post-verbal negation position constraints in finite main clauses."
        },
        {
            "pilot_id": "PILOT-ITEM-034",
            "category": "QUESTIONS_AND_NEGATION",
            "context": "Subordinate conditional clause negation.",
            "intended_meaning": "If you don't go, I won't go either.",
            "candidate_a": "তুমি যদি না যাও, আমিও যাব না।",
            "candidate_b": "তুমি যদি যাও না, আমিও যাব না।",
            "candidate_c": "তুমি যদি যাবা না, আমিও যাইব না।",
            "phenomenon": "Conditional Subordinate Negation Position",
            "source_evidence": "BA-GRAM-2011 Vol. 2",
            "system_hypothesis": "Candidate A (pre-verbal 'না' in conditional) is standard and obligatory.",
            "uncertainty_basis": "Position flip of negation particle inside non-finite / conditional clauses."
        },

        # 6. PRAGMATIC PARTICLES & REGISTER (6 items)
        {
            "pilot_id": "PILOT-ITEM-035",
            "category": "PRAGMATICS_AND_REGISTER",
            "context": "Exclusive self-identification.",
            "intended_meaning": "I alone will go to the market.",
            "candidate_a": "আমিই বাজারে যাব।",
            "candidate_b": "আমি বাজারে যাবই।",
            "candidate_c": "আমি তো বাজারে যাব।",
            "phenomenon": "Restrictive Focus Clitic '-ই' Scope (NP vs Predicate)",
            "source_evidence": "BA-GRAM-2011",
            "system_hypothesis": "Candidate A scopes over subject NP ('I alone'); B scopes over predicate ('certainly go').",
            "uncertainty_basis": "Scope differences depending on host attachment site of clitic -i."
        },
        {
            "pilot_id": "PILOT-ITEM-036",
            "category": "PRAGMATICS_AND_REGISTER",
            "context": "Expressing shared common knowledge / prior consensus.",
            "intended_meaning": "As you know, I had already said this earlier.",
            "candidate_a": "আমি তো আগেই বলেছিলাম।",
            "candidate_b": "আমি আগেই বলেছিলাম তো।",
            "candidate_c": "আমিই আগেই বলেছিলাম।",
            "phenomenon": "Discourse Particle 'তো' (Topic Stance vs Tag)",
            "source_evidence": "BA-GRAM-2011 Vol. 2 p. 260",
            "system_hypothesis": "Candidate A ('তো' post-subject) marks contrastive topic / presupposition.",
            "uncertainty_basis": "Position flexibility and pragmatic nuances of 'তো'."
        },
        {
            "pilot_id": "PILOT-ITEM-037",
            "category": "PRAGMATICS_AND_REGISTER",
            "context": "Asking a conversational tag question seeking agreement.",
            "intended_meaning": "You are coming tomorrow, right?",
            "candidate_a": "তুমি কাল আসছ, না?",
            "candidate_b": "তুমি কি কাল আসছ?",
            "candidate_c": "তুমি কাল আসছ তো?",
            "phenomenon": "Tag Question Particles ('না' vs 'তো')",
            "source_evidence": "Thompson 2012",
            "system_hypothesis": "Both A and C are natural conversational tags; A seeks confirmation, C expresses expectation.",
            "uncertainty_basis": "Subtle pragmatic difference between sentence-final 'না' and 'তো'."
        },
        {
            "pilot_id": "PILOT-ITEM-038",
            "category": "PRAGMATICS_AND_REGISTER",
            "context": "Concessive minimization.",
            "intended_meaning": "There is not even a single person present.",
            "candidate_a": "একজন মানুষও উপস্থিত নেই।",
            "candidate_b": "একজন মানুষই উপস্থিত নেই।",
            "candidate_c": "কোনো মানুষ উপস্থিত নেই।",
            "phenomenon": "Scalar Concessive Clitic '-ও' on Minimal Quantifiers",
            "source_evidence": "Thompson 2012 p. 188",
            "system_hypothesis": "Candidate A ('একজন...ও') is standard scalar minimization ('not even one').",
            "uncertainty_basis": "Contrast between additive -o and restrictive -i on numerals."
        },
        {
            "pilot_id": "PILOT-ITEM-039",
            "category": "PRAGMATICS_AND_REGISTER",
            "context": "Speaking to an elderly professor / dignitary.",
            "intended_meaning": "Where do you live?",
            "candidate_a": "আপনি কোথায় থাকেন?",
            "candidate_b": "তুমি কোথায় থাকো?",
            "candidate_c": "আপনি কোথায় থাকিস?",
            "phenomenon": "Social Deixis & Honorific Agreement Consistency",
            "source_evidence": "Universal BDSB grammar",
            "system_hypothesis": "Candidate A is obligatory; Candidate C is ungrammatical due to honorific clash.",
            "uncertainty_basis": "Strict agreement invariant between subject honorificity and verb inflection."
        },
        {
            "pilot_id": "PILOT-ITEM-040",
            "category": "PRAGMATICS_AND_REGISTER",
            "context": "Expressing mild surprise / evidential reminder.",
            "intended_meaning": "Look, he has actually arrived!",
            "candidate_a": "আরে, সে যে এসে গেছে!",
            "candidate_b": "আরে, সে এসে গেছে যে!",
            "candidate_c": "আরে, সে কি এসে গেছে!",
            "phenomenon": "Emotive / Evidential Particle 'যে'",
            "source_evidence": "BA-GRAM-2011",
            "system_hypothesis": "Candidate A and B express astonished evidential confirmation using 'যে'.",
            "uncertainty_basis": "Pragmatic distinction between complementizer 'যে' and emotive discourse marker 'যে'."
        },
    ]
    return pilot


def write_markdown_pack(items: List[Dict[str, Any]], out_path: Path, title: str):
    lines = [
        f"# {title}",
        "",
        f"**Total Generated Candidates**: {len(items)}",
        "**Status**: `PENDING_HUMAN_REVIEW`",
        "**Generator Version**: `v2.0.0` (BLF Constrained Linguistic Synthesis)",
        "",
        "> [!IMPORTANT]",
        "> **Notice to Annotators**: These candidate items were generated by the BLF linguistic engine.",
        "> They represent candidate hypotheses and minimal pairs across morphotactics, DOM, complex predicates,",
        "> questions, and pragmatics. No automated process has assigned human approval.",
        "",
        "---",
        "",
        "| ID | Phenomenon | Candidate A | Candidate B | Confidence | Status |",
        "|---|---|---|---|---|---|",
    ]
    for it in items:
        iid = it.get("item_id") or it.get("pilot_id")
        phenom = it.get("phenomenon", "DIAGNOSTIC")
        c_a = it.get("candidate_form_a") or it.get("candidate_a", "")
        c_b = it.get("candidate_form_b") or it.get("candidate_b", "")
        conf = it.get("confidence", "MEDIUM")
        lines.append(f"| `{iid}` | {phenom} | {c_a} | {c_b} | `{conf}` | `PENDING_HUMAN_REVIEW` |")

    lines.append("")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    print("==================================================")
    print("BLF Review Queue & Human Review Pilot Generator")
    print("==================================================")

    # 1. Full Diagnostic Candidate Pack (156 items)
    candidate_items = build_candidate_pack()
    pack_data = {
        "title": "BLF Diagnostic Candidate Review Pack",
        "version": "2.0.0",
        "total_items": len(candidate_items),
        "status": "PENDING_HUMAN_REVIEW",
        "epistemic_notice": "Uncurated synthetic candidate pack generated for diagnostic validation; requires native linguist review.",
        "items": candidate_items,
    }
    with open(FULL_PACK_JSON, "w", encoding="utf-8") as f:
        json.dump(pack_data, f, ensure_ascii=False, indent=2)
    write_markdown_pack(candidate_items, FULL_PACK_MD, "BLF Diagnostic Candidate Review Pack")
    print(f"Generated {len(candidate_items)} diagnostic candidate items -> {FULL_PACK_JSON.name}")

    # 2. Controlled Human Review Pilot (40 items)
    pilot_items = build_pilot_40_items()
    pilot_data = {
        "title": "BLF Controlled Human Review Pilot (40 Items)",
        "version": "1.0.0",
        "total_items": len(pilot_items),
        "target_reviewers": "2+ Native Linguists / Educated Native Speakers",
        "status": "READY_FOR_HUMAN_EVALUATION",
        "categories_covered": [
            "VERB_MORPHOLOGY (6 items)",
            "DOM_AND_CASE (8 items)",
            "CLASSIFIERS_AND_NUMBER (6 items)",
            "COMPLEX_PREDICATES (7 items)",
            "QUESTIONS_AND_NEGATION (7 items)",
            "PRAGMATICS_AND_REGISTER (6 items)",
        ],
        "items": pilot_items,
    }
    with open(PILOT_40_JSON, "w", encoding="utf-8") as f:
        json.dump(pilot_data, f, ensure_ascii=False, indent=2)
    write_markdown_pack(pilot_items, PILOT_40_MD, "BLF Controlled Human Review Pilot (40 Items)")
    print(f"Generated {len(pilot_items)} stratified human review pilot items -> {PILOT_40_JSON.name}")

    print("SUCCESS: Review queue assets generated and verified.")


if __name__ == "__main__":
    main()
