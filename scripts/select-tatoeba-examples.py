from __future__ import annotations

import argparse
import bz2
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
URL_RE = re.compile(r"https?://|www\.", re.IGNORECASE)


@dataclass(frozen=True)
class Candidate:
    sentence_id: str
    term: str
    example: str
    author: str
    score: int


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    wanted = load_terms(args)
    if not wanted:
        print("No terms found. Check --ecdict-tag or --terms.", file=sys.stderr)
        return 1

    selected = select_examples(args.tatoeba, wanted, args.limit)
    write_examples(args.out, selected, args.source_name, args.license)
    missing = sorted(set(wanted) - set(selected))
    print(f"Wrote {len(selected)} examples to {args.out}")
    if missing:
        print(f"Missing examples for {len(missing)} terms.", file=sys.stderr)
        print("Preview: " + ", ".join(missing[:30]), file=sys.stderr)
    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select one Tatoeba example sentence per target term.")
    parser.add_argument("--tatoeba", type=Path, required=True, help="Tatoeba English TSV or TSV.BZ2 export.")
    parser.add_argument("--ecdict", type=Path, default=None, help="ECDICT CSV used to collect target terms.")
    parser.add_argument("--ecdict-tag", action="append", default=[], help="ECDICT tag to include, for example gre.")
    parser.add_argument("--terms", action="append", type=Path, default=[], help="Optional term list, one term per line.")
    parser.add_argument("--out", type=Path, required=True, help="Output examples CSV.")
    parser.add_argument("--limit", type=int, default=0, help="Stop after this many terms have examples; 0 means all.")
    parser.add_argument("--source-name", default="Tatoeba", help="Source name written to output.")
    parser.add_argument("--license", default="CC BY 2.0 FR", help="License written to output.")
    args = parser.parse_args(argv)
    if args.ecdict_tag and args.ecdict is None:
        parser.error("--ecdict is required with --ecdict-tag")
    if args.limit < 0:
        parser.error("--limit must be >= 0")
    return args


def load_terms(args: argparse.Namespace) -> dict[str, str]:
    terms: dict[str, str] = {}
    if args.ecdict and args.ecdict_tag:
        wanted_tags = {tag.casefold() for tag in args.ecdict_tag}
        with args.ecdict.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                term = first_value(row, "word", "term", "headword")
                if not term:
                    continue
                tags = {tag.casefold() for tag in split_tags(row.get("tag", ""))}
                if wanted_tags.intersection(tags):
                    keep_term(terms, term)
    for path in args.terms:
        with path.open("r", encoding="utf-8-sig") as fh:
            for raw in fh:
                term = raw.split("#", 1)[0].strip()
                if term:
                    keep_term(terms, term.split(",", 1)[0].strip())
    return terms


def keep_term(terms: dict[str, str], term: str) -> None:
    cleaned = clean_term(term)
    if cleaned:
        terms.setdefault(cleaned.casefold(), cleaned)


def clean_term(term: str) -> str:
    return re.sub(r"\s+", " ", str(term).strip())


def select_examples(path: Path, wanted: dict[str, str], limit: int) -> dict[str, Candidate]:
    selected: dict[str, Candidate] = {}
    opener = bz2.open if path.suffix.lower() == ".bz2" else open
    with opener(path, "rt", encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.reader(fh, delimiter="\t")
        for row in reader:
            parsed = parse_tatoeba_row(row)
            if parsed is None:
                continue
            sentence_id, text, author = parsed
            if not is_usable_sentence(text):
                continue
            for key in matching_terms(text, wanted):
                candidate = Candidate(
                    sentence_id=sentence_id,
                    term=wanted[key],
                    example=normalize_sentence(text),
                    author=author,
                    score=sentence_score(text, wanted[key]),
                )
                current = selected.get(key)
                if current is None or candidate.score > current.score:
                    selected[key] = candidate
            if limit and len(selected) >= limit:
                break
    return selected


def parse_tatoeba_row(row: Sequence[str]) -> tuple[str, str, str] | None:
    if len(row) < 2:
        return None
    sentence_id = row[0].strip()
    if len(row) >= 3 and row[1].strip().lower() == "eng":
        text = row[2].strip()
        author = row[3].strip() if len(row) >= 4 else ""
    else:
        text = row[1].strip()
        author = row[2].strip() if len(row) >= 3 else ""
    if not sentence_id or not text:
        return None
    return sentence_id, text, author


def is_usable_sentence(text: str) -> bool:
    stripped = text.strip()
    if URL_RE.search(stripped):
        return False
    if len(stripped) < 20 or len(stripped) > 140:
        return False
    words = WORD_RE.findall(stripped)
    if len(words) < 5 or len(words) > 18:
        return False
    letters = [char for char in stripped if char.isalpha()]
    if letters and sum(char.isupper() for char in letters) / len(letters) > 0.45:
        return False
    return True


def matching_terms(text: str, wanted: dict[str, str]) -> Iterable[str]:
    tokens = {token.strip("'").casefold() for token in WORD_RE.findall(text)}
    for token in tokens:
        if token in wanted:
            yield token


def sentence_score(text: str, term: str) -> int:
    words = WORD_RE.findall(text)
    count = len(words)
    score = 100
    score -= abs(count - 10) * 4
    score -= max(0, len(text) - 90)
    if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
        score += 25
    if text.endswith((".", "!", "?")):
        score += 5
    return score


def normalize_sentence(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def write_examples(path: Path, selected: dict[str, Candidate], source_name: str, license_name: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["term", "example", "sentence_id", "author", "source_name", "license"],
        )
        writer.writeheader()
        for candidate in sorted(selected.values(), key=lambda item: item.term.casefold()):
            writer.writerow(
                {
                    "term": candidate.term,
                    "example": candidate.example,
                    "sentence_id": candidate.sentence_id,
                    "author": candidate.author,
                    "source_name": source_name,
                    "license": license_name,
                }
            )


def first_value(mapping: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = mapping.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def split_tags(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[,;|/\s]+", str(value or "")) if part.strip()]


if __name__ == "__main__":
    raise SystemExit(main())

