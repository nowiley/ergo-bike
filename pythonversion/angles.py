import numpy as np
from scipy.stats import norm
from usecases import USE_DICT
# #####
# Bike Ergonomic Angle Fit Calculator
# Calculates body angles given bike and body measurements
# Calculates ergonomic score/probability of fit given use case
######


###################################
# FUNCTIONS FOR CALCUATING ANGLES #
###################################
def knee_extension_angle(bike_vector, body_vector, CA, ret_a2=False):
    """
    Input:
        bike vector, body vector, crank angle, OPTIONAL return a2
        np array bike vector:
            [SX, SY, HX, HY, CL]^T
            (seat_x, seat_y, hbar_x, hbar_y, crank len)
            Origin is bottom bracket
        np array body vector:
            [LL, UL, TL, AL, FL, AA]
            (lowleg, upleg, torso len, arm len, foot len, ankle angle)
        CA = crank angle:
            crank angle fom horizontal in radians
        Optional return a2:
            returns a2 for use in kneeoverpedal check

    Output:
        Knee extension angle in radians
        OR
        None if not valid coords (i.e. NaA appeared)

    """
    #decomposing body vector
    sq_body = np.square(body_vector)

    LL = body_vector[:, 0]
    UL = body_vector[:, 1]
    TL = body_vector[:, 2]
    AL = body_vector[:, 3]
    FL = body_vector[:, 4]
    AA = body_vector[:, 5]

    LL_s = sq_body[:, 0]
    UL_s = sq_body[:, 1]
    TL_s = sq_body[:, 2]
    AL_s = sq_body[:, 3]
    FL_s = sq_body[:, 4]
    AA_s = sq_body[:, 5]

    # decomposing bike vector
    sq_bike = np.square(bike_vector)

    SX = bike_vector[:, 0]
    SY = bike_vector[:, 1]
    HX = bike_vector[:, 2]
    HY = bike_vector[:, 3]
    CL = bike_vector[:, 4]

    SX_s = sq_bike[:, 0]
    SY_s = sq_bike[:, 1]
    HX_s = sq_bike[:, 2]
    HY_s = sq_bike[:, 3]
    CL_s = sq_bike[:, 4]

    #Explicit checks for triangle inequality
    functional_lowleg_foot = np.sqrt(FL_s + LL_s - (2 * FL * LL * np.cos(AA)))
    straightline_seat = np.sqrt(SX_s + SY_s)
    if functional_lowleg_foot + UL < straightline_seat:
        return None


    #Using law of sines and checks for nan/angle validity
    x_1 = np.sqrt(LL_s + FL_s - (2 * LL * FL * np.cos(AA)))

    LX = CL * np.cos(CA) - SX
    LY = SY - CL * np.sin(CA)

    x_2 = np.sqrt((LX**2 + LY**2))

    alpha_1 = np.arccos((x_1**2 - UL_s - x_2**2) / (-2 * UL * x_2))
    if np.isnan(alpha_1):
        return None

    alpha_2 = np.arctan2(LY, LX) - alpha_1
    #for use in kneeoverpedal check
    if ret_a2:
        return alpha_2

    LLY = LY - UL * np.sin(alpha_2)
    LLX = LX - UL * np.cos(alpha_2)

    alpha_3 = np.arctan2(LLY, LLX) - alpha_2

    alpha_4 = np.arccos((FL_s - LL_s - x_1**2) / (-2 * LL * x_1))
    if np.isnan(alpha_4):
        return None

    return alpha_3 + alpha_4



