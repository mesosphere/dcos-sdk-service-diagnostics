/// Wrapper around calls to the DCOS CLI

use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::error::Error;

use super::errors::CliError;
use super::responses;

#[derive(Debug)]
pub struct Cli {
    path: PathBuf,
}

impl Cli {
    pub fn new(path: &Path) -> Self {
        //TODO: would be useful to check if given path is valid (exists, maybe is executable)
        Cli{
            path: PathBuf::from(path)
        }
    }

    pub fn run(&self, args: &[&str]) -> Result<Output, Box<std::error::Error>> {
        Ok(Command::new(&self.path)
            .args(args)
            .output()?)
    }


    pub fn attached_cluster(&self) -> Result<responses::Cluster, Box<Error>> {
        let output = self.run(&["cluster", "list", "--attached", "--json"])?;
        if output.status.success() {
            // the response is a list of one cluster so we deserialize into a vec then remove the first
            // element to gain ownership of it and return it.
            let mut clusters: Vec<responses::Cluster> = serde_json::from_slice(&output.stdout)?;
            Ok(clusters.remove(0))
        } else {
            Err(Box::new(CliError::NoClusterAttached))
        }
    }
}
