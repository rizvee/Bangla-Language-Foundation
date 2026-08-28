"""
BLF Verbal Conjugation Engine.

Provides deterministic finite and non-finite verbal inflection matrices for BDSB,
incorporating tense, aspect, person, honorificity, stem mutations, irregular stems,
polarity-aware negation (-ni vs na), and strict conjunctive participle verification.
"""

from typing import Any, Dict, List, Optional
from blf.linguistics.normalizer import normalize_bangla_text


class ConjugationError(Exception):
    """Raised when an unmodeled or invalid verb root is requested."""
    pass


VERIFIED_CONJUNCTIVE_PARTICIPLES: Dict[str, str] = {
    "কর": "করে",
    "করা": "করে",
    "যা": "গিয়ে",
    "যাওয়া": "গিয়ে",
    "আসা": "এসে",
    "আস": "এসে",
    "দে": "দিয়ে",
    "দেওয়া": "দিয়ে",
    "দেয়া": "দিয়ে",
    "নে": "নিয়ে",
    "নেওয়া": "নিয়ে",
    "নেয়া": "নিয়ে",
    "খা": "খেয়ে",
    "খাওয়া": "খেয়ে",
    "হ": "হয়ে",
    "হওয়া": "হয়ে",
    "হয়া": "হয়ে",
    "দেখ": "দেখে",
    "দেখা": "দেখে",
    "বল": "বলে",
    "বলা": "বলে",
    "শোন": "শুনে",
    "শুন": "শুনে",
    "শোনা": "শুনে",
    "পড়": "পড়ে",
    "পড়া": "পড়ে",
    "লিখ": "লিখে",
    "লেখা": "লিখে",
    "কেন": "কিনে",
    "কিন": "কিনে",
    "কেনা": "কিনে",
    "কিনা": "কিনে",
    "পা": "পেয়ে",
    "পাওয়া": "পেয়ে",
    "পায়া": "পেয়ে",
    "ঘুমা": "ঘুমিয়ে",
    "ঘুমানো": "ঘুমিয়ে",
    "হাস": "হেসে",
    "হাসা": "হেসে",
    "কাদ": "কেঁদে",
    "কাঁদ": "কেঁদে",
    "কাঁদা": "কেঁদে",
    "জান": "জেনে",
    "জানা": "জেনে",
    "বোঝ": "বুঝে",
    "বোঝা": "বুঝে",
    "শেখ": "শিখে",
    "শেখা": "শিখে",
    "রাখ": "রেখে",
    "রাখা": "রেখে",
    "বস": "বসে",
    "বসা": "বসে",
    "উঠ": "উঠে",
    "উঠা": "উঠে",
    "ওঠা": "উঠে",
    "চল": "চলে",
    "চলা": "চলে",
    "পাঠা": "পাঠিয়ে",
    "পাঠানো": "পাঠিয়ে",
    "ফেল": "ফেলে",
    "ফেলা": "ফেলে",
    "ভাঙ": "ভেঙে",
    "ভাঙা": "ভেঙে",
    "ভাঙ্গ": "ভেঙে",
    "ভাঙ্গা": "ভেঙে",
    "শো": "শুয়ে",
    "শোয়া": "শুয়ে",
    "থাক": "থেকে",
    "থাকা": "থেকে",
}


