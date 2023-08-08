from pathlib import Path
import shutil
import tempfile

import typer

from repo_mgmt import clone_git_repo_to_temp_dir
from utils import create_tarball, download_file, move_directory

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
        False, "--preserve-history", "-p", help="Preserve the full git history"
    ),
):
    temp_repo = clone_git_repo_to_temp_dir(src_dir, shallow=not preserve_history)
    print(f"Temp repo cloned to: '{temp_repo}'")

    output_dir = Path(tempfile.mkdtemp())

    # use shutil to move the temp_repo dir into output_dir/user_code
    user_code_dir = move_directory(temp_repo, output_dir / "user_code")

    # copy all files in gpt_tools to output_dir
    gpt_tools_dir = Path(__file__).parent / "gpt_tools"
    for file_path in gpt_tools_dir.glob("*"):
        shutil.copy(file_path, output_dir)

    # download the linux git binary, make it executable, and write it to
    # ./gpt_tools/git
    git_binary_url = "https://github.com/nikvdp/1bin/releases/download/v0.0.20/git"
    git_binary_dest_path = Path("gpt_tools/git")
    download_file(git_binary_url, git_binary_dest_path)

    # create a tarball of output_dir, and once it's written move it to the
    # current PWD, and tell the user about it
    tarball_path = Path(tempfile.mktemp(suffix=".tar.gz"))
    tarball = create_tarball(output_dir, tarball_path)
    destination = Path.cwd() / f"{src_dir.resolve().name}.tar.gz"
    shutil.move(str(tarball), str(destination))
    print(f"Tarball moved to '{destination}'")


@app.command()
def clone_repo():
    print("Cloning repo")


if __name__ == "__main__":
    app()
