# CHANGELOG

## v0.5.0 (2019-10-09)

### New features

   - Gather versions of DC/OS cluster and the diagnostics script itself.
   ([PR #17](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/17))

### Improvements
   - Support the `$DCOS_DIR` environment variable.
   ([PR #12](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/12))
   - Make it possible to run the script without a controlling terminal.
   ([PR #13](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/13))
   - Gather more diagnostics when running against an Elastic package.
   ([PR #14](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/14))

## v0.4.0 (2019-08-29)

### New features
   - Introduced support for DC/OS packages whose CLI subcommand names don't match their package names, like "dcos-monitoring".
   ([PR #9](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/9))

### Improvements
   - Improved compatibility with DC/OS clusters by matching the "dcos-cli-core" plugin to the appropriate DC/OS cluster version.
   ([PR #7](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/7))

### Bug fixes
   - Fixed an issue with host arch other than linux x64. ([PR #7](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/7)) ([diff](https://github.com/mesosphere/dcos-sdk-service-diagnostics/blob/0e5bd602203d167628fc2e33fa16817c245a2ad3/python/create_service_diagnostics_bundle.sh#L106-L111))
   - Fixed the docker run command hanging for minutes before showing the script output. ([PR #7](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/7)) ([diff](https://github.com/mesosphere/dcos-sdk-service-diagnostics/blob/0e5bd602203d167628fc2e33fa16817c245a2ad3/python/create_service_diagnostics_bundle.sh#L106-L111))

## v0.3.2 (2019-07-24)

### Improvements
   - Allow sorting of tasks directories fetched by service diagnostic bundle.
   ([PR #4](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/4))
   ([PR #6](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/6))

## v0.3.1 (2019-07-13)

### Improvements
   - The diagnostics tools is extracted from `dcos-commons` into a separate git repo.
   - The tool is packed into own docker image now, which is based on a vanilla python3.7-alpine3.9 image. 
     ([PR](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/3))

## v0.2.1 (2019-01-16) - Snowman

### Bug fixes
   - Don't raise exception when there's a missing agent.
     ([commit](https://github.com/mesosphere/dcos-sdk-service-diagnostics/commit/36df8317c0d462da0f006541ce256f064f717d96))

## v0.2.0 (2019-01-16) - Snowman

### Bug fixes
   - Fixes `IndexError: list index out of range` exception when it can't find an
     active scheduler in the Mesos state
     ([commit](https://github.com/mesosphere/dcos-sdk-service-diagnostics/commit/ddb343271ebdc910d14206bc017118a64e9840a1))

### Improvements
   - Add kafka-specific steps to fetch broker info, and run them for
     confluent-kafka as well
     ([commit](https://github.com/mesosphere/dcos-sdk-service-diagnostics/commit/5da14f92d3fb714c3ecc7fd237f098d1753758de))

## v0.1.0 (2018-10-02) - Initial release
