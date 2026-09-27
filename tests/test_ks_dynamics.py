from math import isclose, pi
from simulator.commonroad.vehicle_params import vehicle_params_v1
from simulator.commonroad.ks_model import KSState, KSControl, clamp_control
from simulator.commonroad.integrator import integrate_step, step_rk4

P=vehicle_params_v1(); DT=.05
def run(s,u,n):
    out=[s]
    for _ in range(n): out.append(step_rk4(out[-1],u,P,DT))
    return out
def test_vehicle_1_frozen_values():
    expected_wheelbase=.88392+1.50876
    assert all(isclose(x,y,rel_tol=1e-12,abs_tol=1e-12) for x,y in zip((P.length,P.width,P.a,P.b,P.wheelbase),(4.298,1.674,.88392,1.50876,expected_wheelbase)))
    assert (P.steering_min,P.steering_max,P.steering_rate_min,P.steering_rate_max,P.acceleration_abs_limit)==(-.91,.91,-.4,.4,11.5)
def test_stationary_and_straight():
    assert run(KSState(0,0,0,0,0),KSControl(0,0),100)[-1]==KSState(0,0,0,0,0)
    s=run(KSState(0,0,0,10,0),KSControl(0,0),40)[-1]; assert abs(s.x-20)<1e-10 and s.y==0 and s.velocity==10
def test_orientation_and_constraints():
    s=run(KSState(0,0,0,10,pi/2),KSControl(0,0),40)[-1]; assert abs(s.x)<1e-10 and abs(s.y-20)<1e-10
    assert clamp_control(KSControl(1,20),P)==KSControl(.4,11.5)
def test_a2_stop_matches_analytic_and_is_deterministic():
    u=30/3.6; xs=run(KSState(0,0,0,u,0),KSControl(0,-7),30); stop=next(s for s in xs if s.velocity==0)
    assert abs(stop.x-u*u/14)<.02
    assert all(b.velocity<=a.velocity for a,b in zip(xs,xs[1:]))
    assert [s.x for s in xs]==[s.x for s in run(KSState(0,0,0,u,0),KSControl(0,-7),30)]
def test_fractional_stop_event_is_nonrecursive_and_exact():
    s=KSState(0,0,0,17/60,0); r=integrate_step(s,KSControl(0,-7),P,.05)
    assert r.stop_event_time_s == 17/420
    assert r.state.velocity == 0 and isclose(r.state.x, s.velocity*s.velocity/14,abs_tol=1e-12)
    assert step_rk4(r.state,KSControl(0,-7),P,.05) == r.state
