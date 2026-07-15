from pathlib import Path
import typer
from rich.console import Console

from etp_extractor.angular_analyzer.analyzer import AngularAnalyzer

app = typer.Typer(help="ETP Extractor")
console = Console()


@app.command()
def analyze_bundles(
    input_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    electron_dir: Path | None = typer.Option(
        None,
        help="Carpeta extraída de app.asar para analizar IPC y almacenamiento del token.",
    ),
    output_file: Path = typer.Option(Path("data/output/angular_analysis.json")),
) -> None:
    """Analiza bundles Angular y, opcionalmente, el cliente Electron."""
    analyzer = AngularAnalyzer(input_dir, electron_dir)
    report = analyzer.analyze()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    console.print(f"[green]Informe generado:[/green] {output_file}")
    console.print(f"Rutas detectadas: {len(report.routes)}")
    console.print(
        "Interceptor token: "
        + ("[green]confirmado[/green]" if report.token_flow.interceptor_found else "[red]no encontrado[/red]")
    )


@app.command()
def status() -> None:
    """Muestra el estado del proyecto."""
    console.print("[bold]ETP Extractor v0.2.0[/bold]")
    console.print("Sprint 1: Angular Analyzer y flujo de sesión ETP.")


if __name__ == "__main__":
    app()
