from pathlib import Path
import tempfile

from plumbum.cmd import git
import typer

from repo_mgmt import clone_git_repo_to_temp_dir, tar_directory

app = typer.Typer()

APP_NAME = "giterpreter"


def validate_directory(path: Path) -> Path:
    if not path.exists() or not path.is_dir():
        raise typer.BadParameter(f"'{path}' is not a valid directory.")
    if not (path / ".git").exists():
        raise typer.BadParameter(f"'{path}' does not contain a .git folder.")
    return path


@app.command()
def build(
    src_dir: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        callback=validate_directory,
        help=f"Build a {APP_NAME} zip file from a directory",
    ),
    preserve_history: bool = typer.Option(
        None, "--preserve-history", "-p", help="Preserve the full git history"
    ),
):
    if preserve_history is None:
        preserve_history = False
    temp_repo = clone_git_repo_to_temp_dir(src_dir, shallow=not preserve_history)
    print(f"Temp repo cloned to: '{temp_repo}'")

    tarball = tar_directory(temp_repo)
    print(f"Tarball written to '{tarball}'")


@app.command()
def clone_repo():
    print("Cloning repo")


if __name__ == "__main__":
    app()