def back_armpit_angles(bike_vector, body_vector, elbow_angle):
    """
    Input: bike_vector, body_vector, elbow_angle in degrees
    Output: back angle, armpit to elbow angle, armpit to wrist angle in degrees

    np array bike vector:
            [SX, SY, HX, HY, CL]^T
    np array body vector:
            [LL, UL, TL, AL, FL, AA]
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

    #Explicit checks for triangle inequality
    # if TL + x_1 < sth_dist:
    #     return (None, None)

    #if not possible return None
    if np.isnan(tors_ang):
        return (None, None)

    # Adds offset to get back angle with horizontal
    back_angle = tors_ang + sth_ang

    #### ARMPIT TO WRIST ANGLE ####
    armpit_to_wrist = np.arccos((TL**2 + x_1 - sth_dist**2)/ (2 * TL * (x_1**0.5)))
    #no check for triangle inequality because checked above

    # return angles in radians
    return (back_angle, armpit_to_wrist)


def deg_to_r(deg):
    """ 
    Converts degrees to radians
    """
    return float(deg / 180) * np.pi


def rad_to_d(rad):
    """
    Converts radians to degrees
    """
    return float(rad * (180 / np.pi))

def all_angles(bike_vector, body_vector, arm_angle):
  """
  Input: bike, body, arm angle (at elbow) in degrees
  Output: tuple (min_ke angle, back angle, awrist angle) in degrees
  """
  #Min knee extension angle over sweep 0-2pi
  #if None appears in sweep, return None

  ke_ang = [
            item for item in (knee_extension_angle(bike_vector, body_vector, angle*0.2)
            for angle in range(0, 32)) if item != None
        ]
  if ke_ang == [] or len(ke_ang) != 32:
    ke_ang = None
  else:
    ke_ang = min(ke_ang)


# back angle, armpit to wrist angle
  b_ang, aw_ang = back_armpit_angles(bike_vector, body_vector, arm_angle)

  return [rad_to_d(ang) if ang != None else None for ang in [ke_ang, b_ang, aw_ang]]

############################
# FUNCTIONS FOR PROABILITY #
############################
# Calculates probability of a certain angle given reccomended angle and standard deviation
# in usecases.py

def prob(mean, sd, value):
    """
    Returns probability of value or larger given mean and sd
    """
    # Handle None type values
    if value is None:
      return None

    dist = abs((value - mean))/sd
    #Double sided probability
    return (1 - norm.cdf(dist, loc=0, scale=1)) * 2

def prob_dists(bike_vector, body_vector, arm_angle, use="road"):
    """
    Input: bike, body, arm angle (degrees), [optional] usecase
    Output: Computes probability of deviation from reccomended angle for each body angle
    """
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

    return (k_ang_prob, b_ang_prob, aw_ang_prob)

def bike_offset(bike_vector, thickness, setback):
    """
    Input: Bike vector
    Output: NEW bike vector with offsets applied
            Seat Y + thickness of seat + hip socket to top of seat
            Seat X - setback - 2 inches for hip socket to seat
            Seat Y - 1 for shoe thickness
            Hbar Y - 1 for shoe thickness
    """
    #Avoid ailiasing
    SX = bike_vector[0, 0].copy()
    SY = bike_vector[1, 0].copy()
    HX = bike_vector[2, 0].copy()
    HY = bike_vector[3, 0].copy()
    CL = bike_vector[4, 0].copy()

    #seat y plus thickness of seat, hip socket to top of seat
    SY += thickness + 2.5  
    #Account for shoe thickness
    SY -= 1 
    HY -= 1
    #seat x decrese by setback and 2 inches for hip socket to seat
    SX -= (2 + setback)

    new_bike = np.array([[SX], [SY], [HX], [HY], [CL]])
    return new_bike

# LL = 19
# UL = 18
# TL = 21
# AL = 24
# FL = 5.5
# AA = deg_to_r(107)
# body_3 = np.array([[LL, UL, TL, AL, FL, AA]])
# body_5 = np.array([[LL, UL, TL, AL, FL, AA]])
# body_4 = np.vstack((body_3, body_5))
# bike_4 = np.array([[-7., 23, 16.5, 25.25, 7]])

# print(knee_extension_angle(bike_4, body_4, deg_to_r(300)))