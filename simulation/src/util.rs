use std::cmp::Ordering;

pub fn clamp<T: PartialOrd>(x: T, (min, max): (T, T)) -> T {
	if x.partial_cmp(&min).is_some_and(|ord| ord == Ordering::Less) {
		min
	} else if x
		.partial_cmp(&max)
		.is_some_and(|ord| ord == Ordering::Greater)
	{
		max
	} else {
		x
	}
}

#[inline]
pub fn lerp(t: f64, (min, max): (f64, f64)) -> f64 {
	t * (max - min) + min
}
#[inline]
pub fn invlerp(t: f64, (min, max): (f64, f64)) -> f64 {
	(t - min) / (max - min)
}
pub fn map(t: f64, i: (f64, f64), o: (f64, f64)) -> f64 {
	lerp(invlerp(t, i), o)
}

#[inline]
pub fn signed_angle_difference(source: f64, target: f64) -> f64 {
	use std::f64::consts::PI;
	(target - source + PI).rem_euclid(2.0 * PI) - PI
}

pub fn cubic_bezier(
	p0: (f64, f64),
	p1: (f64, f64),
	p2: (f64, f64),
	p3: (f64, f64),
	t: f64,
) -> (f64, f64) {
	let o = 1.0 - t;
	(
		o * o * o * p0.0 + 3.0 * o * o * t * p1.0 + 3.0 * o * t * t * p2.0 + t * t * t * p3.0,
		o * o * o * p0.1 + 3.0 * o * o * t * p1.1 + 3.0 * o * t * t * p2.1 + t * t * t * p3.1,
	)
}
