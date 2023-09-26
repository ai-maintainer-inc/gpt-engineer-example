from coder_evals import (
    get_benchmark_ids,
    start_benchmark,
    submit_artifact,
    maybe_register_user,
    BenchmarkContext,
)
import os
import shutil
import gpt_engineer.main as gpt_engineer_main
from gpt_engineer.steps import Config as StepsConfig
from dotenv import load_dotenv
from typing import List, Tuple
from distutils import dir_util
import docker
import uuid
from textwrap import dedent


WORKSPACE_PATH = "./.workspace"


def docker_eval(dockerfile_subdir: str) -> Tuple[bool, str]:
    client = docker.from_env()
    image_tag = str(uuid.uuid4())
    parent_dir = os.path.dirname(dockerfile_subdir)
    dockerfile_name = os.path.join(os.path.basename(dockerfile_subdir), "Dockerfile")

    try:
        image, build_logs = client.images.build(
            path=parent_dir, tag=image_tag, dockerfile=dockerfile_name
        )
        logs = "".join([str(log) for log in build_logs])

    except docker.errors.BuildError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

    try:
        stdout_bytes = client.containers.run(image=image_tag, remove=True, stdout=True)
        stdout = stdout_bytes.decode("utf-8")
        return True, stdout
    except docker.errors.ContainerError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def _local_eval(path: str) -> bool:
    success, logs = docker_eval(path)
    return success, logs


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


def prompt_template(ctx: BenchmarkContext, logs: str) -> str:
    if not logs:
        return ctx.ticket["description"]
    else:
        msg = dedent(
            f"""
            {ctx.ticket["description"]}

            Local eval failed with the following error:
            {logs}
            """
        )
        return msg


def run_agent():
    benchmark_ids = get_benchmark_ids(
        after="2023-09-04T17:21:19.73387Z",
        title_search="persistent | v2",
    )

    for benchmark_id in benchmark_ids:
        # init benchmark
        ctx = start_benchmark(benchmark_id, WORKSPACE_PATH)
        success, logs = False, None
        for i in range(6):
            # write prompt
            with open(os.path.join(WORKSPACE_PATH, "prompt"), "w") as f:
                f.write(prompt_template(ctx, logs))

            # create file_list.txt in workspace
            file_list = make_file_list(
                ctx.cloned_path,
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
                apply_changes(
                    WORKSPACE_PATH, ctx.ticket["code"]["repo"], ctx.cloned_path
                )
            except Exception as e:
                print(f"Error applying changes: {e}")

            # run local eval
            dpath = os.path.join(ctx.cloned_path, ".benchmark")
            print(f"Running local eval for {dpath}")
            success, logs = _local_eval(dpath)
            print(f"Local eval success: {success}")
            if success:
                break
            else:
                print(f"Local eval failed with the following error:\n{logs}")

        # submit artifact
        status, logs = submit_artifact(ctx)
        print(f"\n\nBenchmark with ID {benchmark_id} completed with status {status}")
        print(f"Logs for benchmark {benchmark_id}:\n{logs}\n\n")


def main():
    load_dotenv()
    maybe_register_user()
    setup()
    run_agent()


if __name__ == "__main__":
    main()
