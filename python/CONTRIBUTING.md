# Development

The dcos-commons repository is used as git submodule. The script depends on its
testing library.

## Cloning the repository

```
git clone --recurse-submodules git@github.com:mesosphere/dcos-sdk-service-diagnostics.git
```

## Working with the shell script
The `./create_service_diagnostics_bundle.sh` script runs a Python script in a
Docker container.

To make it to pick up local changes made to Python modules just run the
repository script:

1. `cd` to your dcos-sdk-service-diagnostics repository python directory

```bash
cd /path/to/dcos-sdk-service-diagnostics/python
```

1. Make changes to Python modules under
   `/path/to/dcos-sdk-service-diagnostics/python` (and
   `/path/to/dcos-sdk-service-diagnostics/python/dcos-commons/testing` when
   necessary)

1. Run repository script

```bash
./create_service_diagnostics_bundle.sh --package-name=cassandra --service-name=/prod/cassandra
```

## Releasing a new version

Requires AWS S3 credentials.

1. Push PR with changes to diagnostics code

1. Wait for PR to be merged to master

1. Push a new PR with a `VERSION` bump in
   `create_service_diagnostics_bundle.sh` and a new
   `CHANGELOG.md` entry

   `create_service_diagnostics_bundle.sh`:
   ```bash
   readonly VERSION='vx.y.z'
   ```

   `CHANGELOG.md`:
   ```markdown
   ## vx.y.z (YYYY-MM-DD) - Release title
   ### New features
       - Foo. (commit URL)
       - Bar. (commit URL)
   ### Bug fixes
       - Baz. (commit URL)
       - Qux. (commit URL)
   ### Improvements
       - Quux. (commit URL)
       - Quuz. (commit URL)
   ```

1. Wait for PR to be merged to master

1. Build and publish Docker image tagged with the desired version

   - With the [Jenkins job](https://jenkins.mesosphere.com/service/jenkins/view/Infinity/job/infinity-tools/job/release-tools/job/build-docker-image)

     Make sure to set `IMAGE_TAG` correctly. For example, if `VERSION` is
     `v0.3.1`, `IMAGE_TAG` should be `v0.3.1`.

     | Parameter          | Value                        |
     | ------------------ | ---------------------------- |
     | `DOCKER_FILE_PATH` | python/Dockerfile            |
     | `DOCKER_ORG`       | mesosphere                   |
     | `IMAGE_TAG`        | `$VERSION`            |
     | `IMAGE_NAME`       | dcos-sdk-service-diagnostics |
     | `GITHUB_ORG`       | mesosphere                   |
     | `GITHUB_REPO`      | dcos-sdk-service-diagnostics |
     | `GIT_REF`          | master                       |

   - Or manually

     ```bash
     git fetch upstream
     git stash
     git checkout master
     git reset --hard upstream/master
     docker build -t "mesosphere/dcos-sdk-service-diagnostics:${VERSION}" .
     docker push "mesosphere/dcos-sdk-service-diagnostics:${VERSION}"
     git checkout -
     git stash pop
     ```

1. Publish shell script (which will use the Docker image tagged with the same version)

   1. Version bucket

      ```bash
      aws s3 cp \
        --acl=public-read \
        ./create_service_diagnostics_bundle.sh \
        "s3://infinity-artifacts/dcos-commons/diagnostics/${VERSION}/create_service_diagnostics_bundle.sh"
      ```

   1. Latest bucket

      ```bash
      aws s3 cp \
        --acl=public-read \
        ./create_service_diagnostics_bundle.sh \
        "s3://infinity-artifacts/dcos-commons/diagnostics/latest/create_service_diagnostics_bundle.sh"
      ```