# AgentGrunt

Make Code Interpreter into a Code Editor.

some strategies that seem to work:

- investigation mode:

  - give it a "code mission" and have it explore the repository
  - works best if you give it a job to do of some sort so it can keep that in
    mind while it's exploring
  - also works well to ask it to generate an implementation plan

- implementing stuff:

  - a prompt i used:
    > ok. please implement step 1. use the knowledge you have collected so far to
    > make a more specific implementation plan for step 1, doing any necessary
    > investigations needed. once you have finished your plan, double check it by
    > stepping through each of it's assertions, guessing how they could be wrong, and
    > attempting to test your assumptions by furhter explorastion of the code base.
    > and once you are sure you have a clear plan let me know
    it was medium succesful. the interesting bit was asking it to criticize
    itself, which made it write up a nice set of assertions and then
    coutnerarguments

### Improvement Ideas

- It often forgets about the hotkeys, however if I use one it looks more
  carefully at the prior context and figures it out again. Should consider
  adding an `r` hotkey for reload/refresh that gets it to re-read the readme so
  it remembers more.

- It also forgets where it is in the filesystem, would be good to give it more
  memory/internal notes.

- Should also consider having it keep a list of what it "forgets" in a
  background loop. Should consistently be updating "forgotten" stuff and
  putting it higher up on the list
