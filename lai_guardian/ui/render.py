from __future__ import annotations
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich import box
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from .theme import THEME

console = Console(theme=THEME)

def header():
    console.print(Panel.fit(
        Align.center("[bold white]LAI Guardian[/bold white]\n[cyan]Detector + Anonimizador + Auditoria (LGPD)[/cyan]"),
        box=box.HEAVY, style="header", padding=1
    ))

def kpis(precision: float, recall: float, f1: float, fn: int):
    t = Table(title="📊 [bold]INDICADORES DE DESEMPENHO (KPIs)[/bold]", box=box.ROUNDED)
    t.add_column("Métrica", style="cyan", no_wrap=True)
    t.add_column("Resultado", style="kpi", justify="right")
    t.add_column("Comentário", justify="center")

    def grade(val):
        if val >= 0.99: return "[success]EXCELENTE[/]"
        if val >= 0.90: return "[warning]SATISFATÓRIO[/]"
        return "[danger]CRÍTICO[/]"

    t.add_row("Precisão", f"{precision:.2%}", grade(precision))
    t.add_row("Recall (Segurança)", f"{recall:.2%}", grade(recall))
    t.add_row("F1-Score", f"{f1:.2%}", grade(f1))
    t.add_row("FN (Desempate)", str(fn), "[success]IDEAL=0[/]" if fn==0 else "[danger]ATENÇÃO[/]")
    console.print(t)

def confusion(vn:int, fp:int, fn:int, vp:int):
    t = Table(title="🧩 [bold]MATRIZ DE CONFUSÃO[/bold]", box=box.SIMPLE_HEAD)
    t.add_column("")
    t.add_column("Pred 0", justify="right")
    t.add_column("Pred 1", justify="right")
    t.add_row("True 0", f"VN={vn}", f"FP={fp}")
    t.add_row("True 1", f"FN={fn}", f"VP={vp}")
    console.print(t)

def spinner_progress(desc: str):
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40, complete_style="blue", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    )
