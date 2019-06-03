# CHANGELOG

## v0.3.1 (2019-06-18)

   - the diagnostics tools is extracted from `dcos-sdk-service-diagnostics` to separate git repo.
   - the tools is packed into own docker image now, which is based on vanilla python3.7-alpine3.9 image. 
     ([commit](https://github.com/mesosphere/dcos-sdk-service-diagnostics/commit/8f49db7d9606f8b6edcd7969616c5b7f2b882ca4))

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
