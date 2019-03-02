/// Wrapper around calls to the DCOS CLI

use failure::Error;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::io;

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

    pub fn run(&self, args: &[&str]) -> Result<Output, io::Error> {
        Command::new(&self.path)
            .args(args)
            .output()
    }
}
