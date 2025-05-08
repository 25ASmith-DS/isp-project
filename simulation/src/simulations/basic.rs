use crate::{RobotInstruction as RI, RobotParameters, RobotSimulation, Step};
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

pub struct Basic {
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

impl RobotSimulation<'_> for Basic {
	type DebugInfo = State;

	fn initialize(instructions: &[RI]) -> (Self, Self::DebugInfo)
	where
		Self: Sized,
	{
		let instruction_queue = VecDeque::from_iter(instructions.iter().cloned());
		let state = State::Idle;

		(
			Self {
				instruction_queue,
				state,
			},
			state,
		)
	}

	fn step(
		&mut self,
		_delta_time: std::time::Duration,
		params: &RobotParameters,
	) -> Step<Self::DebugInfo> {
		if let State::Idle = self.state {
			self.state = match self.instruction_queue.pop_front() {
				Some(RI::BladeOff) => State::SetBlade(false),
				Some(RI::BladeOn) => State::SetBlade(true),
				Some(RI::GotoPoint(x, y)) => State::TargetPoint(x, y),
				None => {
					return Step {
						end: true,
						debug: self.state,
					}
				}
			};
		}

		params.motor_left.set(1.0);
		params.motor_right.set(0.5);

		Step {
			end: false,
			debug: self.state,
		}
	}
}
