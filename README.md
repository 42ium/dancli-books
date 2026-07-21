# DanCLI Books

Prebuilt DanCLI word books.

This repository is intended to publish generated `books/*.json` files that can
be installed by DanCLI users without rebuilding from source datasets.

## Install A Book

Use a raw GitHub URL or a release asset URL:

```powershell
python -m dancli books download `
  --book-url https://raw.githubusercontent.com/42ium/dancli-books/main/books/cet4.json `
  --select
```

DanCLI presets use this repository by default:

```powershell
python -m dancli books download --preset cet4 --select
```

## Published Books

```text
cet4.json   3849 words, all with examples
cet6.json   5407 words, all with examples
gk.json     3677 words, all with examples
ielts.json  5040 words, all with examples
toefl.json  6974 words, all with examples
gre.json    7504 words, all with examples
```

Examples are selected from Tatoeba where possible. Remaining gaps are filled
with clearly marked `DanCLI fallback` examples so no word has an empty
`example` field.

## Repository Layout

```text
books/          Generated DanCLI JSON books
examples/       Small hand-written or curated example tables
resources/      Local-only downloaded source data, ignored by git
scripts/        Build helpers
NOTICE.md       Attribution and license notes
SOURCES.json    Machine-readable source metadata
```

## Build Locally

Put source files under `resources/`:

```text
resources/ecdict.csv
resources/examples.csv
```

Then run:

```powershell
.\scripts\build-all.ps1
```

Generated books are written to `books/`.

## Publication Policy

Generated books must keep source metadata. For ECDICT and Tatoeba-derived books,
each word should preserve the example source in `sources.example` when available.

Use `--require-examples` during generation when a book is expected to have an
example for every word.
