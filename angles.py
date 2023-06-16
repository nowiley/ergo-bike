import numpy as np
from scipy.stats import norm
from tabulate import tabulate
#from measureml import analyze

# #####
# Bike Ergonomic Angle Fit Calculator
# Input: Vector of bike coordinates (seat and handle bar position) bottom bracket is origin
# Input: Vecor of body dimensions (shoulder height, leg length, upper leg length, arm length)
# Input: use case ie (road, mtb, commuter/comfort)
# Output: Loss = penalize deviations from optimal
######

# FUNCTIONS FOR CALCUATING ANGLES

# dict of dictionaries maping use cases to their respective body angles and variations
# usecase: { name:(mean value, sd) }
USE_DICT = {
    "road": {
        "opt_knee_angle": (37.5, 5),
        "opt_back_angle": (45, 5),
        "opt_awrist_angle": (90, 5),
        "opt_elbow_angle": (160, 10),
        "opt_ankle_angle": (100.0, 5.0),
        "opt_hip_angle_closed": (60, 5),
    },
    "mtb": {
        "opt_knee_angle": (37.5, 2.5),
        "opt_back_angle": (45, 5),
        "opt_elbow_angle": (160, 10),
        "opt_ankle_angle": (100.0, 5.0),
        "opt_hip_angle_closed": (60, 5),
    },
    "tt": {
        "opt_knee_angle": (37.5, 2.5),
        "opt_back_angle": (45, 5),
        "opt_elbow_angle": (160, 10),
        "opt_ankle_angle": (100.0, 5.0),
        "opt_hip_angle_closed": (60, 5),
    },
    "commute": {
        "opt_knee_angle": (37.5, 2.5),
        "opt_back_angle": (45, 5),
        "opt_elbow_angle": (160, 10),
        "opt_ankle_angle": (100.0, 5.0),
        "opt_hip_angle_closed": (60, 5),
    },
}


def knee_extension_angle(bike_vector, body_vector, CA):
    """
    Input:
        bike vector, body vector, crank angle
        np array bike vector:
            [SX, SY, HX, HY, CL]^T
            (seat_x, seat_y, hbar_x, hbar_y, crank len)
        np array body vector:
            [LL, UL, TL, AL, FL, AA]
            (lowleg, upleg, torso len, arm len, foot len, ankl angle)
        CA = crank angle:
            crank angle fom horizontal in radians
        Origin is bottom bracket

    Output:
        Knee extension angle
        OR
        None if not valid coords (i.e. NaA appeared)

    """
    #decomposing body vector
    sq_body = np.square(body_vector)

    LL = body_vector[0, 0]
    UL = body_vector[1, 0]
    TL = body_vector[2, 0]
    AL = body_vector[3, 0]
    FL = body_vector[4, 0]
    AA = body_vector[5, 0]

    LL_s = sq_body[0, 0]
    UL_s = sq_body[1, 0]
    TL_s = sq_body[2, 0]
    AL_s = sq_body[3, 0]
    FL_s = sq_body[4, 0]
    AA_s = sq_body[5, 0]

    # decomposing bike vector
    sq_bike = np.square(bike_vector)

    SX = bike_vector[0, 0]
    SY = bike_vector[1, 0]
    HX = bike_vector[2, 0]
    HY = bike_vector[3, 0]
    CL = bike_vector[4, 0]

    SX_s = sq_bike[0, 0]
    SY_s = sq_bike[1, 0]
    HX_s = sq_bike[2, 0]
    HY_s = sq_bike[3, 0]
    CL_s = sq_bike[4, 0]


    x_1 = np.sqrt(LL_s + FL_s - (2 * LL * FL * np.cos(AA)))


    LX = CL * np.cos(CA) - SX
    LY = SY - CL * np.sin(CA)


    x_2 = np.sqrt((LX**2 + LY**2))


    alpha_1 = np.arccos((x_1**2 - UL_s - x_2**2) / (-2 * UL * x_2))
    if np.isnan(alpha_1):
        return None


    alpha_2 = np.arctan2(LY, LX) - alpha_1


    LLY = LY - UL * np.sin(alpha_2)
    LLX = LX - UL * np.cos(alpha_2)


    alpha_3 = np.arctan2(LLY, LLX) - alpha_2


    alpha_4 = np.arccos((FL_s - LL_s - x_1**2) / (-2 * LL * x_1))
    if np.isnan(alpha_4):
        return None


    return alpha_3 + alpha_4


