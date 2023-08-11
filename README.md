# 🕵️🧰 AgentGrunt ️

## TL;DR:

Skip the gruntwork! Let AgentGrunt write, edit, and commit code to your own repos for you from inside of [Code Interpreter](https://openai.com/blog/chatgpt-plugins#code-interpreter). 

## Overview

AgentGrunt packs up an codebase, a specially prepared `git` binary that runs in Code Interpreter's environment, and some prompts and code exploration tools into a single file that you can load into Code Interpreter.

Upload the archive, paste in a two sentence prompt, wait a bit, and then let GPT4 write, edit, and commit your code for you. When GPT4 has finished making your changes, press `d` from the hotkey menu and ChatGPT will send you a file you can use to apply the commits GPT4 made (with all their metadata!) directly into your copy of the repo. 
## Features:

- automatically installs `git` into Code Intrerpreter and configures it for code exploration 
- built in hotkey menu for easy usage
- simple, small, and easy to customize.

## Installation
#### Prereqs:

- a valid ChatGPT Plus subscription and Code Interpreter enabled in ChatGPT's settings
- a working python 3.9 or 3.10 installation
- a local git repository that you'd like Code Interpreter to work on with you

Once you have those in place, run:

```shell
pip install agentgrunt
```

If all goes well running `agentgrunt --help` ill output something like this:

```
Usage: agentgrunt [OPTIONS] COMMAND [ARGS]...

Options:
  --help                          Show this message and exit.

Commands:
  apply-remote-changes  (not implemented yet)
  bundle
  rebundle              (not implemented yet)

```

## Usage

To start editing a repo with `agentgrunt` use `agentgrunt`'s `bundle` command:

```shell
agentgrunt bundle <path-to-your-repo>
```
It will do some work and then print out some instructions. When the process has completed you'll have a new file called `<your-repo-name>.tar.gz` in your current folder. 

Now do the following:
-  Copy the short prompt `agentgrunt` prints out to the clipboard (or just say `y` when prompted if on macOS)
- open up ChatGPT and start a new chat in Code Interpreter mode,
- use the +  button to upload the `<your-repo-name>.tar.gz` file
- paste the prompt you copied  a second ago into the chatbox and press send. 

You'll see ChatGPT start to do some work, and a few moments and you'll be greeted with a message saying "Code Interpreter has been upgraded to Code Editor" followed by a hotkey menu similar to the below:

```
l) list changes made so far
c) continue 
d) download changes
r) reload (reload the readme)
?) show this hotkey list
```

Now just ask Code Interpreter to make some changes to your repo, and hit `d` when you're finished to download the changes it made to your local copy of the repo!

Make sure to ask ChatGPT to commit it's changes! 

When you want to download the changes you've made to your local copy of the repo, hit `d`  and Code Interpreter will send you a `.patch` file that you can apply to your copy of the git repo using the (somewhat esoteric) `git am` command:

```shell
git am <path-to-patch-file>
```

## How it works

The python package contains a special [`gpt_tools`](agentgrunt/gpt_tools) folder that gets copied into each bundle AgentGrunt generates. That includes a prompt for Code Interpreter to read in the [`README_ai.md`](agentgrunt/gpt_tools/README_ai.md) file, as well as some python functions that are useful for code exploration that Code Interpreter can load and call directly (see [`code_exploration.py`](agentgrunt/gpt_tools/code_exploration.py)).

When you ask AgentGrunt to generate a bundle it first downloads a single-file version of the `git`  binary from 1bin.org (an older project of mine to make easy to deploy single file binaries of common utilities). Then it clones the repo you point it at into a temporary location location (to avoid bundling up any files that aren't part of the repo, eg `node_modules` folders), copies the `git` binary and the README_ai and code_exploration files into the folder structure described in the README_ai file, and then builds a tarball out of the whole collection.

This arrangement allows the prompt the user has to paste in to ChatGPT to be short and simple, and Code Interpreter itself can then extract the longer prompt from README_ai and bootstrap itself from there.

## Caveats and gotchas

- GPT4 makes a lot of mistakes and is easily confused! While AgentGrunt can be genuinely useful, it's not going to be replacing a human dev any time soon. Expect it to require a fair bit of babysitting and handholding to be able to accomplish meaningful tasks.
- During longer conversations GPT4 tends to forget what it's doing and sometimes stops showing the hotkey menu or that `git` and the tools from `code_exploration.py` functions are available. If this happens, hit `r`  or ask it to re-read "it's" readme file to refresh its memory.
- Code Interpreter is subject to a ~2 minute timeout while working autonomously, so for longer running operations you may need to tell it `c` (continue) to have it finish what it was doing
- Code Interpreter deletes it's workspace files if it's been left idle for too long (seems to be in the ~10-15m range), and when this happens any links to files it may have sent will stop working. **Make sure to download any patch files it sends you immediately to avoid losing your work!** 

## TODOs / future improvements / how to help / acknowledgements

This is still early and more of a proof of concept than anything else. That said, even in it's current form it's often genuinely useful! Allowing Code Interpreter to read files and archives in this way also opens the door for lots of interesting applications. AgentGrunt only uses one prompt, but it's easy to imagine more complex tools like this that include a catalogue of prompts that "daisy-chain" from each other, am very curious to see what other things people build in this vein!

Hattip to [@NickADobos](https://twitter.com/NickADobos)' and his "[AI zip bomb](https://twitter.com/NickADobos/status/1687938356813180928)" thread for the inspiration!

