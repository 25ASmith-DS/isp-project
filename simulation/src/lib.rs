pub mod robot;
pub mod simulation;
pub mod util;
pub mod debug;

use debug::DebugInfo;
pub use robot::{RobotInstruction, RobotParameters};
use simulation::RobotSimulation;
pub use util::*;

use serde::{Deserialize, Serialize};
use std::{cell::Cell, fmt::Debug, time::Duration};

#[derive(Debug, Serialize, Deserialize)]
pub struct SimOutput {
	pub states: Vec<SimulationState>,
	pub delta_time: Duration,
	/// Unit: meters
	pub wheel_distance: f64,
	/// Unit: meters
	pub wheel_radius: f64,
	/// Unit: meters
	pub max_motor_speed: f64,
	/// Unit: meters
	pub blade_radius: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SimInput {
	pub instructions: Vec<RobotInstruction>,
	pub sim_length: SimulationLength,
	pub delta_time: Duration,
	/// Unit: meters
	pub wheel_distance: f64,
	/// Unit: meters
	pub wheel_radius: f64,
	/// Unit: meters
	pub max_motor_speed: f64,
	/// Unit: meters
	pub blade_radius: f64,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub enum SimulationLength {
	Indefinite,
	Timed(Duration),
	Steps(usize),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimulationState {
	pub robot_x: f64,
	pub robot_y: f64,
	pub robot_theta: f64,
    pub blade_on: bool,
	pub debug: DebugInfo,
}

pub struct Step {
	end: bool,
	debug: DebugInfo,
}


pub fn run_simulation(
	SimInput {
		instructions,
		sim_length,
		delta_time: dt,
		wheel_distance,
		wheel_radius,
		max_motor_speed,
        blade_radius,
	}: SimInput,
) -> SimOutput {
	let (mut sim, debug) = RobotSimulation::initialize(&instructions);

	let mut states = Vec::new();
	let mut state = SimulationState {
		debug,
		robot_x: 0.0,
		robot_y: 0.0,
		robot_theta: 0.0,
        blade_on: false,
	};
	states.push(state.clone());

	let steps = match sim_length {
		SimulationLength::Indefinite => None,
		SimulationLength::Timed(length) => {
			Some((length.as_secs_f64() / dt.as_secs_f64()).ceil() as usize)
		}
		SimulationLength::Steps(n) => Some(n),
	};

	let mut in_out = RobotParameters {
		imu: state.robot_theta,
		gps_x: state.robot_x,
		gps_y: state.robot_y,
		motor_left: Cell::default(),
		motor_right: Cell::default(),
		blade_on: Cell::new(state.blade_on),
		wheel_distance,
		wheel_radius,
		max_motor_speed,
	};

	let mut step_count = 0;
	'l: loop {
		in_out.imu = state.robot_theta;
		in_out.gps_x = state.robot_x;
		in_out.gps_y = state.robot_y;

		// run simulation code
		let Step { end, debug } = sim.step(dt, &in_out);
		in_out
			.motor_left
			.set(clamp(in_out.motor_left.get(), (-1.0, 1.0)));
		in_out
			.motor_right
			.set(clamp(in_out.motor_right.get(), (-1.0, 1.0)));

		// update simulation state
		let r = in_out.wheel_radius;
		let s = in_out.wheel_distance;
		let phi_l = in_out.motor_left.get() * in_out.max_motor_speed;
		let phi_r = in_out.motor_right.get() * in_out.max_motor_speed;
		let theta = in_out.imu;

		let dx_dt = (r * theta.cos() / 2.0) * (phi_l + phi_r);
		let dy_dt = (r * theta.sin() / 2.0) * (phi_l + phi_r);
		let dtheta_dt = (r / s) * (phi_r - phi_l);

		state.robot_x += dx_dt * dt.as_secs_f64();
		state.robot_y += dy_dt * dt.as_secs_f64();
		state.robot_theta += dtheta_dt * dt.as_secs_f64();

		state.blade_on = in_out.blade_on.get();

		state.debug = debug;

		// store state
		states.push(state.clone());

		// check for end condition
		if match steps {
			Some(s) => {
				step_count += 1;
				step_count >= s
			}
			None => end,
		} {
			break 'l;
		}
	}

	SimOutput {
		states,
		delta_time: dt,
		wheel_distance,
		wheel_radius,
		max_motor_speed,
        blade_radius,
	}
}
