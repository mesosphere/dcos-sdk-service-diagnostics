# CLI commands for CI process

## Usage

### Gather diagnostics

Gather DC/OS services diagnostic from specific cluster by running  following command:

```bash
$ ci_cli.py --type=diagnostic <service> [<service> ...]
```

- *service* is DC/OS service name, e.g., `cassandra`, `elastic` and `hdfs`


### Install data services (`install_data_services.sh`)

Bulk installation required for DC/OS services in parallel.

```bash
$ install_data_services.sh <service> [<service> ...]
```
- *service* is DC/OS service name, e.g., _cassandra_, _elastic_ and _hdfs_

### Setup DC/OS (`setup_dcos_cli.sh`)

Set up the CLI to communicate with a DC/OS cluster.

```bash
$ setup_dcos_cli.sh <username> <password>
```

- *username* is the username for login.
- *password* is the password in the command line (insecure)

> NOTE: Make sure that the CLUSTER_URL environment variable was exported
>
> ```bash
> $ export CLUSTER_URL=http://<url>
> ```
