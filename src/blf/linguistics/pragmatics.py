"""
BLF Conversational Register, Pragmatics & Social Deixis Engine.

Provides models and engines for:
1. Social deixis and 3-tier addressee honorificity (Apni, Tumi, Tui).
2. Pragmatic particle and clitic semantics (-i, -o, to, na, je, ba).
3. Orthographic/syntactic disambiguation between polar 'ki' and Wh-pronoun 'kee'.
4. Register transformations (Formal, Colloquial, Familiar, Intimate).
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from blf.linguistics.morphology.verbal_conjugator import VerbalConjugatorEngine
from blf.linguistics.normalizer import normalize_bangla_text

conjugator = VerbalConjugatorEngine()


class HonorificTier(str, Enum):
    HONORIFIC = "HONORIFIC"  # আপনি / তিনি (-en)
    FAMILIAR = "FAMILIAR"    # তুমি / সে (-o / -e)
    INTIMATE = "INTIMATE"    # তুই / সে (-is / -e)


class Register(str, Enum):
    FORMAL_STANDARD = "FORMAL_STANDARD"
    COLLOQUIAL_STANDARD = "COLLOQUIAL_STANDARD"
    FAMILIAR = "FAMILIAR"
    INTIMATE = "INTIMATE"


PRONOUN_MAP: Dict[str, Dict[HonorificTier, str]] = {
    "2": {
        HonorificTier.HONORIFIC: "আপনি",
        HonorificTier.FAMILIAR: "তুমি",
        HonorificTier.INTIMATE: "তুই",
    },
    "3": {
        HonorificTier.HONORIFIC: "তিনি",
        HonorificTier.FAMILIAR: "সে",
        HonorificTier.INTIMATE: "সে",
    },
}

VERB_SLOT_MAP: Dict[str, Dict[HonorificTier, str]] = {
    "2": {
        HonorificTier.HONORIFIC: "2_HON",
        HonorificTier.FAMILIAR: "2_ORD",
        HonorificTier.INTIMATE: "2_INT",
    },
    "3": {
        HonorificTier.HONORIFIC: "3_HON",
        HonorificTier.FAMILIAR: "3_ORD",
        HonorificTier.INTIMATE: "3_ORD",
    },
}


class PragmaticParticle:
    def __init__(self, particle: str, particle_type: str, semantic_function: str, is_clitic: bool):
        self.particle = particle
        self.particle_type = particle_type
        self.semantic_function = semantic_function
        self.is_clitic = is_clitic


PARTICLE_INVENTORY: Dict[str, PragmaticParticle] = {
    "ই": PragmaticParticle(
        particle="ই",
        particle_type="FOCUS_CLITIC_RESTRICTIVE",
        semantic_function="Exclusive/restrictive identification (X alone / precisely X).",
        is_clitic=True,
    ),
    "ও": PragmaticParticle(
        particle="ও",
        particle_type="FOCUS_CLITIC_ADDITIVE",
        semantic_function="Inclusive/additive focus (X also / even X).",
        is_clitic=True,
    ),
    "তো": PragmaticParticle(
        particle="তো",
        particle_type="DISCOURSE_PARTICLE_CONTRASTIVE",
        semantic_function="Contrastive topicalization, shared presupposition, or confirmation.",
        is_clitic=False,
    ),
    "না": PragmaticParticle(
        particle="না",
        particle_type="TAG_QUESTION_SOFTENING",
        semantic_function="Sentence-final tag question, confirmation request, or directive softening.",
        is_clitic=False,
    ),
    "যে": PragmaticParticle(
        particle="যে",
        particle_type="EMOTIVE_ASSERTION_PARTICLE",
        semantic_function="Emotive emphasis, unexpected assertion, or evidential reminder.",
        is_clitic=False,
    ),
    "বা": PragmaticParticle(
        particle="বা",
        particle_type="DUBITATIVE_ALTERNATIVE_PARTICLE",
        semantic_function="Dubitative counter-expectation or alternative suggestion.",
        is_clitic=False,
    ),
}


class PragmaticsEngine:
    """Pragmatic analysis, register transformation, and particle disambiguation."""

    def __init__(self):
        pass

    def disambiguate_ki(self, text: str) -> Dict[str, Any]:
        """
        Disambiguates whether 'কি' is used as a Polar Question Particle or Wh-Pronoun 'কী'.
        
        Rules:
        - Invariant pre-verbal 'কি' without case suffix -> POLAR_QUESTION_PARTICLE.
        - Declinable or argument-filling 'কী' (or 'কিসের', 'কিসে') -> INTERROGATIVE_PRONOUN.
        """
        norm = normalize_bangla_text(text)
        tokens = norm.split()
        
        results = []
        for idx, token in enumerate(tokens):
            if token in ["কিসের", "কিসে", "কীসে"]:
                results.append({
                    "token": token,
                    "type": "INTERROGATIVE_PRONOUN_SUBSTANTIVE",
                    "function": "Wh-argument filling nominal slot with overt case marking."
                })
            elif token == "কী":
                results.append({
                    "token": token,
                    "type": "INTERROGATIVE_PRONOUN_SUBSTANTIVE",
                    "function": "Direct object or predicate nominal Wh-pronoun ('what')."
                })
            elif token == "কি":
                # Check if immediately pre-verbal
                is_preverbal = (idx == len(tokens) - 2) or (idx == len(tokens) - 1)
                results.append({
                    "token": token,
                    "type": "POLAR_INTERROGATIVE_PARTICLE",
                    "function": "Yes/No truth-value question marker."
                })
        return {"text": text, "disambiguations": results}

    def transform_addressee_register(
        self,
        verb_root: str,
        tense_base: str,  # e.g. "PRES_SIMP", "PAST_SIMP", "FUT_SIMP", "IMP"
        target_tier: HonorificTier,
        include_subject: bool = True,
        object_np: Optional[str] = None,
    ) -> str:
        """
        Synthesizes an addressee-directed clause transformed into the specified Honorific Tier.
        """
        pronoun = PRONOUN_MAP["2"][target_tier]
        slot = VERB_SLOT_MAP["2"][target_tier]
        
        key = f"{tense_base}.{slot}"
        conj_table = conjugator.conjugate_root(verb_root)
        verb_form = conj_table.get(key, verb_root)

        elements = []
        if include_subject:
            elements.append(pronoun)
        if object_np:
            elements.append(object_np)
        elements.append(verb_form)

        return " ".join(elements)

    def attach_focus_clitic(self, word: str, clitic: str) -> str:
        """
        Attaches restrictive (-i) or additive (-o) focus clitic conforming to Bangla orthography.
        """
        norm = normalize_bangla_text(word)
        c = normalize_bangla_text(clitic)
        
        if c == "ই":
            # If word ends in vowel sign, attaches independent 'ই'
            return norm + "ই"
        elif c == "ও":
            return norm + "ও"
        return norm + c
