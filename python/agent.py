import logging
import os
import re
import datetime
from typing import List
from functools import reduce

import sdk_cmd

import config

logger = logging.getLogger(__name__)


def is_http_server_error(http_status_code: int) -> bool:
    return http_status_code >= 500 and http_status_code <= 599


@config.retry
def debug_agent_files(agent_id: str) -> List[str]:
    response = sdk_cmd.cluster_request(
        "GET",
        "/slave/{}/files/debug".format(agent_id),
        retry=False,
        raise_on_error=False,
        log_response=False,
    )

    if is_http_server_error(response.status_code):
        # Retry.
        raise Exception(response)

    if response.status_code == 404:
        return {}

    if not response.ok:
        # Retry.
        raise Exception(response)

    return response.json()


@config.retry
def browse_agent_path(agent_id: str, agent_path: str) -> List[dict]:
    response = sdk_cmd.cluster_request(
        "GET",
        "/slave/{}/files/browse?path={}".format(agent_id, agent_path),
        retry=False,
        raise_on_error=False,
        log_response=False,
    )

    if is_http_server_error(response.status_code):
        # Retry.
        raise Exception(response)

    if response.status_code == 404:
        return []

    if not response.ok:
        # Retry.
        raise Exception(response)

    return response.json()


def browse_executor_sandbox(agent_id: str, executor_sandbox_path: str) -> List[dict]:
    return browse_agent_path(agent_id, executor_sandbox_path)


def browse_executor_tasks(agent_id: str, executor_sandbox_path: str) -> List[dict]:
    return browse_executor_sandbox(agent_id, os.path.join(executor_sandbox_path, "tasks"))


def browse_task_sandbox(agent_id: str, executor_sandbox_path: str, task_id: str) -> List[dict]:
    executor_tasks = browse_executor_tasks(agent_id, executor_sandbox_path)

    if executor_tasks:
        task_sandbox_path = os.path.join(executor_sandbox_path, "tasks/{}/".format(task_id))
        return browse_agent_path(agent_id, task_sandbox_path)
    else:
        return []


# Does download of files which match patterns in patterns_to_download. The files for download are located
# in target dir specified in path_to_files.
#
# param: path_to_files  Relative path to target dir from task sandbox root. The path elements can be RE expressions,
# marked by enclosing {}.
# Example. For downloading log files in any location of kind '<sandbox-root>/nifi-<version>/logs/' you can specify
#          this templated path: "{^nifi-(.+)$}/logs"
def download_task_files_deep(agent_id: str, task_id: str, executor_sandbox_path: str, path_to_files: str,
                             patterns_to_download: List[str], output_dir_base: str) -> int:
    task_sandbox_path = os.path.join(executor_sandbox_path, "tasks/{}/".format(task_id))
    task_sandbox = browse_agent_path(agent_id, task_sandbox_path)
    if not task_sandbox:
        logger.error("download_task_files_deep: cannot read task sandbox dir %s", task_sandbox_path)
        return 3
    output_dir_path = output_dir_base

    for t in path_to_files.split('/'):
        is_regexp_name = False
        if t.startswith('{') and t.endswith('}'):
            is_regexp_name = True
            path_name = t[1:len(t)-1]
        else:
            path_name = t
        # for patterned name in path we need to translate it into real dir name
        if is_regexp_name:
            if task_sandbox is None: task_sandbox = browse_agent_path(agent_id, task_sandbox_path)
            real_path_name = None
            for x in task_sandbox:
                file_basename = os.path.basename(x["path"])
                m = re.match(path_name, file_basename)
                real_path_name = m.group(0) if m else None
                if real_path_name:
                    task_sandbox_path = os.path.join(task_sandbox_path, real_path_name)
                    output_dir_path = os.path.join(output_dir_path, real_path_name)
                    break  # stop current search and proceed to next path_name
            if real_path_name is None:
                logger.error("download_task_files_deep: cannot find match for pattern '%s' in dir %s", path_name, task_sandbox_path)
                return 2  # stop search completely -> report failure
        else:
            task_sandbox_path = os.path.join(task_sandbox_path, path_name)
            output_dir_path = os.path.join(output_dir_path, path_name)
        task_sandbox = None  # invalidate old sandbox

    # download actual files from target dir
    task_sandbox = browse_agent_path(agent_id, task_sandbox_path)
    if task_sandbox:
        download_sandbox_files(agent_id, task_sandbox, output_dir_path, patterns_to_download)
        return 0  # target dir exist and not empty
    else:
        return 1  # either final path does not exist or target dir is empty


