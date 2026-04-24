"""
Book command - Write entire books with auto-retry and progressive saving.

This command breaks down book writing into manageable chapters,
saves progress regularly, and automatically retries on failure.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.text import Text

from ...core.router import FreeRouter

console = Console()


class BookWriter:
    """Write a book chapter by chapter with auto-save and retry logic."""

    def __init__(
        self,
        title: str,
        num_chapters: int = 5,
        chapter_length: int = 2000,
        output_file: Optional[Path] = None,
        max_retries: int = 3,
    ):
        """
        Initialize book writer.

        Args:
            title: Book title
            num_chapters: Number of chapters to write
            chapter_length: Approximate tokens per chapter
            output_file: Output file path (default: <title>.md)
            max_retries: Max retries per chapter
        """
        self.title = title
        self.num_chapters = num_chapters
        self.chapter_length = chapter_length
        self.max_retries = max_retries

        if output_file is None:
            output_file = Path(f"{title.lower().replace(' ', '_')}.md")
        self.output_file = Path(output_file)

        self.router = FreeRouter(verbose=False)
        self.chapters = {}
        self.load_progress()

    def load_progress(self) -> None:
        """Load existing progress if file exists."""
        if self.output_file.exists():
            content = self.output_file.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Extract completed chapters from markdown
            for line in lines:
                if line.startswith("## Chapter "):
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            chapter_num = int(parts[2])
                            self.chapters[chapter_num] = True
                        except ValueError:
                            pass

    def save_chapter(self, chapter_num: int, content: str) -> None:
        """Save a single chapter to file."""
        self.chapters[chapter_num] = True

        if not self.output_file.exists():
            # Create new file with header
            header = f"# {self.title}\n\n"
            self.output_file.write_text(header, encoding="utf-8")

        # Append chapter
        full_content = self.output_file.read_text(encoding="utf-8")
        if f"## Chapter {chapter_num}" not in full_content:
            full_content += f"\n## Chapter {chapter_num}\n\n{content}\n"
            self.output_file.write_text(full_content, encoding="utf-8")

    def generate_chapter_prompt(
        self, chapter_num: int, previous_context: str = ""
    ) -> str:
        """Generate prompt for a chapter."""
        prompt = f"""Write Chapter {chapter_num} of a book titled "{self.title}".

Chapter {chapter_num} should be approximately {self.chapter_length} tokens.
Write engaging, well-structured content that flows naturally.
"""
        if previous_context:
            prompt += f"\nPrevious context:\n{previous_context}\n"

        prompt += "\nStart the chapter with '## Chapter {chapter_num}' and continue from there."
        return prompt

    def write_chapter(self, chapter_num: int) -> bool:
        """
        Write a single chapter with retry logic.

        Args:
            chapter_num: Chapter number to write

        Returns:
            True if successful, False if exhausted retries
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                # Get context from previous chapters
                previous_content = self.output_file.read_text(encoding="utf-8")
                previous_context = "\n".join(
                    previous_content.split("\n")[-500:]
                )  # Last 500 lines

                prompt = self.generate_chapter_prompt(chapter_num, previous_context)

                # Stream the chapter
                console.print(
                    f"\n[cyan]Writing Chapter {chapter_num}[/cyan] "
                    f"(Attempt {attempt}/{self.max_retries})"
                )

                chapter_content = ""
                with console.status(f"[bold green]Generating content...[/bold green]"):
                    for chunk in self.router.complete_stream(
                        prompt=prompt,
                        max_tokens=self.chapter_length + 500,
                    ):
                        chapter_content += chunk

                # Save chapter
                self.save_chapter(chapter_num, chapter_content)
                console.print(f"[green]✅ Chapter {chapter_num} saved[/green]")
                return True

            except Exception as e:
                console.print(
                    f"[yellow]⚠️ Chapter {chapter_num} failed (attempt {attempt}): {e}[/yellow]"
                )
                if attempt < self.max_retries:
                    console.print(f"[dim]Retrying...[/dim]")
                continue

        console.print(
            f"[red]❌ Chapter {chapter_num} failed after {self.max_retries} attempts[/red]"
        )
        return False

    def write_book(self) -> int:
        """
        Write the entire book.

        Returns:
            Number of successfully written chapters
        """
        console.print(
            Panel(
                f"📚 Writing book: [bold cyan]{self.title}[/bold cyan]\n"
                f"📖 Chapters: {self.num_chapters}\n"
                f"📝 Save to: [yellow]{self.output_file}[/yellow]",
                expand=False,
            )
        )

        success_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Writing chapters...", total=self.num_chapters)

            for chapter_num in range(1, self.num_chapters + 1):
                progress.update(
                    task, description=f"Chapter {chapter_num}/{self.num_chapters}"
                )

                if chapter_num in self.chapters:
                    console.print(
                        f"[dim]⏭️  Chapter {chapter_num} already written, skipping[/dim]"
                    )
                    success_count += 1
                elif self.write_chapter(chapter_num):
                    success_count += 1

                progress.advance(task)

        # Summary
        console.print("\n" + "=" * 60)
        console.print(f"[bold cyan]Book writing complete![/bold cyan]")
        console.print(
            f"[green]✅ {success_count}/{self.num_chapters} chapters written[/green]"
        )
        console.print(f"[yellow]📖 Book saved to: {self.output_file}[/yellow]")

        # Show stats
        status = self.router.status()
        session = status["session"]
        console.print(
            f"\n[dim]Stats: {session['requests']} requests, "
            f"{session['tokens']:,} tokens used, "
            f"{session['fallbacks']} provider fallbacks[/dim]"
        )
        console.print("=" * 60)

        return success_count


def book_command(
    title: str = typer.Argument(..., help="Book title"),
    chapters: int = typer.Option(
        5,
        "--chapters",
        "-c",
        help="Number of chapters to write",
        min=1,
        max=100,
    ),
    chapter_length: int = typer.Option(
        2000,
        "--chapter-length",
        "-l",
        help="Approximate tokens per chapter",
        min=500,
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output markdown file path",
    ),
):
    """
    Write an entire book chapter by chapter.

    Features:
    - Automatically writes multiple chapters
    - Saves progress after each chapter
    - Retries failed chapters automatically
    - Routes across providers as quota exhausts
    - Beautiful progress tracking

    Example:
        quotarouter book "The Art of Python" --chapters 5
        quotarouter book "AI Future" --chapters 10 --chapter-length 3000
        quotarouter book "Story" -c 3 -o my_story.md
    """
    try:
        writer = BookWriter(
            title=title,
            num_chapters=chapters,
            chapter_length=chapter_length,
            output_file=Path(output) if output else None,
            max_retries=3,
        )

        success_count = writer.write_book()

        # Exit with appropriate code
        if success_count == chapters:
            raise typer.Exit(code=0)
        elif success_count > 0:
            raise typer.Exit(code=0)  # Partial success is still success
        else:
            raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)
