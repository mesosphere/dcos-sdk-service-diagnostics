
mod cli_command;

use structopt::StructOpt;
use std::path::PathBuf;
use std::error::Error;
use cli_command::Cli;

#[derive(Debug, StructOpt)]
#[structopt(name="service-diagnostics")]
struct Args {

    #[structopt(long="package-name",
                help="The package name for the service to create the bundle for")]
    package_name: String,

    #[structopt(long="service-name",
                help="The service name to create the bundle for")]
    service_name: String,

    #[structopt(long="bundles-directory",
                help="The directory where bundles will be written to")]
    bundles_directory: PathBuf,

    #[structopt(long="yes",
                help="Disable interactive mode a assume 'yes' for all prompts")]
    skip_prompt: bool,

    // the Python version depends on calls to the CLI, replicating the necessary
    // functionality in Rust would be good at some point but shelling out is
    // quicker right now so this is a new argument for the path to the CLI.
    #[structopt(long="cli-path",
                help="Path to DCOS CLI (default `dcos`)",
                default_value="dcos")]
    cli_path: PathBuf,
}

fn main() {
    let args = Args::from_args();
    preflight_checks(args).unwrap();
}


fn preflight_checks(args: Args) -> Result<(), Box<Error>> {
    let cli = Cli::new(&args.cli_path);

    authenticated_to_cluster(&cli)?;

    // TODO: get attached cluster
    let cluster = cli.attached_cluster()?;

    // TODO: get information on requested service

    // TODO: check that the package name given matches what the cluster says
    Ok(())
}

fn authenticated_to_cluster(cli: &Cli) -> Result<(), Box<Error>> {
    let output = cli.run(&["service"])?;

    if !output.status.success() {
        // TODO: make this an error instead of a panic
        panic!("{}", String::from_utf8(output.stderr).unwrap());
    }

    Ok(())
}