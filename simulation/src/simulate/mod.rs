mod basic;
pub use basic::Basic;

use crate::{RobotInstruction, RobotInstructions};
use serde::{Deserialize, Serialize};
use std::{cell::Cell, f64::consts::TAU, fmt::Debug, time::Duration};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimulationState<D> {
	pub robot_x: f64,
	pub robot_y: f64,
	pub robot_theta: f64,
	pub debug: D,
}

#[derive(Clone, Debug)]
pub struct RobotParameters {
	pub imu: f64,
	pub gps_x: f64,
	pub gps_y: f64,
	pub motor_left: Cell<f64>,
	pub motor_right: Cell<f64>,
}

impl RobotParameters {
	/// Unit: meters
	pub const WHEEL_DISTANCE: f64 = 65.405;
	/// Unit: meters
	pub const WHEEL_RADIUS: f64 = 0.20;
	/// Unit: radians/second
	pub const MAX_MOTOR_SPEED: f64 = 5.0 * TAU; // 300 rpm
}

pub struct SimulationInstructions<'a> {
	pub points: &'a [RobotInstruction],
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum StepReturn {
	#[default]
	None,
	End,
}

pub trait Simulation<'de> {
	type DebugInfo: Serialize + Deserialize<'de> + Clone + Debug;
	fn initialize(instructions: SimulationInstructions<'_>) -> (Self, Self::DebugInfo)
	where
		Self: Sized;
	fn step(
		&mut self,
		delta_time: Duration,
		params: &RobotParameters,
	) -> (StepReturn, Self::DebugInfo);
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub enum SimulationLength {
	Indefinite,
	Timed(Duration),
	Steps(usize),
}

pub fn run_simulation<'de, S: Simulation<'de>>(
	instructions: RobotInstructions,
	length: SimulationLength,
	dt: Duration,
) -> Vec<SimulationState<S::DebugInfo>> {
	let sim_instructions = SimulationInstructions {
		points: &instructions.points,
	};
	let (mut sim, debug) = S::initialize(sim_instructions);

	let mut states = Vec::new();
	let mut state = SimulationState {
		debug,
		robot_x: 0.0,
		robot_y: 0.0,
		robot_theta: 0.0,
	};
	states.push(state.clone());

	let steps = match length {
		SimulationLength::Indefinite => None,
		SimulationLength::Timed(length) => {
			Some((length.as_secs_f64() / dt.as_secs_f64()).ceil() as usize)
		}
		SimulationLength::Steps(n) => Some(n),
	};

	let in_out = RobotParameters {
		imu: 0.0,
		gps_x: 0.0,
		gps_y: 0.0,
		motor_left: Cell::default(),
		motor_right: Cell::default(),
	};

	let mut step_count = 0;
	'l: loop {
		// run simulation code
		let ret = sim.step(dt, &in_out);

		// update simulation state
		let r = RobotParameters::WHEEL_RADIUS;
		let s = RobotParameters::WHEEL_DISTANCE;
		let phi_l = in_out.motor_left.get() * RobotParameters::MAX_MOTOR_SPEED;
		let phi_r = in_out.motor_right.get() * RobotParameters::MAX_MOTOR_SPEED;
		let theta = in_out.imu;

		let dx_dt = (r * theta.cos() / 2.0) * (phi_l + phi_r);
		let dy_dt = (r * theta.sin() / 2.0) * (phi_l + phi_r);
		let dtheta_dt = (r / s) * (phi_r - phi_l);

		state.robot_x += dx_dt * dt.as_secs_f64();
		state.robot_y += dy_dt * dt.as_secs_f64();
		state.robot_theta += dtheta_dt * dt.as_secs_f64();

		// store state
		states.push(state.clone());

		// check for end condition
		if match steps {
			Some(s) => {
				step_count += 1;
				step_count >= s
			}
			None => ret.0 == StepReturn::End,
		} {
			break 'l;
		}
	}

	states
}
