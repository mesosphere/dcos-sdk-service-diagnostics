
use serde::Deserialize;

use std::process::Output;
use std::collections::HashMap;

use super::errors::CliError;

#[derive(Deserialize, Debug)]
pub struct Cluster {
    attached: bool,
    cluster_id: String,
    name: String,
    status: String,
    url: String,
    version: String
}

#[derive(Deserialize, Debug)]
#[serde(rename_all="camelCase")]
pub struct MarathonApp {
    id: String,
    cmd: String,
    // args: 
    // user
    env: HashMap<String, String>,
    instances: u32,
    cpus: f32,
    mem: u32,
    disk: u32,
    executor: String,
    constraints: Vec<Vec<String>>,
    uris: Vec<String>,
    ports: Vec<u16>,
    require_ports: bool,
    backoff_seconds: u32,
    backoff_factor: f32,
    max_launch_delay_seconds: u32,
    container: String,
    // TODO: not sure if String is the right type
    // health_checks: Vec<String>,

    dependencies: Vec<String>,

    // TODO: this might be a more complex object
    // upgrade_strategy: HashMap<String, u32>,

    pub labels: HashMap<String, String>,

    // accepted_resource_roles: 

    version: String,
    version_info: HashMap<String, String>,

    tasks_staged: u32,
    tasks_runnings: u32,
    tasks_healthy: u32,
    tasks_unhealthy: u32,
    deployments: Vec<HashMap<String, String>>
}

// CliResponse exists to provide some convenience around the fact that Rust's
// Output has stdout and stderr as Vec<u8> which may not convert to a String
// properly so needs extra error handling.
#[derive(Debug)]
pub struct CliResponse {
    inner: Output,
}

impl CliResponse {
    pub fn success(&self) -> bool {
        self.inner.status.success()
    }

    pub fn stderr_str(&self) -> Result<String, CliError> {
        match String::from_utf8(self.inner.stderr.clone()) {
            Ok(s) => Ok(s),
            Err(_err) => Err(CliError::InvalidOutputError)
        }
    }

    pub fn stdout_str(&self) -> Result<String, CliError> {
        match String::from_utf8(self.inner.stdout.clone()) {
            Ok(s) => Ok(s),
            Err(_err) => Err(CliError::InvalidOutputError)
        }
    }

    pub fn stdout(&self) -> &Vec<u8> {
        &self.inner.stdout
    }
}

impl From<Output> for CliResponse {
    fn from(o: Output) -> Self {
        CliResponse{
            inner: o
        }
    }
}
