# CHANGELOG

## v0.3.2 (2019-07-24)

### Improvements
   - Allow sorting of tasks directories fetched by service diagnostic bundle.
   ([PR 1](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/4))
   ([PR 2](https://github.com/mesosphere/dcos-sdk-service-diagnostics/pull/6))

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
