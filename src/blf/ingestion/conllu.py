"""
BLF CoNLL-U Corpus Ingestion Adapter.

Implements a robust, provenance-preserving parser and serializer for the
CoNLL-U format (Universal Dependencies v2 specification).
Supports comments, metadata, multi-word tokens, and morphological features.
"""

from collections import defaultdict
import hashlib
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from blf.ingestion.source_record import (
    IngestedDocument,
    IngestedSentence,
    IngestedToken,
    SourceArtifact,
)


class CoNLLUParseError(ValueError):
    """Raised when CoNLL-U formatted text violates syntax specifications."""
    pass


class CoNLLUIngestionAdapter:
    """
    Parses CoNLL-U treebanks into strongly-typed BLF IngestedSentence and IngestedDocument objects.
    """

    @staticmethod
    def calculate_file_sha256(file_path: Union[str, Path]) -> str:
        """Computes the SHA-256 hex digest of a corpus file."""
        p = Path(file_path)
        hasher = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def _parse_feats(feat_str: str) -> Dict[str, str]:
        if not feat_str or feat_str == "_":
            return {}
        feats = {}
        parts = feat_str.split("|")
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                feats[k.strip()] = v.strip()
            else:
                feats[part.strip()] = "True"
        return feats

    @staticmethod
    def _parse_misc(misc_str: str) -> Dict[str, str]:
        if not misc_str or misc_str == "_":
            return {}
        misc = {}
        parts = misc_str.split("|")
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                misc[k.strip()] = v.strip()
            else:
                misc[part.strip()] = "True"
        return misc

    def parse_conllu_text(
        self,
        text: str,
        artifact: Optional[SourceArtifact] = None,
    ) -> List[IngestedSentence]:
        """
        Parses CoNLL-U formatted text into a list of IngestedSentence objects.
        """
        if not text or not text.strip():
            return []

        sentences: List[IngestedSentence] = []
        current_comments: List[str] = []
        current_metadata: Dict[str, str] = {}
        current_tokens: List[IngestedToken] = []
        current_doc_id: Optional[str] = None
        sent_index = 0

        lines = text.splitlines()

        for line_num, line in enumerate(lines, 1):
            line_str = line.strip()

            # Empty line indicates end of sentence block
            if not line_str:
                if current_tokens or current_metadata or current_comments:
                    sent_index += 1
                    sent_id = current_metadata.get("sent_id", f"sent_{sent_index}")
                    raw_text = current_metadata.get("text", "")

                    # Reconstruct raw text if not given in # text = ...
                    if not raw_text and current_tokens:
                        reconstructed = []
                        for tok in current_tokens:
                            if tok.is_multiword:
                                continue
                            reconstructed.append(tok.form)
                            space_after = tok.misc.get("SpaceAfter", "Yes")
                            if space_after != "No":
                                reconstructed.append(" ")
                        raw_text = "".join(reconstructed).strip()

                    sentence = IngestedSentence(
                        sentence_id=sent_id,
                        document_id=current_doc_id or current_metadata.get("doc_id") or current_metadata.get("newdoc id"),
                        raw_text=raw_text,
                        tokens=current_tokens,
                        comments=current_comments,
                        metadata=current_metadata,
                        source_artifact=artifact,
                    )
                    sentences.append(sentence)

                    current_comments = []
                    current_metadata = {}
                    current_tokens = []
                continue

            # Comment / Metadata line
            if line_str.startswith("#"):
                current_comments.append(line_str)
                comment_body = line_str[1:].strip()

                if " = " in comment_body:
                    key, val = comment_body.split(" = ", 1)
                    current_metadata[key.strip()] = val.strip()
                    if key.strip() in ("newdoc id", "doc_id"):
                        current_doc_id = val.strip()
                elif "=" in comment_body:
                    key, val = comment_body.split("=", 1)
                    current_metadata[key.strip()] = val.strip()
                    if key.strip() in ("newdoc id", "doc_id"):
                        current_doc_id = val.strip()
                continue

            # Token row
            cols = line.split("\t")
            if len(cols) != 10:
                # Some malformed files might use spaces; let's try tab split first
                if len(cols) == 1 and " " in line:
                    raise CoNLLUParseError(
                        f"Line {line_num} does not contain 10 tab-separated columns (found spaces instead of tabs): '{line}'"
                    )
                raise CoNLLUParseError(
                    f"Line {line_num} does not contain 10 tab-separated columns (got {len(cols)}): '{line}'"
                )

            id_str = cols[0].strip()
            form = cols[1].strip()
            lemma = cols[2].strip()
            upos = cols[3].strip()
            xpos = cols[4].strip() if cols[4].strip() != "_" else None
            feats = self._parse_feats(cols[5].strip())

            # Parse HEAD
            head_str = cols[6].strip()
            head: Optional[int] = None
            if head_str.isdigit():
                head = int(head_str)

            deprel = cols[7].strip() if cols[7].strip() != "_" else None
            deps = cols[8].strip() if cols[8].strip() != "_" else None
            misc = self._parse_misc(cols[9].strip())

            is_mwt = False
            mwt_range = None

            # Multi-word token (e.g. "1-2")
            if "-" in id_str:
                parts = id_str.split("-")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    is_mwt = True
                    mwt_range = (int(parts[0]), int(parts[1]))
                    token_id = int(parts[0])
                else:
                    token_id = 0
            elif "." in id_str:
                # Empty node (e.g. "1.1")
                token_id = int(id_str.split(".")[0])
            elif id_str.isdigit():
                token_id = int(id_str)
            else:
                token_id = 0

            token = IngestedToken(
                id=token_id,
                form=form,
                lemma=lemma,
                upos=upos,
                xpos=xpos,
                feats=feats,
                head=head,
                deprel=deprel,
                deps=deps,
                misc=misc,
                is_multiword=is_mwt,
                multiword_range=mwt_range,
            )
            current_tokens.append(token)

        # Handle any trailing sentence not followed by a newline
        if current_tokens or current_metadata or current_comments:
            sent_index += 1
            sent_id = current_metadata.get("sent_id", f"sent_{sent_index}")
            raw_text = current_metadata.get("text", "")

            if not raw_text and current_tokens:
                reconstructed = []
                for tok in current_tokens:
                    if tok.is_multiword:
                        continue
                    reconstructed.append(tok.form)
                    space_after = tok.misc.get("SpaceAfter", "Yes")
                    if space_after != "No":
                        reconstructed.append(" ")
                raw_text = "".join(reconstructed).strip()

            sentence = IngestedSentence(
                sentence_id=sent_id,
                document_id=current_doc_id or current_metadata.get("doc_id") or current_metadata.get("newdoc id"),
                raw_text=raw_text,
                tokens=current_tokens,
                comments=current_comments,
                metadata=current_metadata,
                source_artifact=artifact,
            )
            sentences.append(sentence)

        return sentences

    def parse_conllu_file(
        self,
        file_path: Union[str, Path],
        artifact: Optional[SourceArtifact] = None,
    ) -> List[IngestedSentence]:
        """
        Reads and parses a CoNLL-U file from disk.
        """
        p = Path(file_path)
        if not p.is_file():
            raise FileNotFoundError(f"CoNLL-U file not found: {file_path}")

        if artifact is None:
            sha = self.calculate_file_sha256(p)
            artifact = SourceArtifact(
                artifact_id=p.stem,
                source_id="UNKNOWN",
                file_path=str(p),
                file_sha256=sha,
            )

        with open(p, "r", encoding="utf-8") as f:
            text = f.read()

        return self.parse_conllu_text(text, artifact=artifact)

    def parse_documents_from_file(
        self,
        file_path: Union[str, Path],
        artifact: Optional[SourceArtifact] = None,
    ) -> List[IngestedDocument]:
        """
        Parses a CoNLL-U file and groups sentences into IngestedDocument instances.
        """
        sentences = self.parse_conllu_file(file_path, artifact=artifact)
        if not sentences:
            return []

        doc_groups: Dict[str, List[IngestedSentence]] = defaultdict(list)
        art_id = artifact.artifact_id if artifact else Path(file_path).stem
        src_id = artifact.source_id if artifact else "UNKNOWN"

        for s in sentences:
            doc_id = s.document_id or f"{art_id}_doc_default"
            doc_groups[doc_id].append(s)

        documents: List[IngestedDocument] = []
        for doc_id, sents in doc_groups.items():
            doc = IngestedDocument(
                document_id=doc_id,
                artifact_id=art_id,
                source_id=src_id,
                sentences=sents,
            )
            documents.append(doc)

        return documents

    def to_conllu_text(self, sentences: List[IngestedSentence]) -> str:
        """
        Serializes a list of IngestedSentence objects back into valid CoNLL-U format.
        """
        blocks = []
        for s in sentences:
            block_lines = []
            if s.comments:
                block_lines.extend(s.comments)
            else:
                block_lines.append(f"# sent_id = {s.sentence_id}")
                if s.raw_text:
                    block_lines.append(f"# text = {s.raw_text}")

            for t in s.tokens:
                if t.is_multiword and t.multiword_range:
                    id_col = f"{t.multiword_range[0]}-{t.multiword_range[1]}"
                else:
                    id_col = str(t.id)

                form_col = t.form or "_"
                lemma_col = t.lemma or "_"
                upos_col = t.upos or "_"
                xpos_col = t.xpos or "_"

                if t.feats:
                    feats_col = "|".join(f"{k}={v}" for k, v in sorted(t.feats.items()))
                else:
                    feats_col = "_"

                head_col = str(t.head) if t.head is not None else "_"
                deprel_col = t.deprel or "_"
                deps_col = t.deps or "_"

                if t.misc:
                    misc_col = "|".join(f"{k}={v}" if v != "True" else k for k, v in sorted(t.misc.items()))
                else:
                    misc_col = "_"

                row = f"{id_col}\t{form_col}\t{lemma_col}\t{upos_col}\t{xpos_col}\t{feats_col}\t{head_col}\t{deprel_col}\t{deps_col}\t{misc_col}"
                block_lines.append(row)

            blocks.append("\n".join(block_lines))

        return "\n\n".join(blocks) + "\n"
