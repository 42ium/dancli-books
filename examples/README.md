# Example Tables

Example tables can be CSV, TSV, or JSON.

Minimal CSV format:

```csv
term,example
abandon,They had to abandon the plan.
```

Recommended CSV format for Tatoeba-derived examples:

```csv
term,example,sentence_id,author,source_name,license
abandon,They had to abandon the plan.,12345,alice,Tatoeba,CC BY 2.0 FR
```

The build command can consume one or more files through `--examples`.

