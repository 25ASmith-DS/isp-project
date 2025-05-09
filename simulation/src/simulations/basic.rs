use crate::{
	debug::{renderables::line, DebugInfo},
	RobotInstruction as RI, RobotParameters, RobotSimulation, Step,
};
use serde::{Deserialize, Serialize};
use std::{collections::VecDeque, f64::consts::PI};

pub struct BasicGoto {
	instruction_queue: VecDeque<RI>,
	state: State,
}

#[derive(Debug, Default, Clone, Copy, Serialize, Deserialize)]
pub enum State {
	#[default]
	Idle,
	SetBlade(bool),
	TargetPoint(f64, f64),
}

impl RobotSimulation for BasicGoto {
	fn initialize(instructions: &[RI]) -> (Self, DebugInfo)
	where
		Self: Sized,
	{
		let mut debug = DebugInfo::default();
		let instruction_queue = VecDeque::from_iter(instructions.iter().cloned());
		let state = State::Idle;

		debug.messages.push("Robot Initialized".to_string());
		(
			Self {
				instruction_queue,
				state,
			},
			debug,
		)
	}

	fn step(&mut self, _delta_time: std::time::Duration, params: &RobotParameters) -> Step {
		let mut debug = DebugInfo::default();

		if let State::Idle = self.state {
			params.motor_left.set(0.0);
			params.motor_right.set(0.0);

			let instruction = self.instruction_queue.pop_front();
			self.state = match instruction {
				Some(RI::BladeOff) => State::SetBlade(false),
				Some(RI::BladeOn) => State::SetBlade(true),
				Some(RI::GotoPoint(x, y)) => State::TargetPoint(x, y),
				None => {
					debug.messages.push("No instructions remaining".to_string());
					return Step { end: true, debug };
				}
			};
		}

		self.state = match self.state {
			State::Idle => unreachable!(),
			State::SetBlade(b) => {
				params.blade_on.set(b);
				State::Idle
			}
			State::TargetPoint(x, y) => {
				let (bot_x, bot_y, bot_angle) = (params.gps_x, params.gps_y, params.imu);
				let (distance, angle) = {
					let dx = x - bot_x;
					let dy = y - bot_y;
					((dx * dx + dy * dy).sqrt(), dy.atan2(dx))
				};
				let error_angle = angle - bot_angle;

				debug.renderables.push(line((x, y), (bot_x, bot_y), 4.0, (255, 0, 0)));

				debug
					.messages
					.push(format!("Robot Position: ({:.3}, {:.3})", bot_x, bot_y));
				debug
					.messages
					.push(format!("Target point: ({:.2}, {:.2})", x, y));
				debug
					.messages
					.push(format!("Distance to target: {distance:.4}"));

				let ten_degrees = PI / 18.0;
				if error_angle.abs() > ten_degrees {
					let power = error_angle.signum() * error_angle.abs().powf(0.7);
					params.motor_right.set(power);
					params.motor_left.set(-power);
				} else {
					let power = distance.min(1.0);
					params.motor_right.set(error_angle + power);
					params.motor_left.set(-error_angle + power);
				}

				if distance < 0.5 {
					State::Idle
				} else {
					State::TargetPoint(x, y)
				}
			}
		};

		Step { end: false, debug }
	}
}
