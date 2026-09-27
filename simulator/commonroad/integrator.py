"""Fixed-step RK4 integration with non-reversing longitudinal policy."""
from .ks_model import KSState, KSControl, derivative, clamp_control
from .vehicle_params import VehicleParams
def _add(s, d, h): return KSState(s.x+h*d.x,s.y+h*d.y,s.steering_angle+h*d.steering_angle,s.velocity+h*d.velocity,s.orientation+h*d.orientation)
def step_rk4(s: KSState, u: KSControl, p: VehicleParams, dt: float) -> KSState:
    u=clamp_control(u,p); k1=derivative(s,u,p); k2=derivative(_add(s,k1,dt/2),u,p); k3=derivative(_add(s,k2,dt/2),u,p); k4=derivative(_add(s,k3,dt),u,p)
    if u.acceleration < 0 and s.velocity > 0 and s.velocity + u.acceleration * dt < 0:
        return step_rk4(s, u, p, s.velocity / -u.acceleration)
    out=KSState(s.x+dt*(k1.x+2*k2.x+2*k3.x+k4.x)/6,s.y+dt*(k1.y+2*k2.y+2*k3.y+k4.y)/6,max(p.steering_min,min(p.steering_max,s.steering_angle+dt*(k1.steering_angle+2*k2.steering_angle+2*k3.steering_angle+k4.steering_angle)/6)),max(0.0,s.velocity+dt*(k1.velocity+2*k2.velocity+2*k3.velocity+k4.velocity)/6),s.orientation+dt*(k1.orientation+2*k2.orientation+2*k3.orientation+k4.orientation)/6)
    return out
