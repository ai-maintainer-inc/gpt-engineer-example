from agent_harness.agent_harness import (
    get_benchmark_ids,
    start_benchmark,
    submit_artifact,
    maybe_register_user,
)
import os
import shutil
import gpt_engineer.main as gpt_engineer_main
from gpt_engineer.steps import Config as StepsConfig
from dotenv import load_dotenv
from typing import List


WORKSPACE_PATH = "./deleteme"
CODE_PATH = "./deleteme/myproj"


def setup():
    # monkeypatch gpt_engineer collect_consent
    gpt_engineer_main.collect_consent = lambda: True

    # create a clean workspace
    if os.path.exists(WORKSPACE_PATH):
        shutil.rmtree(WORKSPACE_PATH)
    os.mkdir(WORKSPACE_PATH)

    # move project folder into workspace
    shutil.copytree("myproj", CODE_PATH)

    # move prompt file into workspace
    shutil.copy("prompt", os.path.join(WORKSPACE_PATH, "prompt"))

    # create file_list.txt in workspace
    file_list = make_file_list(
        CODE_PATH,
        ignore_dirs=[".git, .benchmark"],
        ignore_files=[".DS_Store"],
    )
    with open(os.path.join(WORKSPACE_PATH, "file_list.txt"), "w") as f:
        for file in file_list:
            f.write(file + "\n")


def make_file_list(code_path: str, ignore_dirs=[], ignore_files=[]) -> List[str]:
    # generates a list of absolute paths to all files in code_path
    # skips files in ignore_files and directories in ignore_dirs
    file_list = []
    for root, dirs, files in os.walk(code_path):
        for file in files:
            if file not in ignore_files:
                file_list.append(os.path.join(root, file))
        for dir in dirs:
            if dir in ignore_dirs:
                dirs.remove(dir)

    return file_list


def run_agent():
    # run gpt-engineer
    gpt_engineer_main.main(
        os.path.abspath("deleteme"),
        "gpt-4",
        0.1,
        StepsConfig.EVAL_IMPROVE_CODE,
        True,
        None,
        False,
    )


def apply_changes():
    """
    TODO:
    - move files from {WORKSPACE_PATH}/workspace/myproj to {CODE_PATH}
    """
    pass


def main():
    load_dotenv()
    # maybe_register_user()
    setup()
    run_agent()
    apply_changes()


if __name__ == "__main__":
    main()
