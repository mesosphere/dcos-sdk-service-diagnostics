
use std::error::Error;
use std::fmt;

#[derive(Debug)]
pub enum CliError {
    NoClusterAttached,
}

impl Error for CliError {}

impl fmt::Display for CliError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        use CliError::*;
        match self {
            NoClusterAttached => write!(f, "no cluster attached"),
        }
    }
}