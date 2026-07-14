from pathlib import Path
import typer
from rich.console import Console

from etp_extractor.angular_analyzer.analyzer import AngularAnalyzer

app = typer.Typer(help="ETP Extractor")
console = Console()


@app.command()
def analyze_bundles(
    input_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    output_file: Path = typer.Option(Path("data/output/angular_analysis.json")),
) -> None:
    """Analiza bundles JavaScript del cliente Angular."""
    analyzer = AngularAnalyzer(input_dir)
    report = analyzer.analyze()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    console.print(f"[green]Informe generado:[/green] {output_file}")


@app.command()
def status() -> None:
    """Muestra el estado inicial del proyecto."""
    console.print("[bold]ETP Extractor v0.1.0[/bold]")
    console.print("Arquitectura inicial creada correctamente.")


if __name__ == "__main__":
    app()
