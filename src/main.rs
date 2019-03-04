
mod cli_command;
mod errors;

use structopt::StructOpt;
use std::path::PathBuf;

use cli_command::Cli;
use errors::DiagError;

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

fn main() -> Result<(), DiagError> {
    let args = Args::from_args();

    preflight_checks(args)
}


fn preflight_checks(args: Args) -> Result<(), DiagError> {
    let cli = Cli::new(&args.cli_path);

    authenticated_to_cluster(&cli)?;

    let cluster = cli.attached_cluster()?;

    let (package_name, package_version) = match cli.marathon_app(&args.service_name) {
        Ok(app) => {
            let name = match app.labels.get("DCOS_PACKAGE_NAME") {
                Some(n) => n.clone(),
                None => return Err(DiagError::custom("Marathon app def missing DCOS_PACKAGE_NAME")),
            };
            let version = match app.labels.get("DCOS_PACKAGE_VERSION") {
                Some(n) => n.clone(),
                None => return Err(DiagError::custom("Marathon app def missing DCOS_PACKAGE_VERSION")),
            };
            (name, version)
        },
        Err(_err) => {
            (args.package_name.clone(), "n/a".to_owned())
        },
    };

    if args.package_name != package_name {
        let msg = format!("Given package name {} does not match found name {}", args.package_name, package_name);
        return Err(DiagError::custom(&msg))
    }

    Ok(())
}

fn authenticated_to_cluster(cli: &Cli) -> Result<(), DiagError> {
    let output = cli.run(&["service"])?;

    if !output.success() {
        return Err(DiagError::custom(&output.stderr_str()?))
    }

    Ok(())
}
