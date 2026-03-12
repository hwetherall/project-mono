"""
Terminal progress display using Rich.
"""
from rich.console import Console
from rich.table import Table


class ProgressTracker:
    """Displays real-time research progress in the terminal."""

    def __init__(self):
        self.console = Console()
        self.current_phase = ""
        self.category_statuses: dict[str, str] = {}

    def start_phase(self, phase_name: str, category_ids: list[str]):
        self.current_phase = phase_name
        for cid in category_ids:
            self.category_statuses[cid] = "pending"
        self.console.print(f"\n[bold blue]=== Phase: {phase_name} ===[/bold blue]")
        self.console.print(f"  Categories: {', '.join(category_ids)}")

    def start_category(self, category_id: str):
        self.category_statuses[category_id] = "running"
        self.console.print(f"  [yellow]> Starting {category_id}[/yellow]")

    def end_category(self, category_id: str, status: str, error: str | None = None,
                     source_count: int = 0, gap_count: int = 0):
        self.category_statuses[category_id] = status
        icon = "+" if status == "success" else "x" if status == "failed" else "~"
        color = "green" if status == "success" else "red" if status == "failed" else "yellow"
        suffix = f" ({error})" if error else ""
        self.console.print(f"  [{color}]{icon} {category_id}: {status}{suffix}[/{color}]")

    def end_phase(self, phase_name: str):
        self.console.print(f"[bold blue]=== Phase {phase_name} complete ===[/bold blue]")

    def log(self, message: str):
        self.console.print(f"  [dim]{message}[/dim]")

    def complete(self, total_seconds: float):
        mins = int(total_seconds // 60)
        secs = int(total_seconds % 60)
        self.console.print(f"\n[bold green]+ Research complete in {mins}m {secs}s[/bold green]")

        table = Table(title="Category Results")
        table.add_column("Category", style="cyan")
        table.add_column("Status")
        for cid, status in sorted(self.category_statuses.items()):
            color = "green" if status == "success" else "red" if status == "failed" else "yellow"
            table.add_row(cid, f"[{color}]{status}[/{color}]")
        self.console.print(table)
