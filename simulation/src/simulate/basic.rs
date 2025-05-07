use crate::{RobotInstruction as RI, Simulation};
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

use super::{RobotParameters, StepReturn};

pub struct Basic {
	instruction_queue: VecDeque<RI>,
	state: State,
}

#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub enum State {
	#[default]
	Idle,
	SetBlade(bool),
	TargetPoint(f64, f64),
}

impl Simulation<'_> for Basic {
	type DebugInfo = State;

	fn initialize(instructions: super::SimulationInstructions<'_>) -> (Self, Self::DebugInfo)
	where
		Self: Sized,
	{
		let instruction_queue = VecDeque::from_iter(instructions.points.iter().cloned());
		let state = State::Idle;

		(
			Self {
				instruction_queue,
				state: state.clone(),
			},
			state,
		)
	}

	fn step(
		&mut self,
		delta_time: std::time::Duration,
		params: &RobotParameters,
	) -> (super::StepReturn, Self::DebugInfo) {
		if let State::Idle = self.state {
			self.state = match self.instruction_queue.pop_front() {
				Some(RI::BladeOff) => State::SetBlade(false),
				Some(RI::BladeOn) => State::SetBlade(true),
				Some(RI::GotoPoint(x, y)) => State::TargetPoint(x, y),
				None => return (StepReturn::End, State::Idle),
			};
		}

        params.motor_left.set(1.0);
        params.motor_right.set(0.5);

		(StepReturn::None, self.state.clone())
	}
}
