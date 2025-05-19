use isp_sim::{run_simulation, SimInput};
use std::path::PathBuf;

#[derive(clap::Parser, Debug)]
struct Args {
	#[arg(long)]
	input: Option<PathBuf>,
	#[arg(long)]
	output: Option<PathBuf>,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
	let args: Args = clap::Parser::parse();
	let input_path = args.input.unwrap_or(PathBuf::from("/dev/stdin"));
	let output_path = args.output.unwrap_or(PathBuf::from("/dev/stdout"));

	let raw_input = std::fs::read(input_path)?;
	let sim_input: SimInput = serde_json::from_slice(&raw_input)?;

	let sim_output = run_simulation(sim_input);

	std::fs::write(output_path, &serde_json::to_vec(&sim_output)?)?;

	Ok(())
}
