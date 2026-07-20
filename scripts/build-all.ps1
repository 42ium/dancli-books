param(
    [string]$DanWordsRoot = "..",
    [string]$Ecdict = ".\resources\ecdict.csv",
    [string]$Examples = ".\resources\examples.csv",
    [switch]$RequireExamples
)

$ErrorActionPreference = "Stop"

$presets = @(
    @{ Id = "cet4"; Title = "CET-4"; Tag = "cet4"; Level = "CET-4" },
    @{ Id = "cet6"; Title = "CET-6"; Tag = "cet6"; Level = "CET-6" },
    @{ Id = "gk"; Title = "Gaokao English"; Tag = "gk"; Level = "Gaokao" },
    @{ Id = "ielts"; Title = "IELTS"; Tag = "ielts"; Level = "IELTS" },
    @{ Id = "toefl"; Title = "TOEFL"; Tag = "toefl"; Level = "TOEFL" },
    @{ Id = "gre"; Title = "GRE"; Tag = "gre"; Level = "GRE" }
)

if (-not (Test-Path $Ecdict)) {
    throw "Missing ECDICT CSV: $Ecdict"
}

$builder = Join-Path $DanWordsRoot "tools\build_book.py"
if (-not (Test-Path $builder)) {
    throw "Missing DanWords builder: $builder"
}

New-Item -ItemType Directory -Force -Path ".\books" | Out-Null

foreach ($preset in $presets) {
    $args = @(
        $builder,
        "--ecdict", $Ecdict,
        "--ecdict-tag", $preset.Tag,
        "--id", $preset.Id,
        "--title", $preset.Title,
        "--level", $preset.Level,
        "--source-name", "ECDICT",
        "--license", "See NOTICE.md",
        "--out", ".\books\$($preset.Id).json"
    )

    if (Test-Path $Examples) {
        $args += @(
            "--examples", $Examples,
            "--example-source-name", "Tatoeba",
            "--example-license", "See NOTICE.md"
        )
    }

    if ($RequireExamples) {
        $args += "--require-examples"
    }

    python @args
}

