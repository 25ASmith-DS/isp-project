use std::{fs, io, time::Duration};

use isp_sim::{
	run_simulation, simulations::Basic, RobotInstruction as RI, RobotSimulation, SimInput,
	SimulationLength,
};

fn main() -> Result<(), Box<dyn std::error::Error>> {
	let wheel_distance = 1.28;
	let wheel_radius = 0.2;
	let max_motor_speed = 5.0 * std::f64::consts::TAU;

	create_test(
		"basic_goto",
		SimInput {
			instructions: vec![
				RI::GotoPoint(5.0, 5.0),
				RI::BladeOn,
				RI::GotoPoint(-5.0, 15.0),
				RI::BladeOff,
				RI::GotoPoint(0.0, 0.0),
			],
			sim_length: SimulationLength::Steps(100),
			delta_time: Duration::from_millis(10),
			wheel_distance,
			wheel_radius,
			max_motor_speed,
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

fn run_test<'de, S: RobotSimulation<'de>>(name: &str) -> io::Result<()> {
	let filename = format!("tests/{name}.json");
	let input: SimInput = serde_json::from_slice(&fs::read(filename)?)?;
	let output = run_simulation::<S>(input);
	let filename = format!("tests/{name}.sim");
	fs::write(filename, serde_json::to_vec_pretty(&output)?)?;

	Ok(())
}
