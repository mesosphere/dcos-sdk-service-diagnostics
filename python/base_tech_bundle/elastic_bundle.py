import logging

import sdk_cmd

from base_tech_bundle import BaseTechBundle
import config

logger = logging.getLogger(__name__)


class ElasticBundle(BaseTechBundle):
    def __init__(
        self, package_name, service_name, scheduler_tasks, service, output_directory
    ):
        super().__init__(
            package_name, service_name, scheduler_tasks, service, output_directory
        )

    @config.retry
    def task_exec(self, task_id, cmd, print_output=True):
        full_cmd = " ".join(
            [
                "export JAVA_HOME=$(ls -d ${MESOS_SANDBOX}/jdk*/) &&",
                "export TASK_IP=$(${MESOS_SANDBOX}/bootstrap --get-task-ip) &&",
                "ELASTICSEARCH_DIRECTORY=$(ls -d ${MESOS_SANDBOX}/elasticsearch-*/) &&",
                cmd,
            ]
        )

        return sdk_cmd.marathon_task_exec(
            task_id, "bash -c '{}'".format(full_cmd), print_output=print_output
        )

    def create_http_api_output_file(self, task_id, path):
        command = 'curl -s "${{MESOS_CONTAINER_IP}}:${{PORT_HTTP}}/{}"'.format(path)
        rc, stdout, stderr = self.task_exec(task_id, command, print_output=False)

        if rc != 0:
            logger.error(
                "Could not GET '/%s'. return-code: '%s'\nstdout: '%s'\nstderr: '%s'",
                path,
                rc,
                stdout,
                stderr,
            )
        else:
            if stderr:
                logger.warning("GET '/%s'\nstderr: '%s'", path, stderr)
            self.write_file(
                "elasticsearch_{}_{}.json".format(
                    self.url_path_as_file_name(path), task_id
                ),
                stdout,
            )

    def create_tasks_http_api_output_files(self, path):
        self.for_each_running_task_with_prefix(
            "master", lambda task_id: self.create_http_api_output_file(task_id, path)
        )

    def create(self):
        logger.info("Creating Elastic bundle")
        self.create_configuration_file()
        self.create_pod_status_file()
        self.create_plans_status_files()
        for path in [
            "_cat/indices?v",
            "_cat/shards?v",
            "_cluster/health?pretty&human",
            "_cluster/state?pretty&human",
            "_cluster/stats?pretty&human",
            "_stats?pretty&human",
        ]:
            self.create_tasks_http_api_output_files(path)
