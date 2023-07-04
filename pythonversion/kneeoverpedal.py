from angles import knee_extension_angle
import numpy as np
## Testing Ergonomics of Knee Over Pedal Spindle
def kops(bike, body):
    """
    Input: bike vector, body vector, crank length
    Output: horizontal offset knee to pedal center at 3 o'clock
    """
    alpha_2 = knee_extension_angle(bike, body, 0, ret_a2=True)
    if alpha_2 is None:
        return None
    upper_leg = body[1, 0]
    seat_x = bike[0, 0]
    crank_len = bike[4, 0]
    return seat_x + upper_leg * np.cos(alpha_2) - crank_len


