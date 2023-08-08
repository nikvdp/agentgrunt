import typer
from pathlib import Path

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
    )
):
    print("Building from:", src_dir)


@app.command()
def clone_repo():
    print("Cloning repo")


if __name__ == "__main__":
    app()
