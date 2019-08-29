# Service Diagnostics Bundle

Script that gathers SDK-related service diagnostics artifacts.

## Artifacts Gathered

- `dcos service --completed --inactive --json` output
- `dcos $service describe` output
- `dcos $service pod status --json` output
- `dcos $service plan status $plan --json` output for all `$plan`s
- stdout and stderr log files for all pod tasks and their executors (even killed
  or finished ones) and scheduler tasks
- `https://$cluster/$service/v1/debug/offers` output. WARNING: Will be deprecated in favour of
v2/debug/offers below in upcoming releases.
- `https://$cluster/$service/v2/debug/offers` output
- `https://$cluster/$service/v1/debug/plans` output
- `https://$cluster/$service/v1/debug/taskStatuses` output
- `https://$cluster/$service/v1/configurations/$configuration_id` output for all
  `$configuration_id`s
- Output of base-tech specific diagnostics commands (e.g.: Cassandra's `nodetool
  status`, Elasticsearch's node stats, etc.)

## Known Limitations

- Doesn't currently work with Spark services since Spark is not an SDK service
- Doesn't currently work with crash-looping schedulers
- Doesn't currently create a compressed archive from the bundle directory

## Requirements

- Docker
- Network access to DC/OS cluster
- DC/OS 1.10+

## Usage

1. Download the latest version

   ```bash
   wget https://infinity-artifacts.s3.amazonaws.com/dcos-commons/diagnostics/latest/create_service_diagnostics_bundle.sh
   chmod +x create_service_diagnostics_bundle.sh
   ```

1. Run script against a service. In this case against a Cassandra service named
   `/prod/cassandra`

   ```bash
   ./create_service_diagnostics_bundle.sh --package-name=cassandra --service-name=/prod/cassandra
   ```

On the first run the script might take a few minutes to start because it
downloads a Docker image. After the image is downloaded subsequent runs start
instantly.

When the script runs you should see something like:
```
$ ./create_service_diagnostics_bundle.sh --package-name=cassandra --service-name=/prod/cassandra

Will create bundle for:
  Package:         cassandra
  Package version: 2.3.0-3.0.16
  Service name:    /prod/cassandra
  DC/OS version:   1.11.5
  Cluster URL:     https://my-dcos-cluster.com/

Proceed? [Y/n]:
```

Make sure the information looks correct and press ENTER.

When the script finishes running it will create a directory under your current
`$(pwd)/service-diagnostic-bundles` directory. You can see the bundle directory
name at the end of the script output. E.g.:
```
Created /service-diagnostic-bundles/my-dcos-cluster_prod__cassandra_20180912T142246Z
```

Optionally, zip the bundle directory so that it can be uploaded somewhere:
```
$ cd service-diagnostic-bundles
$ zip -r my-dcos-cluster_prod__cassandra_20180912T142246Z.zip my-dcos-cluster_prod__cassandra_20180912T142246Z
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md)
