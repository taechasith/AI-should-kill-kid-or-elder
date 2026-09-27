"""Transparent Kinematic Single-Track state equations."""
from dataclasses import dataclass
from math import cos, sin, tan
from .vehicle_params import VehicleParams

@dataclass(frozen=True)
class KSState:
    x: float; y: float; steering_angle: float; velocity: float; orientation: float
@dataclass(frozen=True)
class KSControl:
    steering_rate: float; acceleration: float

def clamp_control(control: KSControl, p: VehicleParams) -> KSControl:
    return KSControl(max(p.steering_rate_min, min(p.steering_rate_max, control.steering_rate)), max(-p.acceleration_abs_limit, min(p.acceleration_abs_limit, control.acceleration)))
def derivative(s: KSState, u: KSControl, p: VehicleParams) -> KSState:
    return KSState(s.velocity*cos(s.orientation), s.velocity*sin(s.orientation), u.steering_rate, u.acceleration if s.velocity > 0 or u.acceleration > 0 else 0.0, s.velocity*tan(s.steering_angle)/p.wheelbase)
