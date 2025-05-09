use serde::{Deserialize, Serialize};

#[derive(Debug, Default, Serialize, Deserialize, Clone)]
pub struct DebugInfo {
	pub messages: Vec<String>,
	pub renderables: Vec<String>,
}

pub mod renderables {
	pub fn circle(center: (f64, f64), radius: f64, color: (u8, u8, u8)) -> String {
		format!("Circle({center:?}, {radius}, {color:?})")
	}
	pub fn line(p1: (f64, f64), p2: (f64, f64), width: f64, color: (u8, u8, u8)) -> String {
		format!("Line({p1:?}, {p2:?}, {width}, {color:?})")
	}
}
