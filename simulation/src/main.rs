use std::{fs, io, time::Duration};

use isp_sim::{
	simulate::{run_simulation, Basic, SimulationLength},
	RobotInstruction as RI, RobotInstructions, Simulation, SimulationState,
};
use serde::{Deserialize, Serialize};

fn main() -> Result<(), Box<dyn std::error::Error>> {
	create_test(
		"basic_goto",
		SimInput {
			instructions: RobotInstructions {
				points: vec![
					RI::GotoPoint(5.0, 5.0),
					RI::BladeOn,
					RI::GotoPoint(-5.0, 15.0),
					RI::BladeOff,
					RI::GotoPoint(0.0, 0.0),
				]
				.into(),
			},
			sim_length: SimulationLength::Steps(100),
			delta_time: Duration::from_millis(10),
		},
	)?;
	run_test::<Basic>("basic_goto").unwrap();
	Ok(())
}

fn create_test(name: &str, input: SimInput) -> io::Result<()> {
	let filename = format!("tests/{name}.json");
	let data = serde_json::to_vec_pretty(&input)?;
	fs::write(filename, &data)
}

fn run_test<'de, S: Simulation<'de>>(name: &str) -> io::Result<()> {
	let filename = format!("tests/{name}.json");
	let input: SimInput = serde_json::from_slice(&fs::read(filename)?)?;

	let steps = run_simulation::<S>(input.instructions, input.sim_length, input.delta_time);

	let output: SimOutput<_> = SimOutput {
		steps,
		delta_time: input.delta_time,
	};

	let filename = format!("tests/{name}.sim");
	fs::write(filename, serde_json::to_vec_pretty(&output)?)?;

	Ok(())
}

#[derive(Debug, Serialize, Deserialize)]
struct SimOutput<D> {
	steps: Vec<SimulationState<D>>,
	delta_time: Duration,
}

#[derive(Debug, Serialize, Deserialize)]
struct SimInput {
	instructions: RobotInstructions,
	sim_length: SimulationLength,
	delta_time: Duration,
}
