"""
Unit tests for BLF CoNLL-U Ingestion Adapter.
"""

from pathlib import Path
import tempfile
import unittest

from blf.ingestion.conllu import CoNLLUIngestionAdapter, CoNLLUParseError
from blf.ingestion.source_record import SourceArtifact


SAMPLE_CONLLU_FIXTURE = """# newdoc id = doc_sample_01
# sent_id = dev-s1
# text = তিনি বই পড়েন।
1\tতিনি\tতিনি\tPRON\t_\tCase=Nom|Person=3|Polite=Form\t3\tnsubj\t_\tSpaceAfter=No
2\tবই\tবই\tNOUN\t_\tCase=Nom|Number=Sing\t3\tobj\t_\t_
3\tপড়েন\tপড়া\tVERB\t_\tPerson=3|Tense=Pres\t0\troot\t_\tSpaceAfter=No
4\t।\t।\tPUNCT\t_\t_\t3\tpunct\t_\t_

# sent_id = dev-s2
# text = ছেলেটি ভাত খাচ্ছে।
1\tছেলেটি\tছেলে\tNOUN\t_\tCase=Nom|Definite=Def\t3\tnsubj\t_\t_
2\tভাত\tভাত\tNOUN\t_\tCase=Nom\t3\tobj\t_\t_
3\tখাচ্ছে\tখাওয়া\tVERB\t_\tAspect=Prog|Tense=Pres\t0\troot\t_\tSpaceAfter=No
4\t।\t।\tPUNCT\t_\t_\t3\tpunct\t_\t_
"""


class TestCoNLLUIngestionAdapter(unittest.TestCase):

    def setUp(self) -> None:
        self.adapter = CoNLLUIngestionAdapter()
        self.artifact = SourceArtifact(
            artifact_id="ART-UD-TEST-FIXTURE",
            source_id="UD-TEST-SOURCE",
            license_expression="CC-BY-SA-4.0",
        )

    def test_parse_conllu_text_structure(self) -> None:
        sentences = self.adapter.parse_conllu_text(SAMPLE_CONLLU_FIXTURE, artifact=self.artifact)
        self.assertEqual(len(sentences), 2)

        # Sentence 1 verification
        s1 = sentences[0]
        self.assertEqual(s1.sentence_id, "dev-s1")
        self.assertEqual(s1.document_id, "doc_sample_01")
        self.assertEqual(s1.raw_text, "তিনি বই পড়েন।")
        self.assertEqual(s1.token_count, 4)
        self.assertEqual(s1.source_artifact.artifact_id, "ART-UD-TEST-FIXTURE")

        # Token verification
        t1 = s1.tokens[0]
        self.assertEqual(t1.form, "তিনি")
        self.assertEqual(t1.lemma, "তিনি")
        self.assertEqual(t1.upos, "PRON")
        self.assertEqual(t1.head, 3)
        self.assertEqual(t1.deprel, "nsubj")
        self.assertEqual(t1.feats.get("Person"), "3")
        self.assertEqual(t1.feats.get("Polite"), "Form")

        t2 = s1.tokens[1]
        self.assertEqual(t2.form, "বই")
        self.assertEqual(t2.upos, "NOUN")
        self.assertEqual(t2.deprel, "obj")

        t3 = s1.tokens[2]
        self.assertEqual(t3.upos, "VERB")
        self.assertEqual(t3.head, 0)
        self.assertEqual(t3.deprel, "root")

    def test_reconstruct_text_when_missing(self) -> None:
        # Fixture without # text header
        text_without_header = """# sent_id = s_no_text
1\tআমি\tআমি\tPRON\t_\t_\t2\tnsubj\t_\t_
2\tযাব\tযাওয়া\tVERB\t_\t_\t0\troot\t_\t_
"""
        sents = self.adapter.parse_conllu_text(text_without_header)
        self.assertEqual(len(sents), 1)
        self.assertEqual(sents[0].raw_text, "আমি যাব")

    def test_multiword_token_handling(self) -> None:
        mwt_text = """# sent_id = s_mwt
1-2\tdont\t_\t_\t_\t_\t_\t_\t_\t_
1\tdo\tdo\tVERB\t_\t_\t0\troot\t_\t_
2\tnot\tnot\tPART\t_\t_\t1\tadvmod\t_\t_
"""
        sents = self.adapter.parse_conllu_text(mwt_text)
        self.assertEqual(len(sents), 1)
        tokens = sents[0].tokens
        self.assertEqual(len(tokens), 3)
        self.assertTrue(tokens[0].is_multiword)
        self.assertEqual(tokens[0].multiword_range, (1, 2))
        self.assertFalse(tokens[1].is_multiword)
        self.assertEqual(sents[0].token_count, 2)  # Non-MWT tokens

    def test_malformed_token_line_raises_error(self) -> None:
        malformed = """# sent_id = bad_01
1\tশুধু\tদুই\tকলাম
"""
        with self.assertRaises(CoNLLUParseError):
            self.adapter.parse_conllu_text(malformed)

    def test_round_trip_serialization(self) -> None:
        sents = self.adapter.parse_conllu_text(SAMPLE_CONLLU_FIXTURE)
        serialized = self.adapter.to_conllu_text(sents)
        reparsed = self.adapter.parse_conllu_text(serialized)
        self.assertEqual(len(reparsed), len(sents))
        self.assertEqual(reparsed[0].sentence_id, sents[0].sentence_id)
        self.assertEqual(reparsed[0].token_count, sents[0].token_count)
        self.assertEqual(reparsed[0].tokens[0].form, sents[0].tokens[0].form)

    def test_file_parsing_and_document_grouping(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.conllu"
            file_path.write_text(SAMPLE_CONLLU_FIXTURE, encoding="utf-8")

            # Check sha256
            sha = self.adapter.calculate_file_sha256(file_path)
            self.assertEqual(len(sha), 64)

            # Test parse_conllu_file
            sents = self.adapter.parse_conllu_file(file_path)
            self.assertEqual(len(sents), 2)

            # Test document grouping
            docs = self.adapter.parse_documents_from_file(file_path)
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0].document_id, "doc_sample_01")
            self.assertEqual(docs[0].sentence_count, 2)
            self.assertEqual(docs[0].token_count, 8)


if __name__ == "__main__":
    unittest.main()
