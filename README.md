# gpt-engineer-example

Does not use the agent-harness yet. Uses a toy repo `./myproj` while we try to get gpt-engineer working.

Running `main.py` will do the following:
- create a temporary workspace folder `./deleteme`
- copy the toy repo `./myproj` into `./deleteme` (emulates cloning the repo)
- move `prompt` into the workspace (gpt-engineer looks for this)
- generate list of project files into `file_list.txt` in workspace (gpt-engineer looks for this)
- run gpt-engineer on the workspace in "auto-mode"

TODO:
- gpt-engineer writes changes into a copy of the project. We need to copy the changes back into `./deleteme/myproj`
- use the agent-harness to get real repos instead of the toy repo `./myproj`
- use the agent-harness to get real prompts instead of the toy prompt `./prompt`
- use the agent-harness to submit changes