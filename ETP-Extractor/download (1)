param(
    [Parameter(Mandatory=$true)]
    [string]$InputDirectory
)

$ErrorActionPreference = "Stop"
& .\.venv\Scripts\Activate.ps1

python -m etp_extractor.cli analyze-bundles `
    $InputDirectory `
    --output-file data/output/angular_analysis.json
