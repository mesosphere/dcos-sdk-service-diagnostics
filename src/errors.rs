
use std::error::Error;
use std::fmt;

use super::cli_command::errors::CliError;

// Not yet sure what kinds of errors this will have.
// For now, just give it a generic error that wraps around the real one.
#[derive(Debug)]
pub enum DiagError {
    WrappedError(Box<Error>),
    StringError(String),
}

impl Error for DiagError {}

impl fmt::Display for DiagError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        use DiagError::*;
        match self {
            WrappedError(err) => write!(f, "error: {}", err),
            StringError(msg) => write!(f, "error: {}", msg),
        }
    }
}

impl From<Box<dyn Error>> for DiagError {
    fn from(err: Box<dyn Error>) -> Self {
        DiagError::WrappedError(err)
    }
}

impl From<CliError> for DiagError {
    fn from(err: CliError) -> Self {
        DiagError::WrappedError(Box::new(err))
    }
}

impl DiagError {
    pub fn custom(msg: &str) -> Self {
        DiagError::StringError(msg.to_owned())
    }
}
