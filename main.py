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
from distutils import dir_util


WORKSPACE_PATH = "./.workspace"
REPO = "myproj"
CODE_PATH = os.path.join(WORKSPACE_PATH, REPO)
DUMMY_FILE = "deleteme-dummy"


def setup():
    # monkeypatch gpt_engineer collect_consent
    gpt_engineer_main.collect_consent = lambda: True

    # create a clean workspace
    if os.path.exists(WORKSPACE_PATH):
        shutil.rmtree(WORKSPACE_PATH)
    os.mkdir(WORKSPACE_PATH)


def make_file_list(code_path: str, ignore_dirs=[], ignore_files=[]) -> List[str]:
    # generates a list of absolute paths to all files in code_path
    # skips files in ignore_files and directories in ignore_dirs
    file_list = []
    for root, dirs, files in os.walk(code_path):
        if any([dir in root for dir in ignore_dirs]):
            continue
        for file in files:
            if file in ignore_files:
                continue
            abs_path = os.path.abspath(os.path.join(root, file))
            file_list.append(abs_path)

    return file_list


def apply_changes(workspace_path, repo_name, code_path):
    # move files from {workspace_path}/workspace/{repo_name} to {code_path}
    # {workspace_path}/workspace/{repo_name} only contains changes
    # some files in {code_path} aren't in {workspace_path}/workspace/{repo_name}
    source_dir = os.path.join(workspace_path, "workspace", repo_name)
    dir_util.copy_tree(source_dir, code_path)


def run_agent():
    benchmark_ids = get_benchmark_ids(
        after="2023-09-04T17:21:19.73387Z",
        # title_search="test & hello",
    )

    for benchmark_id in benchmark_ids:
        # init benchmark
        info = start_benchmark(benchmark_id, WORKSPACE_PATH)

        # write prompt
        with open(os.path.join(WORKSPACE_PATH, "prompt"), "w") as f:
            f.write(info.ticket["description"])

        # create file_list.txt in workspace
        file_list = make_file_list(
            info.cloned_path,
            ignore_dirs=[".git", ".benchmark"],
            ignore_files=[".DS_Store"],
        )
        with open(os.path.join(WORKSPACE_PATH, "file_list.txt"), "w") as f:
            for file in file_list:
                f.write(file + "\n")

        # run gpt-engineer
        try:
            gpt_engineer_main.main(
                os.path.abspath(WORKSPACE_PATH),
                "gpt-4",
                0.1,
                StepsConfig.EVAL_IMPROVE_CODE,
                True,
                None,
                False,
            )
        except Exception as e:
            print(f"Error running gpt-engineer: {e}")

        # apply changes
        try:
            apply_changes(WORKSPACE_PATH, info.ticket["code"]["repo"], info.cloned_path)
        except Exception as e:
            print(f"Error applying changes: {e}")

        # submit artifact
        status, logs = submit_artifact(info)
        print(f"\n\nBenchmark with ID {benchmark_id} completed with status {status}")
        print(f"Logs for benchmark {benchmark_id}:\n{logs}\n\n")


def main():
    load_dotenv()
    maybe_register_user()
    setup()
    run_agent()


if __name__ == "__main__":
    main()