class VerbalConjugatorEngine:
    """Deterministic verbal conjugator for Bangladesh Standard Bangla (Cholit BDSB)."""

    def __init__(self):
        pass

    def get_conjunctive_participle(self, verb: str) -> str:
        """
        Returns the non-finite conjunctive participle in -e for a verb root or lemma.
        Raises ConjugationError if the verb is unmodeled in the verified lexicon.
        """
        r = normalize_bangla_text(verb)
        if r in VERIFIED_CONJUNCTIVE_PARTICIPLES:
            return VERIFIED_CONJUNCTIVE_PARTICIPLES[r]
        raise ConjugationError(
            f"Unsupported verb for conjunctive participle: '{verb}'. "
            f"BLF requires explicit lexicon modeling to avoid corrupted fallbacks."
        )

    def conjugate_root(self, root: str) -> Dict[str, str]:
        """
        Generates the complete inflection matrix for a given verb root.
        
        Person slots:
        - 1: 1st person (Ami / Amra)
        - 2_ORD: 2nd person familiar (Tumi / Tomra)
        - 2_HON: 2nd person honorific (Apni / Aponara)
        - 2_INT: 2nd person intimate (Tui / Tora)
        - 3_ORD: 3rd person ordinary (Se / E / O)
        - 3_HON: 3rd person honorific (Tini / Ini / Uni)
        """
        r = normalize_bangla_text(root)

        # 1. Custom / Irregular Root Handling
        if r in ["কর", "kor", "করা"]:
            return self._conjugate_kor()
        elif r in ["যা", "ja", "যাওয়া"]:
            return self._conjugate_ja()
        elif r in ["খা", "kha", "খাওয়া"]:
            return self._conjugate_kha()
        elif r in ["দে", "de", "দেওয়া", "দেয়া"]:
            return self._conjugate_de()
        elif r in ["নে", "ne", "নেওয়া", "নেয়া"]:
            return self._conjugate_ne()
        elif r in ["হ", "ho", "হওয়া", "হয়া"]:
            return self._conjugate_ho()
        elif r in ["পা", "pa", "পাওয়া", "পায়া"]:
            return self._conjugate_pa()
        elif r in ["কেন", "ken", "কেনা", "কিন", "কিনা"]:
            return self._conjugate_regular_closed("কিন", "কেন")
        elif r in ["বল", "bol", "বলা"]:
            return self._conjugate_regular_closed("বল", "বল")
        elif r in ["লিখ", "likh", "লেখা"]:
            return self._conjugate_regular_closed("লিখ", "লেখ")
        elif r in ["দেখ", "dekh", "দেখা"]:
            return self._conjugate_regular_closed("দেখ", "দেখ")
        elif r in ["পড়", "por", "পড়া"]:
            return self._conjugate_regular_closed("পড়", "পড়")
        elif r in ["ফেল", "fel", "ফেলা"]:
            return self._conjugate_regular_closed("ফেল", "ফেল")
        elif r in ["উঠ", "uth", "উঠা", "ওঠা"]:
            return self._conjugate_regular_closed("উঠ", "উঠ")
        elif r in ["বস", "bosh", "বসা"]:
            return self._conjugate_regular_closed("বস", "বস")
        elif r in ["রাখ", "rakh", "রাখা"]:
            return self._conjugate_regular_closed("রাখ", "রাখ")
        elif r in ["থাক", "thak", "থাকা"]:
            return self._conjugate_regular_closed("থাক", "থাক")
        elif r in ["শোন", "shon", "শোনা", "শুন"]:
            return self._conjugate_regular_closed("শুন", "শোন")
        elif r in ["জান", "jan", "জানা"]:
            return self._conjugate_regular_closed("জান", "জান")
        elif r in ["বোঝ", "bojh", "বোঝা", "বুঝ"]:
            return self._conjugate_regular_closed("বুঝ", "বোঝ")
        elif r in ["শেখ", "shekh", "শেখা", "শিখ"]:
            return self._conjugate_regular_closed("শিখ", "শেখ")
        elif r in ["চল", "chol", "চলা"]:
            return self._conjugate_regular_closed("চল", "চল")
        else:
            return self._conjugate_regular_closed(r, r)

    def conjugate_negative(self, root: str, tense_person_key: str) -> str:
        """
        Generates the grammatically correct negative finite verb form in BDSB.
        
        Special Rules:
        - Present Perfect + Negative -> Past simple stem + '-নি'
          (e.g., করিনি, যায়নি, খায়নি, হয়নি, বলেনি, দেখেনি).
        - Other tenses -> Positive inflected form + ' না'
          (e.g., করি না, করছি না, করলাম না, করব না).
        """
        norm_root = normalize_bangla_text(root)
        table = self.conjugate_root(norm_root)

        if tense_person_key.startswith("PRES_PERF."):
            person = tense_person_key.split(".")[1]
            # Map present perfect negation to standard BDSB '-ni' forms
            if norm_root in ["কর", "করা"]:
                mapping = {"1": "করিনি", "2_ORD": "করোনি", "2_HON": "করেননি", "2_INT": "করিসনি", "3_ORD": "করেনি", "3_HON": "করেননি"}
                return mapping.get(person, "করেনি")
            elif norm_root in ["যা", "যাওয়া"]:
                mapping = {"1": "যাইনি", "2_ORD": "যাওনি", "2_HON": "যাননি", "2_INT": "যাসনি", "3_ORD": "যায়নি", "3_HON": "যাননি"}
                return mapping.get(person, "যায়নি")
            elif norm_root in ["খা", "খাওয়া"]:
                mapping = {"1": "খাইনি", "2_ORD": "খাওনি", "2_HON": "খাননি", "2_INT": "খাসনি", "3_ORD": "খায়নি", "3_HON": "খাননি"}
                return mapping.get(person, "খায়নি")
            elif norm_root in ["হ", "হওয়া", "হয়া"]:
                mapping = {"1": "হইনি", "2_ORD": "হওনি", "2_HON": "হননি", "2_INT": "হসনি", "3_ORD": "হয়নি", "3_HON": "হননি"}
                return mapping.get(person, "হয়নি")
            elif norm_root in ["দে", "দেওয়া", "দেয়া"]:
                mapping = {"1": "দেইনি", "2_ORD": "দাওনি", "2_HON": "দেননি", "2_INT": "দিসনি", "3_ORD": "দেয়নি", "3_HON": "দেননি"}
                return mapping.get(person, "দেয়নি")
            elif norm_root in ["নে", "নেওয়া", "নেয়া"]:
                mapping = {"1": "নেইনি", "2_ORD": "নাওনি", "2_HON": "নেননি", "2_INT": "নিসনি", "3_ORD": "নেয়নি", "3_HON": "নেননি"}
                return mapping.get(person, "নেয়নি")
            elif norm_root in ["লিখ", "লেখা"]:
                mapping = {"1": "লিখিনি", "2_ORD": "লেখোনি", "2_HON": "লেখেননি", "2_INT": "লিখিসনি", "3_ORD": "লেখেনি", "3_HON": "লেখেননি"}
                return mapping.get(person, "লেখেনি")
            elif norm_root in ["দেখ", "দেখা"]:
                mapping = {"1": "দেখিনি", "2_ORD": "দেখোনি", "2_HON": "দেখেননি", "2_INT": "দেখিসনি", "3_ORD": "দেখেনি", "3_HON": "দেখেননি"}
                return mapping.get(person, "দেখেনি")
            elif norm_root in ["বল", "বলা"]:
                mapping = {"1": "বলিনি", "2_ORD": "বলোনি", "2_HON": "বলেননি", "2_INT": "বলিসনি", "3_ORD": "বলেনি", "3_HON": "বলেননি"}
                return mapping.get(person, "বলেনি")
            elif norm_root in ["পড়", "পড়া"]:
                mapping = {"1": "পড়িনি", "2_ORD": "পড়োনি", "2_HON": "পড়েননি", "2_INT": "পড়িসনি", "3_ORD": "পড়েনি", "3_HON": "পড়েননি"}
                return mapping.get(person, "পড়েনি")
            elif norm_root in ["জান", "জানা"]:
                mapping = {"1": "জানিনি", "2_ORD": "জানোনি", "2_HON": "জানেননি", "2_INT": "জানিসনি", "3_ORD": "জানেনি", "3_HON": "জানেননি"}
                return mapping.get(person, "জানেনি")
            elif norm_root in ["বোঝ", "বোঝা", "বুঝ"]:
                mapping = {"1": "বুঝিনি", "2_ORD": "বোঝোনি", "2_HON": "বোঝেননি", "2_INT": "বুঝিসনি", "3_ORD": "বোঝেনি", "3_HON": "বোঝেননি"}
                return mapping.get(person, "বোঝেনি")
            elif norm_root in ["শেখ", "শেখা", "শিখ"]:
                mapping = {"1": "শিখিনি", "2_ORD": "শেখেনি", "2_HON": "শেখেননি", "2_INT": "শিখিসনি", "3_ORD": "শেখেনি", "3_HON": "শেখেননি"}
                return mapping.get(person, "শেখেনি")
            else:
                # Default regular root + e/i + ni
                return norm_root + "েনি"

        pos_form = table.get(tense_person_key, norm_root)
        return f"{pos_form} না"

    def _conjugate_ho(self) -> Dict[str, str]:
        """Dedicated conjugation paradigm for irregular/mutating verb root 'হ' (হওয়া)."""
        return {
            # Simple Present
            "PRES_SIMP.1": "হই",
            "PRES_SIMP.2_ORD": "হও",
            "PRES_SIMP.2_HON": "হন",
            "PRES_SIMP.2_INT": "হস",
            "PRES_SIMP.3_ORD": "হয়",
            "PRES_SIMP.3_HON": "হন",
            # Present Continuous
            "PRES_CONT.1": "হচ্ছি",
            "PRES_CONT.2_ORD": "হচ্ছো",
            "PRES_CONT.2_HON": "হচ্ছেন",
            "PRES_CONT.2_INT": "হচ্ছিস",
            "PRES_CONT.3_ORD": "হচ্ছে",
            "PRES_CONT.3_HON": "হচ্ছেন",
            # Present Perfect
            "PRES_PERF.1": "হয়েছি",
            "PRES_PERF.2_ORD": "হয়েছো",
            "PRES_PERF.2_HON": "হয়েছেন",
            "PRES_PERF.2_INT": "হয়েছিস",
            "PRES_PERF.3_ORD": "হয়েছে",
            "PRES_PERF.3_HON": "হয়েছেন",
            # Simple Past
            "PAST_SIMP.1": "হলাম",
            "PAST_SIMP.2_ORD": "হলে",
            "PAST_SIMP.2_HON": "হলেন",
            "PAST_SIMP.2_INT": "হলি",
            "PAST_SIMP.3_ORD": "হলো",  # standard colloquial BDSB
            "PAST_SIMP.3_HON": "হলেন",
            # Past Continuous
            "PAST_CONT.1": "হচ্ছিলাম",
            "PAST_CONT.2_ORD": "হচ্ছিলে",
            "PAST_CONT.2_HON": "হচ্ছিলেন",
            "PAST_CONT.2_INT": "হচ্ছিলি",
            "PAST_CONT.3_ORD": "হচ্ছিল",
            "PAST_CONT.3_HON": "হচ্ছিলেন",
            # Past Perfect
            "PAST_PERF.1": "হয়েছিলাম",
            "PAST_PERF.2_ORD": "হয়েছিলে",
            "PAST_PERF.2_HON": "হয়েছিলেন",
            "PAST_PERF.2_INT": "হয়েছিলি",
            "PAST_PERF.3_ORD": "হয়েছিল",
            "PAST_PERF.3_HON": "হয়েছিলেন",
            # Past Habitual
            "PAST_HAB.1": "হতাম",
            "PAST_HAB.2_ORD": "হতে",
            "PAST_HAB.2_HON": "হতেন",
            "PAST_HAB.2_INT": "হতিস",
            "PAST_HAB.3_ORD": "হত",
            "PAST_HAB.3_HON": "হতেন",
            # Simple Future
            "FUT_SIMP.1": "হব",
            "FUT_SIMP.2_ORD": "হবে",
            "FUT_SIMP.2_HON": "হবেন",
            "FUT_SIMP.2_INT": "হবি",
            "FUT_SIMP.3_ORD": "হবে",
            "FUT_SIMP.3_HON": "হবেন",
            # Imperative
            "IMP.2_HON": "হন",
            "IMP.2_ORD": "হও",
            "IMP.2_INT": "হ",
            # Non-finite
            "NF_CONJUNCTIVE": "হয়ে",
            "NF_CONDITIONAL": "হলে",
            "NF_INFINITIVE": "হতে",
        }

    def _conjugate_pa(self) -> Dict[str, str]:
        """Conjugation paradigm for open vowel root 'পা' (পাওয়া)."""
        return {
            # Simple Present
            "PRES_SIMP.1": "পাই",
            "PRES_SIMP.2_ORD": "পাও",
            "PRES_SIMP.2_HON": "পান",
            "PRES_SIMP.2_INT": "পাস",
            "PRES_SIMP.3_ORD": "পায়",
            "PRES_SIMP.3_HON": "পান",
            # Present Continuous
            "PRES_CONT.1": "পাচ্ছি",
            "PRES_CONT.2_ORD": "পাচ্ছ",
            "PRES_CONT.2_HON": "পাচ্ছেন",
            "PRES_CONT.2_INT": "পাচ্ছিস",
            "PRES_CONT.3_ORD": "পাচ্ছে",
            "PRES_CONT.3_HON": "পাচ্ছেন",
            # Present Perfect
            "PRES_PERF.1": "পেয়েছি",
            "PRES_PERF.2_ORD": "পেয়েছ",
            "PRES_PERF.2_HON": "পেয়েছেন",
            "PRES_PERF.2_INT": "পেয়েছিস",
            "PRES_PERF.3_ORD": "পেয়েছে",
            "PRES_PERF.3_HON": "পেয়েছেন",
            # Simple Past
            "PAST_SIMP.1": "পেলাম",
            "PAST_SIMP.2_ORD": "পেলে",
            "PAST_SIMP.2_HON": "পেলেন",
            "PAST_SIMP.2_INT": "পেলি",
            "PAST_SIMP.3_ORD": "পেল",
            "PAST_SIMP.3_HON": "পেলেন",
            # Past Continuous
            "PAST_CONT.1": "পাচ্ছিলাম",
            "PAST_CONT.2_ORD": "পাচ্ছিলে",
            "PAST_CONT.2_HON": "পাচ্ছিলেন",
            "PAST_CONT.2_INT": "পাচ্ছিলি",
            "PAST_CONT.3_ORD": "পাচ্ছিল",
            "PAST_CONT.3_HON": "পাচ্ছিলেন",
            # Past Perfect
            "PAST_PERF.1": "পেয়েছিলাম",
            "PAST_PERF.2_ORD": "পেয়েছিলে",
            "PAST_PERF.2_HON": "পেয়েছিলেন",
            "PAST_PERF.2_INT": "পেয়েছিলি",
            "PAST_PERF.3_ORD": "পেয়েছিল",
            "PAST_PERF.3_HON": "পেয়েছিলেন",
            # Past Habitual
            "PAST_HAB.1": "পেতাম",
            "PAST_HAB.2_ORD": "পেতে",
            "PAST_HAB.2_HON": "পেতেন",
            "PAST_HAB.2_INT": "পেতিস",
            "PAST_HAB.3_ORD": "পেত",
            "PAST_HAB.3_HON": "পেতেন",
            # Simple Future
            "FUT_SIMP.1": "পাব",
            "FUT_SIMP.2_ORD": "পাবে",
            "FUT_SIMP.2_HON": "পাবেন",
            "FUT_SIMP.2_INT": "পাবি",
            "FUT_SIMP.3_ORD": "পাবে",
            "FUT_SIMP.3_HON": "পাবেন",
            # Imperative
            "IMP.2_HON": "পান",
            "IMP.2_ORD": "পাও",
            "IMP.2_INT": "পা",
            # Non-finite
            "NF_CONJUNCTIVE": "পেয়ে",
            "NF_CONDITIONAL": "পেলে",
            "NF_INFINITIVE": "পেতে",
        }

    def _conjugate_kor(self) -> Dict[str, str]:
        return {
            # Simple Present
            "PRES_SIMP.1": "করি",
            "PRES_SIMP.2_ORD": "করো",
            "PRES_SIMP.2_HON": "করেন",
            "PRES_SIMP.2_INT": "করিস",
            "PRES_SIMP.3_ORD": "করে",
            "PRES_SIMP.3_HON": "করেন",
            # Present Continuous
            "PRES_CONT.1": "করছি",
            "PRES_CONT.2_ORD": "করছো",
            "PRES_CONT.2_HON": "করছেন",
            "PRES_CONT.2_INT": "করছিস",
            "PRES_CONT.3_ORD": "করছে",
            "PRES_CONT.3_HON": "করছেন",
            # Present Perfect
            "PRES_PERF.1": "করেছি",
            "PRES_PERF.2_ORD": "করেছো",
            "PRES_PERF.2_HON": "করেছেন",
            "PRES_PERF.2_INT": "করেছিস",
            "PRES_PERF.3_ORD": "করেছে",
            "PRES_PERF.3_HON": "করেছেন",
            # Simple Past
            "PAST_SIMP.1": "করলাম",
            "PAST_SIMP.2_ORD": "করলে",
            "PAST_SIMP.2_HON": "করলেন",
            "PAST_SIMP.2_INT": "করলি",
            "PAST_SIMP.3_ORD": "করল",
            "PAST_SIMP.3_HON": "করলেন",
            # Past Continuous
            "PAST_CONT.1": "করছিলাম",
            "PAST_CONT.2_ORD": "করছিলে",
            "PAST_CONT.2_HON": "করছিলেন",
            "PAST_CONT.2_INT": "করছিলি",
            "PAST_CONT.3_ORD": "করছিল",
            "PAST_CONT.3_HON": "করছিলেন",
            # Past Perfect
            "PAST_PERF.1": "করেছিলাম",
            "PAST_PERF.2_ORD": "করেছিলে",
            "PAST_PERF.2_HON": "করেছিলেন",
            "PAST_PERF.2_INT": "করেছিলি",
            "PAST_PERF.3_ORD": "করেছিল",
            "PAST_PERF.3_HON": "করেছিলেন",
            # Past Habitual
            "PAST_HAB.1": "করতাম",
            "PAST_HAB.2_ORD": "করতে",
            "PAST_HAB.2_HON": "করতেন",
            "PAST_HAB.2_INT": "করতিস",
            "PAST_HAB.3_ORD": "করত",
            "PAST_HAB.3_HON": "করতেন",
            # Simple Future
            "FUT_SIMP.1": "করব",
            "FUT_SIMP.2_ORD": "করবে",
            "FUT_SIMP.2_HON": "করবেন",
            "FUT_SIMP.2_INT": "করবি",
            "FUT_SIMP.3_ORD": "করবে",
            "FUT_SIMP.3_HON": "করবেন",
            # Imperative
            "IMP.2_HON": "করুন",
            "IMP.2_ORD": "করো",
            "IMP.2_INT": "কর",
            # Non-finite
            "NF_CONJUNCTIVE": "করে",
            "NF_CONDITIONAL": "করলে",
            "NF_INFINITIVE": "করতে",
        }

    def _conjugate_ja(self) -> Dict[str, str]:
        return {
            # Simple Present
            "PRES_SIMP.1": "যাই",
            "PRES_SIMP.2_ORD": "যাও",
            "PRES_SIMP.2_HON": "যান",
            "PRES_SIMP.2_INT": "যাস",
            "PRES_SIMP.3_ORD": "যায়",
            "PRES_SIMP.3_HON": "যান",
            # Present Continuous
            "PRES_CONT.1": "যাচ্ছি",
            "PRES_CONT.2_ORD": "যাচ্ছো",
            "PRES_CONT.2_HON": "যাচ্ছেন",
            "PRES_CONT.2_INT": "যাচ্ছিস",
            "PRES_CONT.3_ORD": "যাচ্ছে",
            "PRES_CONT.3_HON": "যাচ্ছেন",
            # Present Perfect
            "PRES_PERF.1": "গেছি",
            "PRES_PERF.2_ORD": "গেছো",
            "PRES_PERF.2_HON": "গেছেন",
            "PRES_PERF.2_INT": "গেছিস",
            "PRES_PERF.3_ORD": "গেছে",
            "PRES_PERF.3_HON": "গেছেন",
            # Simple Past
            "PAST_SIMP.1": "গেলাম",
            "PAST_SIMP.2_ORD": "গেলে",
            "PAST_SIMP.2_HON": "গেলেন",
            "PAST_SIMP.2_INT": "গেলি",
            "PAST_SIMP.3_ORD": "গেল",
            "PAST_SIMP.3_HON": "গেলেন",
            # Past Continuous
            "PAST_CONT.1": "যাচ্ছিলাম",
            "PAST_CONT.2_ORD": "যাচ্ছিলে",
            "PAST_CONT.2_HON": "যাচ্ছিলেন",
            "PAST_CONT.2_INT": "যাচ্ছিলি",
            "PAST_CONT.3_ORD": "যাচ্ছিল",
            "PAST_CONT.3_HON": "যাচ্ছিলেন",
            # Past Perfect
            "PAST_PERF.1": "গিয়েছিলাম",
            "PAST_PERF.2_ORD": "গিয়েছিলে",
            "PAST_PERF.2_HON": "গিয়েছিলেন",
            "PAST_PERF.2_INT": "গিয়েছিলি",
            "PAST_PERF.3_ORD": "গিয়েছিল",
            "PAST_PERF.3_HON": "গিয়েছিলেন",
            # Past Habitual
            "PAST_HAB.1": "যেতাম",
            "PAST_HAB.2_ORD": "যেতে",
            "PAST_HAB.2_HON": "যেতেন",
            "PAST_HAB.2_INT": "যেতিস",
            "PAST_HAB.3_ORD": "যেত",
            "PAST_HAB.3_HON": "যেতেন",
            # Simple Future
            "FUT_SIMP.1": "যাব",
            "FUT_SIMP.2_ORD": "যাবে",
            "FUT_SIMP.2_HON": "যাবেন",
            "FUT_SIMP.2_INT": "যাবি",
            "FUT_SIMP.3_ORD": "যাবে",
            "FUT_SIMP.3_HON": "যাবেন",
            # Imperative
            "IMP.2_HON": "যান",
            "IMP.2_ORD": "যাও",
            "IMP.2_INT": "যা",
            # Non-finite
            "NF_CONJUNCTIVE": "গিয়ে",
            "NF_CONDITIONAL": "গেলে",
            "NF_INFINITIVE": "যেতে",
        }

    def _conjugate_kha(self) -> Dict[str, str]:
        return {
            # Simple Present
            "PRES_SIMP.1": "খাই",
            "PRES_SIMP.2_ORD": "খাও",
            "PRES_SIMP.2_HON": "খান",
            "PRES_SIMP.2_INT": "খাস",
            "PRES_SIMP.3_ORD": "খায়",
            "PRES_SIMP.3_HON": "খান",
            # Present Continuous
            "PRES_CONT.1": "খাচ্ছি",
            "PRES_CONT.2_ORD": "খাচ্ছো",
            "PRES_CONT.2_HON": "খাচ্ছেন",
            "PRES_CONT.2_INT": "খাচ্ছিস",
            "PRES_CONT.3_ORD": "খাচ্ছে",
            "PRES_CONT.3_HON": "খাচ্ছেন",
            # Present Perfect
            "PRES_PERF.1": "খেয়েছি",
            "PRES_PERF.2_ORD": "খেয়েছো",
            "PRES_PERF.2_HON": "খেয়েছেন",
            "PRES_PERF.2_INT": "খেয়েছিস",
            "PRES_PERF.3_ORD": "খেয়েছে",
            "PRES_PERF.3_HON": "খেয়েছেন",
            # Simple Past
            "PAST_SIMP.1": "খেলাম",
            "PAST_SIMP.2_ORD": "খেলে",
            "PAST_SIMP.2_HON": "খেলেন",
            "PAST_SIMP.2_INT": "খেলি",
            "PAST_SIMP.3_ORD": "খেল",
            "PAST_SIMP.3_HON": "খেলেন",
            # Past Continuous
            "PAST_CONT.1": "খাচ্ছিলাম",
            "PAST_CONT.2_ORD": "খাচ্ছিলে",
            "PAST_CONT.2_HON": "খাচ্ছিলেন",
            "PAST_CONT.2_INT": "খাচ্ছিলি",
            "PAST_CONT.3_ORD": "খাচ্ছিল",
            "PAST_CONT.3_HON": "খাচ্ছিলেন",
            # Past Perfect
            "PAST_PERF.1": "খেয়েছিলাম",
            "PAST_PERF.2_ORD": "খেয়েছিলে",
            "PAST_PERF.2_HON": "খেয়েছিলেন",
            "PAST_PERF.2_INT": "খেয়েছিলি",
            "PAST_PERF.3_ORD": "খেয়েছিল",
            "PAST_PERF.3_HON": "খেয়েছিলেন",
            # Past Habitual
            "PAST_HAB.1": "খেতাম",
            "PAST_HAB.2_ORD": "খেতে",
            "PAST_HAB.2_HON": "খেতেন",
            "PAST_HAB.2_INT": "খেতিস",
            "PAST_HAB.3_ORD": "খেত",
            "PAST_HAB.3_HON": "খেতেন",
            # Simple Future
            "FUT_SIMP.1": "খাব",
            "FUT_SIMP.2_ORD": "খাবে",
            "FUT_SIMP.2_HON": "খাবেন",
            "FUT_SIMP.2_INT": "খাবি",
            "FUT_SIMP.3_ORD": "খাবে",
            "FUT_SIMP.3_HON": "খাবেন",
            # Imperative
            "IMP.2_HON": "খান",
            "IMP.2_ORD": "খাও",
            "IMP.2_INT": "খা",
            # Non-finite
            "NF_CONJUNCTIVE": "খেয়ে",
            "NF_CONDITIONAL": "খেলে",
            "NF_INFINITIVE": "খেতে",
        }

    def _conjugate_de(self) -> Dict[str, str]:
        return {
            # Simple Present
            "PRES_SIMP.1": "দিই",
            "PRES_SIMP.2_ORD": "দাও",
            "PRES_SIMP.2_HON": "দেন",
            "PRES_SIMP.2_INT": "দিস",
            "PRES_SIMP.3_ORD": "দেয়",
            "PRES_SIMP.3_HON": "দেন",
            # Present Continuous
            "PRES_CONT.1": "দিচ্ছি",
            "PRES_CONT.2_ORD": "দিচ্ছো",
            "PRES_CONT.2_HON": "দিচ্ছেন",
            "PRES_CONT.2_INT": "দিচ্ছিস",
            "PRES_CONT.3_ORD": "দিচ্ছে",
            "PRES_CONT.3_HON": "দিচ্ছেন",
            # Present Perfect
            "PRES_PERF.1": "দিয়েছি",
            "PRES_PERF.2_ORD": "দিয়েছো",
            "PRES_PERF.2_HON": "দিয়েছেন",
            "PRES_PERF.2_INT": "দিয়েছিস",
            "PRES_PERF.3_ORD": "দিয়েছে",
            "PRES_PERF.3_HON": "দিয়েছেন",
            # Simple Past
            "PAST_SIMP.1": "দিলাম",
            "PAST_SIMP.2_ORD": "দিলে",
            "PAST_SIMP.2_HON": "দিলেন",
            "PAST_SIMP.2_INT": "দিলি",
            "PAST_SIMP.3_ORD": "দিল",
            "PAST_SIMP.3_HON": "দিলেন",
            # Past Continuous
            "PAST_CONT.1": "দিচ্ছিলাম",
            "PAST_CONT.2_ORD": "দিচ্ছিলে",
            "PAST_CONT.2_HON": "দিচ্ছিলেন",
            "PAST_CONT.2_INT": "দিচ্ছিলি",
            "PAST_CONT.3_ORD": "দিচ্ছিল",
            "PAST_CONT.3_HON": "দিচ্ছিলেন",
            # Past Perfect
            "PAST_PERF.1": "দিয়েছিলাম",
            "PAST_PERF.2_ORD": "দিয়েছিলে",
            "PAST_PERF.2_HON": "দিয়েছিলেন",
            "PAST_PERF.2_INT": "দিয়েছিলি",
            "PAST_PERF.3_ORD": "দিয়েছিল",
            "PAST_PERF.3_HON": "দিয়েছিলেন",
            # Past Habitual
            "PAST_HAB.1": "দিতাম",
            "PAST_HAB.2_ORD": "দিতে",
            "PAST_HAB.2_HON": "দিতেন",
            "PAST_HAB.2_INT": "দিতি",
            "PAST_HAB.3_ORD": "দিত",
            "PAST_HAB.3_HON": "দিতেন",
            # Simple Future
            "FUT_SIMP.1": "দেব",
            "FUT_SIMP.2_ORD": "দেবে",
            "FUT_SIMP.2_HON": "দেবেন",
            "FUT_SIMP.2_INT": "দিবি",
            "FUT_SIMP.3_ORD": "দেবে",
            "FUT_SIMP.3_HON": "দেবেন",
            # Imperative
            "IMP.2_HON": "দিন",
            "IMP.2_ORD": "দাও",
            "IMP.2_INT": "দে",
            # Non-finite
            "NF_CONJUNCTIVE": "দিয়ে",
            "NF_CONDITIONAL": "দিলে",
            "NF_INFINITIVE": "দিতে",
        }

    def _conjugate_ne(self) -> Dict[str, str]:
        return {
            # Simple Present
            "PRES_SIMP.1": "নিই",
            "PRES_SIMP.2_ORD": "নাও",
            "PRES_SIMP.2_HON": "নেন",
            "PRES_SIMP.2_INT": "নিস",
            "PRES_SIMP.3_ORD": "নেয়",
            "PRES_SIMP.3_HON": "নেন",
            # Present Continuous
            "PRES_CONT.1": "নিচ্ছি",
            "PRES_CONT.2_ORD": "নিচ্ছো",
            "PRES_CONT.2_HON": "নিচ্ছেন",
            "PRES_CONT.2_INT": "নিচ্ছিস",
            "PRES_CONT.3_ORD": "নিচ্ছে",
            "PRES_CONT.3_HON": "নিচ্ছেন",
            # Present Perfect
            "PRES_PERF.1": "নিয়েছি",
            "PRES_PERF.2_ORD": "নিয়েছো",
            "PRES_PERF.2_HON": "নিয়েছেন",
            "PRES_PERF.2_INT": "নিয়েছিস",
            "PRES_PERF.3_ORD": "নিয়েছে",
            "PRES_PERF.3_HON": "নিয়েছেন",
            # Simple Past
            "PAST_SIMP.1": "নিলাম",
            "PAST_SIMP.2_ORD": "নিলে",
            "PAST_SIMP.2_HON": "নিলেন",
            "PAST_SIMP.2_INT": "নিলি",
            "PAST_SIMP.3_ORD": "নিল",
            "PAST_SIMP.3_HON": "নিলেন",
            # Past Continuous
            "PAST_CONT.1": "নিচ্ছিলাম",
            "PAST_CONT.2_ORD": "নিচ্ছিলে",
            "PAST_CONT.2_HON": "নিচ্ছিলেন",
            "PAST_CONT.2_INT": "নিচ্ছিলি",
            "PAST_CONT.3_ORD": "নিচ্ছিল",
            "PAST_CONT.3_HON": "নিচ্ছিলেন",
            # Past Perfect
            "PAST_PERF.1": "নিয়েছিলাম",
            "PAST_PERF.2_ORD": "নিয়েছিলে",
            "PAST_PERF.2_HON": "নিয়েছিলেন",
            "PAST_PERF.2_INT": "নিয়েছিলি",
            "PAST_PERF.3_ORD": "নিয়েছিল",
            "PAST_PERF.3_HON": "নিয়েছিলেন",
            # Past Habitual
            "PAST_HAB.1": "নিতাম",
            "PAST_HAB.2_ORD": "নিতে",
            "PAST_HAB.2_HON": "নিতেন",
            "PAST_HAB.2_INT": "নিতি",
            "PAST_HAB.3_ORD": "নিত",
            "PAST_HAB.3_HON": "নিতেন",
            # Simple Future
            "FUT_SIMP.1": "নেব",
            "FUT_SIMP.2_ORD": "নেবে",
            "FUT_SIMP.2_HON": "নেবেন",
            "FUT_SIMP.2_INT": "নিবি",
            "FUT_SIMP.3_ORD": "নেবে",
            "FUT_SIMP.3_HON": "নেবেন",
            # Imperative
            "IMP.2_HON": "নিন",
            "IMP.2_ORD": "নাও",
            "IMP.2_INT": "নে",
            # Non-finite
            "NF_CONJUNCTIVE": "নিয়ে",
            "NF_CONDITIONAL": "নিলে",
            "NF_INFINITIVE": "নিতে",
        }

    def _conjugate_regular_closed(self, root: str, open_form: str) -> Dict[str, str]:
        r = root
        o = open_form
        return {
            # Simple Present
            "PRES_SIMP.1": r + "ি",
            "PRES_SIMP.2_ORD": o + "ো",
            "PRES_SIMP.2_HON": r + "েন",
            "PRES_SIMP.2_INT": r + "িস",
            "PRES_SIMP.3_ORD": o + "ে",
            "PRES_SIMP.3_HON": r + "েন",
            # Present Continuous
            "PRES_CONT.1": r + "ছি",
            "PRES_CONT.2_ORD": r + "ছো",
            "PRES_CONT.2_HON": r + "ছেন",
            "PRES_CONT.2_INT": r + "ছিস",
            "PRES_CONT.3_ORD": r + "ছে",
            "PRES_CONT.3_HON": r + "ছেন",
            # Present Perfect
            "PRES_PERF.1": o + "েছি",
            "PRES_PERF.2_ORD": o + "েছো",
            "PRES_PERF.2_HON": o + "েছেন",
            "PRES_PERF.2_INT": o + "েছিস",
            "PRES_PERF.3_ORD": o + "েছে",
            "PRES_PERF.3_HON": o + "েছেন",
            # Simple Past
            "PAST_SIMP.1": r + "লাম",
            "PAST_SIMP.2_ORD": r + "লে",
            "PAST_SIMP.2_HON": r + "লেন",
            "PAST_SIMP.2_INT": r + "লি",
            "PAST_SIMP.3_ORD": r + "ল",
            "PAST_SIMP.3_HON": r + "লেন",
            # Past Continuous
            "PAST_CONT.1": r + "ছিলাম",
            "PAST_CONT.2_ORD": r + "ছিলে",
            "PAST_CONT.2_HON": r + "ছিলেন",
            "PAST_CONT.2_INT": r + "ছিলি",
            "PAST_CONT.3_ORD": r + "ছিল",
            "PAST_CONT.3_HON": r + "ছিলেন",
            # Past Perfect
            "PAST_PERF.1": o + "েছিলাম",
            "PAST_PERF.2_ORD": o + "েছিলে",
            "PAST_PERF.2_HON": o + "েছিলেন",
            "PAST_PERF.2_INT": o + "েছিলি",
            "PAST_PERF.3_ORD": o + "েছিল",
            "PAST_PERF.3_HON": o + "েছিলেন",
            # Past Habitual
            "PAST_HAB.1": r + "তাম",
            "PAST_HAB.2_ORD": r + "তে",
            "PAST_HAB.2_HON": r + "তেন",
            "PAST_HAB.2_INT": r + "তিস",
            "PAST_HAB.3_ORD": r + "ত",
            "PAST_HAB.3_HON": r + "তেন",
            # Simple Future
            "FUT_SIMP.1": r + "ব",
            "FUT_SIMP.2_ORD": r + "বে",
            "FUT_SIMP.2_HON": r + "বেন",
            "FUT_SIMP.2_INT": r + "বি",
            "FUT_SIMP.3_ORD": r + "বে",
            "FUT_SIMP.3_HON": r + "বেন",
            # Imperative
            "IMP.2_HON": r + "ুন",
            "IMP.2_ORD": o + "ো",
            "IMP.2_INT": r,
            # Non-finite
            "NF_CONJUNCTIVE": o + "ে",
            "NF_CONDITIONAL": r + "লে",
            "NF_INFINITIVE": r + "তে",
        }
