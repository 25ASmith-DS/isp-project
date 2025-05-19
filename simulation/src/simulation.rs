use crate::{
	debug::{renderables::line, DebugInfo},
	signed_angle_difference,
	util::cubic_bezier,
	RobotInstruction as RI, RobotParameters, Step,
};
use serde::{Deserialize, Serialize};
use std::{collections::VecDeque, f64::consts::PI};

pub struct RobotSimulation {
	instruction_queue: VecDeque<RI>,
	state: RobotState,
	steps_since_idle: usize,
}

#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub enum RobotState {
	#[default]
	Idle,
	SetBlade(bool),
	GotoPoints(VecDeque<(f64, f64)>),
}

impl RobotSimulation {
	const BEZIER_STEPS: usize = 100;

	pub fn initialize(instructions: &[RI]) -> (Self, DebugInfo) {
		let mut debug = DebugInfo::default();
		let instruction_queue = VecDeque::from_iter(instructions.iter().cloned());
		let state = RobotState::Idle;
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

	pub fn step(&mut self, _delta_time: std::time::Duration, params: &RobotParameters) -> Step {
		let mut debug = DebugInfo::default();

		if let RobotState::Idle = self.state {
			self.steps_since_idle = 0;

			params.motor_left.set(0.0);
			params.motor_right.set(0.0);

			let instruction = self.instruction_queue.pop_front();
			self.state = match instruction {
				Some(RI::BladeOff) => RobotState::SetBlade(false),
				Some(RI::BladeOn) => RobotState::SetBlade(true),
				Some(RI::GotoPoint(x, y)) => RobotState::GotoPoints(vec![(x, y)].into()),
				Some(RI::Line { start, end }) => RobotState::GotoPoints(vec![start, end].into()),
				Some(RI::CubicBezier { p0, p1, p2, p3 }) => RobotState::GotoPoints(
					(0..Self::BEZIER_STEPS)
						.map(|n| n as f64 / Self::BEZIER_STEPS as f64)
						.map(|t| cubic_bezier(p0, p1, p2, p3, t))
						.collect(),
				),
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

		match &mut self.state {
			RobotState::Idle => unreachable!(),
			RobotState::SetBlade(b) => {
				params.blade_on.set(*b);
				self.state = RobotState::Idle;
			}
			RobotState::GotoPoints(points) => 'gp: {
				if points.is_empty() {
					self.state = RobotState::Idle;
					break 'gp;
				}

				let (x, y) = points[0];
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

					params
						.motor_right
						.set(error_angle * correction_factor + power);
					params
						.motor_left
						.set(-error_angle * correction_factor + power);
				}

				let distance_threshold = 0.1;
				if distance < distance_threshold {
					points.pop_front();
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
				debug.messages.push(format!(
					"Left Motor Power: {:+5.2}",
					params.motor_left.get()
				));
				debug.messages.push(format!(
					"Right Motor Power: {:+5.2}",
					params.motor_right.get()
				));
			}
		};

		Step { end: false, debug }
	}
}
