# using equation theta_2 = -K (theta - theta_ref) - B (theta_dot - theta_1_ref)
# theta_dot = theta_(t+1) - theta_t
from odometry_guided_feedback import convert_PWM_to_vel, convert_vel_to_PWM, convert_delta_PWM_to_vel
from config import *
import numpy as np
from collections import deque
from camera import Camera
from time import sleep


cam = Camera()
sleep(2)

previous_thetas = deque()
previous_dts = deque()
stopping = False


# takes
#   PWM_l_prev: float,
#   PWM_r_prev: float,
#   lane_error_pix: int,
#   time since last call, dt: float,
#   stop_marker_seen: bool
# returns
#   (PWM_l, PWM_r): (float, float)
def get_PWMs_from_visual(lane_error_pix, dt, PWM_l_prev, PWM_r_prev):

    # TODO: translate pixel error from center of bot to center of lane to theta
    # tan(theta) = o/a = lane error in centimeters / dist from ROI center to bot center
    # theta = arctan(lane error in centimeters / dist from ROI center to bot center)
    lane_error_cm = lane_error_pix / PIX_PER_CM
    theta = np.arctan2(lane_error_cm, DIST_TO_ROI_CM)

    # TODO: store past thetas and calculate moving average theta_dot
    previous_thetas.append(theta)
    previous_dts.append(dt)
    if len(previous_thetas) > 1:
        previous_thetas.popleft()
        previous_dts.popleft()
    avg_theta = sum(previous_thetas) / len(previous_thetas)
    # TODO: better calculation: computer theta vel for each dt and then average
    theta_velocity = avg_theta / sum(previous_dts)

    # TODO: use equation to determine delta_PWM (delta_PWM ~ theta_acceleration)
    delta_PWM = - K * theta - B * theta_velocity

    # handle PWM <==> velocity stuff
    vel_l_prev = convert_PWM_to_vel(PWM_l_prev)
    vel_r_prev = convert_PWM_to_vel(PWM_r_prev)
    delta_vel = convert_delta_PWM_to_vel(delta_PWM)

    # TODO: return PWMs
    vel_l_new = vel_l_prev + delta_vel
    vel_r_new = vel_r_prev - delta_vel
    PWM_l = convert_vel_to_PWM(vel_l_new)
    PWM_r = convert_vel_to_PWM(vel_r_new)

    # TODO: what is the right way to clamp these values?
    PWM_l = np.clip(PWM_l, -400, 400)
    PWM_r = np.clip(PWM_r, -400, 400)

    if DEBUG_INFO_ON:
        print("Visual Controller")
        print("{:>22} : {}".format("lane_error_pix", lane_error_pix))
        print("{:>22} : {}".format("dt", dt))
        print("{:>22} : {}".format("PWM_l_prev", PWM_l_prev))
        print("{:>22} : {}".format("PWM_r_prev", PWM_r_prev))
        print("{:>22} : {}".format("delta_PWM", delta_PWM))
        print("{:>22} : {}".format("vel_l_prev", vel_l_prev))
        print("{:>22} : {}".format("vel_r_prev", vel_r_prev))
        print("{:>22} : {}".format("delta_vel", delta_vel))
        print("{:>22} : {}".format("vel_l_new", vel_l_new))
        print("{:>22} : {}".format("vel_r_new", vel_r_new))
        print("{:>22} : {}".format("PWM_l", PWM_l))
        print("{:>22} : {}".format("PWM_r", PWM_r))
        print("="*30)
        
    return PWM_l, PWM_r


def clear_visual_globals():
    previous_thetas.clear()
    previous_dts.clear()


def compute_motor_values(t, delta_t, left_encoder, right_encoder, delta_left_encoder, delta_right_encoder, left_motor_prev, right_motor_prev):
    PWM_l, PWM_r = 0, 0
    lane_error_pix, stop_marker_seen = cam.get_error()

    PWM_l_prev, PWM_r_prev = left_motor_prev, right_motor_prev

    if stop_marker_seen or stopping:
        if DEBUG_INFO_ON:
            print("Visual compute motor values")
            print("{:>22} : {}".format("lane_error_pix", lane_error_pix))
            print("{:>22} : {}".format("dt", delta_t))
            print("{:>22} : {}".format("stop_marker_seen", stop_marker_seen))
            print("{:>22} : {}".format("PWM_l_prev", PWM_l_prev))
            print("{:>22} : {}".format("PWM_r_prev", PWM_r_prev))
            print("{:>22} : {}".format("PWM_l", PWM_l))
            print("{:>22} : {}".format("PWM_r", PWM_r))
            print("="*30)

        PWM_l = convert_vel_to_PWM(convert_PWM_to_vel(PWM_l_prev) / 2)
        PWM_r = convert_vel_to_PWM(convert_PWM_to_vel(PWM_r_prev) / 2)

        return PWM_l, PWM_r

    PWM_l, PWM_r = get_PWMs_from_visual(lane_error_pix, delta_t, PWM_l_prev, PWM_r_prev)

    return PWM_l, PWM_r


def test():
    return get_PWMs_from_visual(20, 0.1, 150, 150)
