import tempfile
import shutil
import tempfile
from pathlib import Path
from textwrap import dedent

import typer
from plumbum import local

from .repo_mgmt import clone_git_repo_to_temp_dir
from .utils import create_tarball, download_file, move_directory

app = typer.Typer()


def validate_directory(path: Path) -> Path:
    if not path.exists() or not path.is_dir():
        raise typer.BadParameter(f"'{path}' is not a valid directory.")
    if not (path / ".git").exists():
        raise typer.BadParameter(f"'{path}' does not contain a .git folder.")
    return path


@app.command()
def bundle(
    src_dir: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        callback=validate_directory,
        help=f"Build an AgentGrunt zip file from a directory",
    ),
    preserve_history: bool = typer.Option(
        False,
        "--preserve-history",
        "-p",
        help="Preserve the full git history (defaults to shallow clone to save space)",
    ),
    interactive: bool = typer.Option(
        True, "--no-interactive", "-b", help="don't ask questions (batch) mode"
    ),
    assume_yes: bool = typer.Option(
        False, "--assume-yes", "-y", help="assume yes for all prompts"
    ),
):
    temp_repo = clone_git_repo_to_temp_dir(src_dir, shallow=not preserve_history)
    print(  # "\033[92m" +
        f"Preparing to build '{src_dir.resolve().name}'..."
        # + "\033[0m"
    )

    output_dir = Path(tempfile.mkdtemp())
    output_dir.mkdir(parents=True, exist_ok=True)
    gpt_tools_dir = Path(__file__).parent / "gpt_tools"

    # use shutil to move the temp_repo dir into output_dir/user_code
    user_code_dir = output_dir / "uc"
    move_directory(temp_repo, user_code_dir)

    # copy all files in gpt_tools to output_dir
    shutil.copytree(gpt_tools_dir, output_dir / "tools_for_ai")

    # download the linux git binary, make it executable
    git_binary_url = "https://github.com/nikvdp/1bin/releases/download/v0.0.20/git"
    git_binary_dest_path = output_dir / "tools_for_ai" / "git"
    if not git_binary_dest_path.exists():
        download_file(git_binary_url, git_binary_dest_path)
        git_binary_dest_path.chmod(0o755)

    # create a tarball of output_dir, and once it's written move it to the
    # current PWD, and tell the user about it
    tarball_path = Path(tempfile.mktemp(suffix=".tar.gz"))
    tarball = create_tarball(output_dir, tarball_path)
    destination = Path.cwd() / f"{src_dir.resolve().name}.tar.gz"
    shutil.move(str(tarball), str(destination))

    final_msg = (
        dedent(
            f"""
            Wrote archive to: {destination}

            Please upload this file to ChatGPT, and paste the following message into the chat:
            """
        ).strip()
        + "\n"
    )

    gpt_prompt = (
        dedent(
            """
        Please extract the archive I've uploaded to /tmp, read the contents of
        tools_for_ai/README_ai.md, and follow the directions listed inside that
        file.
        """
        )
        .strip()
        .replace("\n", " ")
    )

    print(final_msg)
    print(f"---\n{gpt_prompt}\n---")

    if interactive and shutil.which("pbcopy"):
        # prompt user if they want to copy it and reveal the file, then do it if they say yes

        copy = (
            True if assume_yes else typer.confirm("Copy the message to your clipboard?")
        )
        if copy:
            pbcopy = local["pbcopy"]
            echo = local["echo"]
            (echo[gpt_prompt] | pbcopy)()
        open_finder = (
            True if assume_yes else typer.confirm("Reveal the file in Finder?")
        )
        if open_finder:
            local["open"]("-R", destination)


@app.command()
def apply_remote_changes(
    patch_file: Path = typer.Argument(
        ..., exists=True, readable=True, dir_okay=False, resolve_path=True
    )
):
    """(not implemented yet)"""
    print(
        f"if this were implemneted it would apply the patch at {patch_file} to the last bundled repo"
    )


@app.command()
def rebundle():
    """(not implemented yet)"""
    print("if this were implemented it would re-bundle the last bundled repo")


def cli():
    import sys

    if len(sys.argv) == 1:
        # show help even if user didn't pass --help
        sys.argv += ["--help"]
        app()
    else:
        app()


if __name__ == "__main__":
    cli()
