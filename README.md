# DanWords Books

Prebuilt DanWords word books.

This repository is intended to publish generated `books/*.json` files that can
be installed by DanWords users without rebuilding from source datasets.

## Install A Book

Use a raw GitHub URL or a release asset URL:

```powershell
python -m danwords books download `
  --book-url https://raw.githubusercontent.com/<owner>/danwords-books/main/books/cet4.json `
  --select
```

## Repository Layout

```text
books/          Generated DanWords JSON books
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

