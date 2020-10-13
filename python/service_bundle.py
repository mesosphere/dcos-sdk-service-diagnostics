import functools
import json
import logging
import os
import warnings
from toolz import groupby
from typing import List

import sdk_cmd
import sdk_diag

from bundle import Bundle
import agent
import config

log = logging.getLogger(__name__)


class ServiceBundle(Bundle):
    DOWNLOAD_FILES_WITH_PATTERNS = ["^stdout(\\.\\d+)?$", "^stderr(\\.\\d+)?$"]

    def __init__(self, service_name, scheduler_tasks, service, output_directory):
        self.service_name = service_name
        self.scheduler_tasks = scheduler_tasks
        self.service = service
        self.framework_id = service.get("id")
        self.output_directory = output_directory

    def tasks(self):
        return self.service.get("tasks") + self.service.get("completed_tasks")

    def tasks_with_state(self, state):
        return list(filter(lambda task: task["state"] == state, self.tasks()))

    def running_tasks(self):
        return self.tasks_with_state("TASK_RUNNING")

    def run_on_tasks(self, fn, task_ids):
        for task_id in task_ids:
            fn(task_id)

    def for_each_running_task_with_prefix(self, prefix, fn):
        task_ids = [t["id"] for t in self.running_tasks() if t["name"].startswith(prefix)]
        self.run_on_tasks(fn, task_ids)

    def for_each_running_task_with_suffix(self, suffix, fn):
        task_ids = [t["id"] for t in self.running_tasks() if t["name"].endswith(suffix)]
        self.run_on_tasks(fn, task_ids)

    # tasks can be self.running_tasks() or self.tasks() or self.scheduler_tasks + self.tasks()
    @staticmethod
    def get_tasks_with_prefix(prefix, tasks: List) -> List:
        return [t for t in tasks if t["name"].startswith(prefix)]

    @staticmethod
    def get_tasks_with_suffix(suffix, tasks: List) -> List:
        return [t for t in tasks if t["name"].endswith(suffix)]

    def download_log_files(self):
        all_tasks = self.scheduler_tasks + self.tasks()

        tasks_by_agent_id = dict(groupby("slave_id", all_tasks))

        for agent_id, tasks in tasks_by_agent_id.items():
            agent_files = agent.debug_agent_files(agent_id)
            for task in tasks:
                task_executor_sandbox_path = sdk_diag._find_matching_executor_path(
                    agent_files, sdk_diag._TaskEntry(task)
                )
                if task_executor_sandbox_path:
                    agent.download_task_files(
                        task,
                        task_executor_sandbox_path,
                        os.path.join(self.output_directory, "tasks"),
                        self.DOWNLOAD_FILES_WITH_PATTERNS,
                    )
                else:
                    log.info(
                        "Could not find executor sandbox path for task '%s'. "
                        "This probably means that its agent ('%s') is missing",
                        task["id"],
                        task["slave_id"],
                    )

    def download_task_log_files(self, tasks: List, path_to_files: str, file_patterns_to_download: List[str]):
        """
        Version which takes list of tasks, templated path and patterns of log files to be downloaded.
        Downloads files which match patterns in 'patterns_to_download'. The files for download are located in target dir specified in 'path_to_files'.
        Example. For downloading log files in any location of kind '<sandbox-root>/nifi-<version>/logs/' you can specify this templated path: "{^nifi-(.+)$}/logs"

        :param tasks: List of tasks which sandboxes should be searched for matching log files
        :param path_to_files: Relative path to target dir from task sandbox root. The path elements can be RE expressions  marked by enclosing {}.
        :param file_patterns_to_download: List of RE patterns matching basenames of log files
        """
        tasks_by_agent_id = dict(groupby("slave_id", tasks))

        for agent_id, tasks in tasks_by_agent_id.items():
            agent_files = agent.debug_agent_files(agent_id)
            for task in tasks:
                task_executor_sandbox_path = sdk_diag._find_matching_executor_path(
                    agent_files, sdk_diag._TaskEntry(task)
                )
                if task_executor_sandbox_path:
                    agent.download_task_only_files(
                        task,
                        task_executor_sandbox_path,
                        os.path.join(self.output_directory, "tasks"),
                        path_to_files,
                        file_patterns_to_download
                    )
                else:
                    log.info(
                        "Could not find executor sandbox path for task '%s'. "
                        "This probably means that its agent ('%s') is missing",
                        task["id"],
                        task["slave_id"],
                    )


    @config.retry
    def create_offers_file(self):
        warnings.warn("The v1/debug/offers endpoint will be deprecated in favour of the newer "
                      "v2/debug/offers endpoint.", PendingDeprecationWarning)
        response = sdk_cmd.service_request("GET", self.service_name, "/v1/debug/offers",
                                           raise_on_error=False)
        if not response.ok:
            log.error(
                "Could not get scheduler offers\nstatus_code: '%s'\nstderr: '%s'",
                response.status_code, response.text
            )
        else:
            self.write_file("service_v1_debug_offers.html", response.text)

    @config.retry
    def create_v2_offers_file(self):
        response = sdk_cmd.service_request("GET", self.service_name, "/v2/debug/offers",
                                           raise_on_error=False)
        if not response.ok:
            log.error(
                "Could not get v2 scheduler offers\nstatus_code: '%s'\nstderr: '%s'",
                response.status_code, response.text
            )
        else:
            self.write_file("service_v2_debug_offers.json", response.text)

    @config.retry
    def create_plans_file(self):
        response = sdk_cmd.service_request("GET", self.service_name, "/v1/debug/plans",
                                           raise_on_error=False)
        if not response.ok:
            log.error(
                "Could not get scheduler plans\nstatus_code: '%s'\nstderr: '%s'",
                response.status_code, response.text
            )
        else:
            self.write_file("service_v1_debug_plans.json", response.text)

    @config.retry
    def create_task_statuses_file(self):
        response = sdk_cmd.service_request("GET", self.service_name, "/v1/debug/taskStatuses",
                                           raise_on_error=False)
        if not response.ok:
            log.error(
                "Could not get scheduler task-statuses\nstatus_code: '%s'\nstderr: '%s'",
                response.status_code, response.text
            )
        else:
            self.write_file("service_v1_debug_taskStatuses.json", response.text)

    @config.retry
    def create_task_reservations_file(self):
        response = sdk_cmd.service_request("GET", self.service_name, "/v1/debug/reservations",
                                           raise_on_error=False)
        if not response.ok:
            log.error(
                "Could not get scheduler task-reservations\nstatus_code: '%s'\nstderr: '%s'",
                response.status_code, response.text
            )
        else:
            self.write_file("service_v1_debug_reservations.json", response.text)

    @functools.lru_cache()
    @config.retry
    def configuration_ids(self) -> List[str]:
        response = sdk_cmd.service_request("GET", self.service_name, "/v1/configurations",
                                           raise_on_error=False)
        if not response.ok:
            log.error(
                "Could not get scheduler configurations\nstatus_code: '%s'\nstderr: '%s'",
                response.status_code, response.text
            )
        else:
            return json.loads(response.text)

    @functools.lru_cache()
    @config.retry
    def configuration_target_id(self) -> List[str]:
        response = sdk_cmd.service_request("GET", self.service_name, "/v1/configurations/targetId",
                                           raise_on_error=False)
        if not response.ok:
            log.error(
                "Could not get scheduler configuration target id\nstatus_code: '%s'\nstderr: '%s'",
                response.status_code, response.text
            )
        else:
            return json.loads(response.text)

    @functools.lru_cache()
    @config.retry
    def configuration(self, configuration_id) -> dict:
        response = sdk_cmd.service_request("GET", self.service_name,
                                           "/v1/configurations/{}".format(configuration_id),
                                           raise_on_error=False)
        if not response.ok:
            log.error("Could not get scheduler configuration with ID '%s'"
                      "\nstatus_code: '%s'\nstderr: '%s'",
                      configuration_id, response.status_code, response.text
                      )
        else:
            return json.loads(response.text)

    @config.retry
    def create_configuration_ids_file(self):
        self.write_file(
            "service_v1_configuration_ids.json", self.configuration_ids(), serialize_to_json=True
        )

    @config.retry
    def create_configuration_target_id_file(self):
        self.write_file(
            "service_v1_configuration_target_id.json", self.configuration_target_id(), serialize_to_json=True
        )

    @config.retry
    def create_configuration_files(self):
        for configuration_id in self.configuration_ids():
            self.write_file(
                "service_v1_configuration_{}.json".format(configuration_id),
                self.configuration(configuration_id),
                serialize_to_json=True,
            )

    def create(self):
        self.create_offers_file()
        self.create_v2_offers_file()
        self.create_plans_file()
        self.create_task_statuses_file()
        self.create_task_reservations_file()
        self.create_configuration_ids_file()
        self.create_configuration_target_id_file()
        self.create_configuration_files()
        self.download_log_files()
