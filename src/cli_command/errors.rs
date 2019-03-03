
use std::error::Error;
use std::fmt;

#[derive(Debug)]
pub enum CliError {
    NoClusterAttached,
    CliCallError(String),
    InvalidOutputError,
}

impl Error for CliError {}

impl fmt::Display for CliError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        use CliError::*;
        match self {
            NoClusterAttached => write!(f, "no cluster attached"),
            CliCallError(msg) => write!(f, "error from DCOS CLI call: {}", msg),
            InvalidOutputError => write!(f, "some ouput from DCOS CLI was not valid utf8"),
        }
    }
}