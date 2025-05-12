use crate::{
	debug::{renderables::line, DebugInfo},
	signed_angle_difference, RobotInstruction as RI, RobotParameters, RobotSimulation, Step,
};
use serde::{Deserialize, Serialize};
use std::{collections::VecDeque, f64::consts::PI};

pub struct BasicGoto {
	instruction_queue: VecDeque<RI>,
	state: State,
	steps_since_idle: usize,
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
		let steps_since_idle = 0;

		debug.messages.push("Robot Initialized".to_string());
		(
			Self {
				instruction_queue,
				state,
				steps_since_idle,
			},
			debug,
		)
	}

	fn step(&mut self, _delta_time: std::time::Duration, params: &RobotParameters) -> Step {
		let mut debug = DebugInfo::default();

		if let State::Idle = self.state {
			self.steps_since_idle = 0;

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
		} else {
			self.steps_since_idle += 1;
		}
		debug
			.messages
			.push(format!("Steps since last idle: {}", self.steps_since_idle));

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
				let error_angle = signed_angle_difference(bot_angle, angle);

				let direction_threshold = 5.0 * (PI / 180.0);
				if error_angle.abs() > direction_threshold {
					let power = error_angle.signum() * error_angle.abs().min(1.0).powf(0.7) / 1.5;
					params.motor_right.set(power);
					params.motor_left.set(-power);
				} else {
					let power = distance.min(2.0) / 2.0;
                    let power = power.sqrt();
                    let correction_factor = 4.0;

					params.motor_right.set(error_angle * correction_factor + power);
					params.motor_left.set(-error_angle * correction_factor + power);
				}

                let distance_threshold = 0.2;
				let next_state = if distance < distance_threshold {
					State::Idle
				} else {
					State::TargetPoint(x, y)
				};

				debug
					.renderables
					.push(line((x, y), (bot_x, bot_y), 4.0, (255, 0, 0)));
				debug
					.messages
					.push(format!("Robot Position: ({:.3}, {:.3})", bot_x, bot_y));
				debug
					.messages
					.push(format!("Robot Angle: {:.1}", bot_angle * 180.0 / PI));
				debug
					.messages
					.push(format!("Target point: ({:.2}, {:.2})", x, y));
				debug
					.messages
					.push(format!("Distance to target: {distance:.4}"));
				debug.messages.push(format!(
					"Angle error to target: {:.1}",
					error_angle * 180.0 / PI
				));
				debug
					.messages
					.push(format!("Left Motor Power: {:+5.2}", params.motor_left.get()));
				debug
					.messages
					.push(format!("Right Motor Power: {:+5.2}", params.motor_right.get()));

				next_state
			}
		};

		Step { end: false, debug }
	}
}