def back_armpit_angles(bike_vector, body_vector, elbow_angle):
    """
    Input: bike_vector, body_vector, elbow_angle
    Output: back angle, armpit to wrist angle in radians

    np array bike vector:
            [SX, SY, HX, HY, CL]^T
    np array body vector:
            [LL, UL, TL, AL, FL, AA]

    TL = UL
    UA = LL
    La = FL
    AA = ARM Angle
    CL = 0
    hx = -sx
    hy = -sy
    """
    elbow_angle = elbow_angle * (np.pi/180)

    LL = body_vector[0, 0]
    UL = body_vector[1, 0]
    TL = body_vector[2, 0]
    AL = float(body_vector[3, 0])
    FL = body_vector[4, 0]
    AA = float(body_vector[5, 0])

    # decomposing bike vector
    SX = bike_vector[0, 0]
    SY = bike_vector[1, 0]
    HX = bike_vector[2, 0]
    HY = bike_vector[3, 0]
    CL = bike_vector[4, 0]

    #### BACK ANGLE ####
    # Calculating straightline distance between handlebars and seat
    sth_dist = ((HY - SY) ** 2 + (HX - SX) ** 2) ** 0.5

    # Calculating angle offset (horizontal to sth_dist) for torso angle
    sth_ang = np.arctan2((HY - SY), (HX - SX))


    # Uses new dist and law of cosines to find torso angle
    x_1 = (AL / 2) ** 2 + (AL / 2) ** 2 - 2 * (AL / 2) * (AL / 2) * np.cos(elbow_angle)
    tors_ang = np.arccos((TL**2 + sth_dist**2 - x_1) / (2 * TL * sth_dist))
    #if not possible return None
    if np.isnan(tors_ang):
        return (None, None)

    # Adds offset to get back angle with horizontal
    back_angle = tors_ang + sth_ang

    #### ARMPIT TO WRIST ANGLE ####
    armpit_to_wrist = np.arccos((TL**2 + x_1 - sth_dist**2)/ (2 * TL * (x_1**0.5)))

    # return angles in radians
    return (back_angle, armpit_to_wrist)


def deg_to_r(deg):
    return float(deg / 180) * np.pi


def rad_to_d(rad):
    return float(rad * (180 / np.pi))


def prob(mean, sd, value):
    """
    Returns probability of value or larger given mean and sd
    """
    #handle None type values
    if value is None:
      return None

    dist = abs((value - mean))/sd
    return 1 - norm.cdf(dist, loc=0, scale=1)



def prob_dists(bike_vector, body_vector, arm_angle, use="road"):
    """
    Input: bike, body, arm angle (degrees), [optional] usecase
    Computes probability of deviation from optimal for each body angle
    """
    # arm angle in radians:
    #arm_angle = float(arm_angle * (np.pi / 180))



    # back angle, armpit to elbow angle, armpit to wrist angle
    our_knee_angle, our_back_angle, our_awrist_angle = all_angles(bike_vector, body_vector, arm_angle)

    k_ang_prob = prob(
        USE_DICT[use]["opt_knee_angle"][0],
        USE_DICT[use]["opt_knee_angle"][1],
        our_knee_angle,
    )
    b_ang_prob = prob(
        USE_DICT[use]["opt_back_angle"][0],
        USE_DICT[use]["opt_back_angle"][1],
        our_back_angle,
    )
    aw_ang_prob = prob(
        USE_DICT[use]["opt_awrist_angle"][0],
        USE_DICT[use]["opt_awrist_angle"][1],
        our_awrist_angle,
    )
    # print(f"knee extension: {our_knee_angle}")
    # print(f"back angle: {our_back_angle}")
    # print(f"armpit wrist: {our_awrist_angle}")

    return (k_ang_prob, b_ang_prob, aw_ang_prob)


def all_angles(bike_vector, body_vector, arm_angle):
  """
  Input: bike, body, arm_angle in degrees
  Output: tuple (min_ke angle, back angle, awrist angle) in degrees
  """

  # min knee extension angle over sweep 0-2pi
  ke_ang = [
            item for item in (knee_extension_angle(bike_vector, body_vector, angle*0.2)
            for angle in range(0, 32)) if item != None
        ]
  if ke_ang == [] or len(ke_ang) != 32:
    ke_ang = None
  else:
    ke_ang = min(ke_ang)


    # back angle, armpit to elbow angle, armpit to wrist angle
  b_ang, aw_ang = back_armpit_angles(
      bike_vector, body_vector, arm_angle
  )

  return [rad_to_d(ang) if ang != None else None for ang in [ke_ang, b_ang, aw_ang]]