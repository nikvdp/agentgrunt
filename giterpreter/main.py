import shutil
import tempfile
from pathlib import Path
from textwrap import dedent

import typer
from plumbum import local

from .repo_mgmt import clone_git_repo_to_temp_dir
from .utils import create_tarball, download_file, move_directory

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
    print(f"Preparing to build '{src_dir.resolve().name}'...")

    output_dir = Path(tempfile.mkdtemp())
    gpt_tools_dir = Path(__file__).parent.parent / "gpt_tools"

    # use shutil to move the temp_repo dir into output_dir/user_code
    user_code_dir = output_dir / "user_code"
    move_directory(temp_repo, user_code_dir)

    # download the linux git binary, make it executable, and write it to
    # ../gpt_tools/git for later use
    git_binary_url = "https://github.com/nikvdp/1bin/releases/download/v0.0.20/git"
    git_binary_dest_path = gpt_tools_dir / "git"
    if not git_binary_dest_path.exists():
        download_file(git_binary_url, git_binary_dest_path)
        git_binary_dest_path.chmod(0o755)

    # copy all files in gpt_tools to output_dir
    shutil.copytree(gpt_tools_dir, output_dir / "gpt_tools")

    # create a tarball of output_dir, and once it's written move it to the
    # current PWD, and tell the user about it
    tarball_path = Path(tempfile.mktemp(suffix=".tar.gz"))
    tarball = create_tarball(output_dir, tarball_path)
    destination = Path.cwd() / f"{src_dir.resolve().name}.tar.gz"
    shutil.move(str(tarball), str(destination))

    final_msg = dedent(
        f"""
        Wrote archive to: {destination}

        Please upload this file to ChatGPT, and paste the following message into the chat:

        """
    )

    gpt_prompt = dedent(
        """
        Please extract the archive I've uploaded, read the contents of README_ai.md, and 
        follow the directions listed inside that file.
    """
    )

    print(final_msg)
    print("---", "\n", gpt_prompt, "---")

    if shutil.which("pbcopy"):
        # prompt user if they want to copy it and reveal the file, then do it if they say yes
        copy = typer.confirm("Copy the message to your clipboard?")
        if copy:
            pbcopy = local["pbcopy"]
            echo = local["echo"]
            (echo[gpt_prompt] | pbcopy)()
        if typer.confirm("Reveal the file in Finder?"):
            local["open"]("-R", destination)


@app.command()
def clone_repo():
    print("Cloning repo")


if __name__ == "__main__":
    app()
