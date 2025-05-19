use serde::{Deserialize, Serialize};
use std::cell::Cell;

#[derive(Clone, Debug)]
pub struct RobotParameters {
	pub motor_left: Cell<f64>,
	pub motor_right: Cell<f64>,
	pub blade_on: Cell<bool>,
	// Unit: radians
	pub imu: f64,
	// Unit: meters
	pub gps_x: f64,
	/// Unit: meters
	pub gps_y: f64,
	/// Unit: meters
	pub wheel_distance: f64, // 65.405
	/// Unit: meters
	pub wheel_radius: f64, // 0.20
	/// Unit: radians/second
	pub max_motor_speed: f64, // 5.0 * TAU = 300 rpm
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub enum RobotInstruction {
	BladeOn,
	BladeOff,
    GotoPoint(f64, f64),
	Line {
		start: (f64, f64),
		end: (f64, f64),
	},
	CubicBezier {
		p0: (f64, f64),
		p1: (f64, f64),
		p2: (f64, f64),
		p3: (f64, f64),
	},
}
