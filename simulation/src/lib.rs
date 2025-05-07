pub mod util;
pub mod simulate;


use serde::{Deserialize, Serialize};
pub use simulate::{SimulationState, Simulation};

/// The external file format, represented by the rust
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RobotInstructions {
    pub points: Box<[RobotInstruction]>,
}
impl From<Vec<RobotInstruction>> for RobotInstructions {
    fn from(value: Vec<RobotInstruction>) -> Self {
        Self {
            points: value.into(),
        }
    }
}


#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub enum RobotInstruction {
    BladeOn,
    BladeOff,
    GotoPoint(f64, f64),
}
