# AgentGrunt

### TL;DR:

Turn OpenAI's Code Interpreter into a coding sidekick that can edit your codebase on your behalf, **and commit them to your repo**!
### Overview

**AgentGrunt** lets you take any git repository you have available on your local machine, packs up your repo (along with with some prompts and tools to allow Code Interpreter to work with it effectively) in such a way that you can upload it into Code Interpreter and let Code Interpreter work with it. 

The coolest part is that one of the tools it packs up for you is a full-fledged working version of `git` so that Code Interpreter can make commits to your repo on your behalf!

Since Code Interpreter doesn't have internet access **AgentGrunt** makes use of one of git's more esoteric features to send you patch files that you can apply to your repo as full commits, with history and metadata. Once you start an AgentGrunt session Code Interpreter itself will walk you through the process of applying the commits to your local copy of your repository.

### What is this useful for?

Lots of things! Some examples that work pretty well:

- Learning or exploring a new codebase: 
	
	Upload a codebase you're unfamiliar with into AgentGrunt and ask it to give you an overview of the codebase or to explain how some part of the codebase works

- Repetitive refactoring tasks. 
	Before settling on AgentGrunt this repo had a different name. To rename it, I uploaded this repo itself into AgentGrunt and it took care of updating the README, the pyproject.toml file, the folder names, and a few constants in the code base on it's own (you can see the diff [here](https://github.com/nikvdp/agentgrunt/compare/d990b666741558b34fd1a1fe8b3b0577b95a2e43...e43ac2f02824ed1817a2426e8b8746c5f592cdc2))
 
  ...
### Installation

If you have a working python 3.9 or 3.10 installation do:
```shell
pip install 'git+https://github.com/nikvdp/agentgrunt.git'
```

Once it's completed successfully you'll have a new `agentgrunt` command available.

### Usage

To start editing a repo with `agentgrunt` you can use `agentgrunt`'s `bundle` command:

```shell
agentgrunt bundle <path-to-your-repo>
```
and follow the instructions. When it's finished there'll be a new `<your-repo-name>.tar.gz` in your current folder. 

Copy the short prompt `agentgrunt` shows in the output to your clipboard, open up ChatGPT in Code Interpreter mode, paste in the prompt, and drag in the `tar.gz` file `agentgrunt` created a second ago. Then press send in ChatGPT, wait a few moments for it to extract your archive and you'll be created with a message saying "Code Interpreter has been upgraded to Code Editor". 



then (make sure to click the GPT4 dropdown and choose Code Interpreter. If it's not present you may need to first enable Code Interpreter in ChatGPT's settings).