@config.retry
def download_agent_path(
    agent_id: str, agent_file_path: str, output_file_path: str, chunk_size: int = 8192
) -> None:
    stream = sdk_cmd.cluster_request(
        "GET",
        "/slave/{}/files/download?path={}".format(agent_id, agent_file_path),
        retry=False,
        raise_on_error=False,
        log_response=False,
        stream=True,
    )

    if is_http_server_error(stream.status_code):
        raise Exception(stream)

    if stream.status_code == 404:
        return

    if not stream.ok:
        # Retry.
        raise Exception(stream)

    with open(output_file_path, "wb") as f:
        for chunk in stream.iter_content(chunk_size=chunk_size):
            f.write(chunk)


def download_sandbox_files(
    agent_id: str, sandbox: List[dict], output_base_path: str, patterns_to_download: List[str]
) -> None:
    if not sandbox:
        logger.warning("download_sandbox_files: input file list is empty!")
        return
    if not os.path.exists(output_base_path):
        os.makedirs(output_base_path)

    for task_file in sandbox:
        # print("download_sandbox_files: file_path = " + task_file["path"])
        task_file_basename = os.path.basename(task_file["path"])
        for pattern in patterns_to_download:
            # print("download_sandbox_files: pattern = " + pattern)
            if re.match(pattern, task_file_basename):
                download_agent_path(
                    agent_id, task_file["path"], os.path.join(output_base_path, task_file_basename)
                )


def download_task_files(
    task,
    executor_sandbox_path: str,
    base_path: str,
    patterns_to_download: List[str] = [],
) -> List[dict]:
    agent_id = task["slave_id"]
    task_id = task["id"]
    task_folder_name = build_task_folder_name(task)

    executor_sandbox = browse_executor_sandbox(agent_id, executor_sandbox_path)
    pod_task_sandbox = browse_task_sandbox(agent_id, executor_sandbox_path, task_id)

    # Pod task: download files under its sandbox and also under its parent executor's sandbox.
    if pod_task_sandbox:
        output_pod_task_directory = os.path.join(base_path, task_folder_name, "task")
        download_sandbox_files(
            agent_id, pod_task_sandbox, output_pod_task_directory, patterns_to_download
        )

        output_executor_directory = os.path.join(base_path, task_folder_name, "executor")
        download_sandbox_files(
            agent_id, executor_sandbox, output_executor_directory, patterns_to_download
        )
    # Scheduler task: no parent executor, only download files under its sandbox.
    else:
        output_directory = os.path.join(base_path, task_folder_name)
        download_sandbox_files(agent_id, executor_sandbox, output_directory, patterns_to_download)


# Does download of files which match patterns in patterns_to_download. The files for download are located
# in target dir specified in path_to_files. Files for search must be in task's sandbox (executor's sandbox is ignored).
#
# param: path_to_files  Relative path to target dir from task sandbox root. The path elements can be RE expressions,
# marked by enclosing {}.
# Example. For downloading log files in any location of kind '<sandbox-root>/nifi-<version>/logs/' you can specify
#          this templated path: "{^nifi-(.+)$}/logs"
def download_task_only_files(
        task,
        executor_sandbox_path: str,
        base_path: str,
        path_to_files: str,
        patterns_to_download: List[str]
) -> None:
    agent_id = task["slave_id"]
    task_id = task["id"]
    task_folder_name = build_task_folder_name(task)
    output_dir_base = os.path.join(base_path, task_folder_name, "task")
    download_task_files_deep(agent_id, task_id, executor_sandbox_path, path_to_files, patterns_to_download, output_dir_base)


def build_task_folder_name(task):
    match = re.search("([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", task["id"])
    if match is not None:
        task_uuid = match.group(0)
        folder_name = build_task_state_timestamps(task) + "__" + task["name"] + "__" + task_uuid
    else:
        folder_name = build_task_state_timestamps(task) + "__" + task["id"]

    return folder_name


def build_task_state_timestamps(task):
    task_state_timestamps = reduce(lambda result, status:
                                   result + status["state"].lower() + "_" + datetime.datetime.fromtimestamp(status["timestamp"])
                            .strftime("%Y%m%dT%H%M%S") + "-",
                            task["statuses"], "")
    task_state_timestamps = task_state_timestamps.replace("task_", "")
    task_state_timestamps = task_state_timestamps[:-1]
    return task_state_timestamps
