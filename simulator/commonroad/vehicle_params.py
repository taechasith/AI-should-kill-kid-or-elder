"""Load the frozen official Vehicle 1 parameters."""
from dataclasses import dataclass
from vehiclemodels.parameters_vehicle1 import parameters_vehicle1

@dataclass(frozen=True)
class VehicleParams:
    length: float; width: float; a: float; b: float
    steering_min: float; steering_max: float; steering_rate_min: float; steering_rate_max: float; acceleration_abs_limit: float
    @property
    def wheelbase(self): return self.a + self.b

def vehicle_params_v1() -> VehicleParams:
    p = parameters_vehicle1()
    return VehicleParams(p.l, p.w, p.a, p.b, p.steering.min, p.steering.max, p.steering.v_min, p.steering.v_max, p.longitudinal.a_max)
