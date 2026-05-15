#!/usr/bin/env python3
"""
Point d'entrée principal — Vinted Optimizer
Usage :
    # Mode scraping automatique
    python main.py --user TON_PSEUDO

    # Mode fichier JSON manuel
    python main.py --file input_vinted.json

    # Mode export RGPD (dossier décompressé)
    python main.py --export-folder ./vinted_data/

    # Mode export RGPD (ZIP direct)
    python main.py --export-zip ./vinted_export.zip
"""

import json
import sys
from pathlib import Path
from typing import Optional
import traceback

import typer
from rich.console import Console
from rich.progress import track
from rich.table import Table

from core.analyser import analyse_item
from core.models import ItemInput
from core.reporter import save_reports
from core.scraper import scrape_user_items
from core.html_parser import load_from_export_folder, load_from_zip

app = typer.Typer(help="Vinted Optimizer - Pipeline d'optimisation d'annonces")
console = Console(force_terminal=True)


@app.command()
def run(
    # ── Source de données (au choix) ──────────────────────────
    user: Optional[str] = typer.Option(None, "--user", "-u",
        help="Pseudo Vinted -> scraping automatique"),
    file: Optional[Path] = typer.Option(None, "--file", "-f",
        help="Fichier JSON d'articles en entrée"),
    export_folder: Optional[Path] = typer.Option(None, "--export-folder", "-e",
        help="Dossier décompressé de l'export RGPD Vinted"),
    export_zip: Optional[Path] = typer.Option(None, "--export-zip", "-z",
        help="Fichier ZIP de l'export RGPD Vinted"),

    # ── Options scraping ──────────────────────────────────────
    max_items: int = typer.Option(20, "--max", "-m", help="Nombre max d'articles"),
    delay: float = typer.Option(1.5, "--delay", "-d", help="Délai entre requêtes (secondes)"),
    country: str = typer.Option("fr", "--country", "-c", help="Pays Vinted (fr/be/es/de/it)"),

    # ── Sortie ────────────────────────────────────────────────
    output: Path = typer.Option(Path("output_vinted"), "--output", "-o",
        help="Dossier de sortie"),
) -> None:
    # ── Vérification qu'au moins une source est fournie ───────
    sources = [user, file, export_folder, export_zip]
    if not any(sources):
        console.print("[bold red][ERROR] Donne --user, --file, --export-folder ou --export-zip[/bold red]")
        raise typer.Exit(1)

    # ── Chargement selon la source ────────────────────────────
    items: list[ItemInput] = []

    try:
        if export_zip:
            console.print(f"[cyan][INFO] Mode export ZIP : {export_zip}[/cyan]")
            items = load_from_zip(export_zip)

        elif export_folder:
            console.print(f"[cyan][INFO] Mode export dossier : {export_folder}[/cyan]")
            items = load_from_export_folder(export_folder)

        elif file:
            console.print(f"[cyan][INFO] Mode fichier JSON : {file}[/cyan]")
            data = json.loads(file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data = [data]
            items = [ItemInput(**d) for d in data[:max_items]]
            console.print(f"[green][OK] {len(items)} article(s) charge(s).[/green]")

        elif user:
            console.print(f"[cyan][INFO] Mode scraping : {user}[/cyan]")
            items = scrape_user_items(user, country=country, max_items=max_items, delay=delay)
    except Exception as e:
        console.print(f"[bold red][ERROR] Erreur lors du chargement : {e}[/bold red]")
        if "--debug" in sys.argv:
            traceback.print_exc()
        raise typer.Exit(1)

    if not items:
        console.print("[yellow][WARN] Aucun article à analyser. Programme termine.[/yellow]")
        raise typer.Exit(0)

    # ── Analyse ───────────────────────────────────────────────
    pairs = []
    table = Table(title="Resultats analyse", show_lines=True)
    table.add_column("#",        style="dim", width=4)
    table.add_column("Titre",    max_width=38)
    table.add_column("Score",    justify="center", width=8)
    table.add_column("Potentiel")

    try:
        for idx, item in enumerate(track(items[:max_items], description="Analyse en cours..."), start=1):
            result = analyse_item(item)
            pairs.append((item, result))
            score = result.score_global["score_global"]
            table.add_row(str(idx), item.titre[:38], f"{score}/10", result.potentiel_vente)
    except Exception as e:
        console.print(f"[bold red][ERROR] Erreur lors de l'analyse : {e}[/bold red]")
        if "--debug" in sys.argv:
            traceback.print_exc()
        raise typer.Exit(1)

    console.print(table)

    # ── Sauvegarde ────────────────────────────────────────────
    try:
        json_path = save_reports(pairs, output)
        console.print(f"\n[bold green][SUCCESS] {len(pairs)} articles analyses ![/bold green]")
        console.print(f"[INFO] Rapports dans   : [cyan]{output.resolve()}[/cyan]")
        console.print(f"[INFO] JSON consolide : [cyan]{json_path}[/cyan]")
    except Exception as e:
        console.print(f"[bold red][ERROR] Erreur lors de la sauvegarde : {e}[/bold red]")
        if "--debug" in sys.argv:
            traceback.print_exc()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
