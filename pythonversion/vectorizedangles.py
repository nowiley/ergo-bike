import numpy as np
from scipy.stats import norm
from usecases import USE_DICT
# #####
# Bike Ergonomic Angle Fit Calculator
# Calculates body angles given bike and body measurements
# Calculates ergonomic score/probability of fit given use case
######


#############################################
# Masking Functions for Triangle Inequality #
#############################################

def deg_to_r(deg):
    """ 
    Converts degrees to radians
    """
    return (deg.astype(float) / 180) * np.pi


def rad_to_d(rad):
    """
    Converts radians to degrees
    """
    return rad.astype(float) * (180 / np.pi)

def validity_mask(bikes, bodies, arm_angle):
    """
    Input: bikes, bodies, arm_angles matricies n x 5, n x 8, nx1
    Output: n x 1 True/False mask for valid/invalid
    Checks for triangle inequality for:
        Leg
        Arm/torso
    """
    print("VALID MASK INPUT: bikes", bikes)
    print("VALID MASK INPUT: bodies", bodies)
    print("VALID MASK INPUT: arm_angle", arm_angle)
    ### Mask invalid arm/torso combos ###
    # Straight line distance between saddle position and handlebar position
    bike_reach = np.sqrt(np.square(-bikes[:, 0:1] - bikes[:,3:4]) + np.square(bikes[:, 1:2] - bikes[:, 4:5]))
    # Armlength considering arm bent at elbow
    functional_arms = np.sqrt( (np.square(bodies[:, 3:4]/2)) * (1 - np.cos(deg_to_r(arm_angle))))
    # Max reach of functional arms + torso
    max_body_reach = bodies[:, 2:3] + functional_arms
    # Mask where sum of arms + torso is greater than straightline saddle to handlebar
    mask_upper = max_body_reach <= bike_reach
    
    ### Mask invalid leg combos ###
    # Functional low leg length (considering ankle angle and foot length)
    a_2 = np.square(bodies[:, 4:5])  
    b_2 = np.square(bodies[:, 0:1])
    ab_cos = 2 * bodies[:, 4:5] * bodies[:, 0:1] * np.cos(bodies[:, 5:6]* (np.pi/180))
    funcitonal_low_leg = np.sqrt(a_2 + b_2 - ab_cos)
    
    # Max leg length (functional low leg + upper leg)
    max_leg = bodies[:, 1:2] + funcitonal_low_leg

    # Straightline distance from seat to pedal at longest part of pedal stroke
    straightline_seat = np.sqrt(np.square(bikes[:, 0:1]) + np.square(bikes[:, 1:2])) + bikes[:, 4:5]

    # Mask where max leg length is greater than straightline seat to pedal
    mask_lower = max_leg <= straightline_seat

    #Combine and return masks
    return np.logical_and(mask_upper, mask_lower)




###################################
# FUNCTIONS FOR CALCUATING ANGLES #
###################################
def knee_extension_angle(bike_vectors, body_vectors, CA, ret_a2=False):
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
            crank angle fom horizontal in DEGREES
        Optional return a2:
            returns a2 for use in kneeoverpedal check

    Output:
        Knee extension angle in radians
        OR
        None if not valid coords (i.e. NaA appeared)

    """
    CA = CA * (np.pi/180)

    #decomposing body vector
    sq_body = np.square(body_vectors)

    LL = body_vectors[:,0:1]
    UL = body_vectors[:,1:2]
    TL = body_vectors[:,2:3]
    AL = body_vectors[:,3:4]
    FL = body_vectors[:,4:5]
    AA = body_vectors[:,5:6] * (np.pi/180)

    LL_s = sq_body[:,0:1]
    UL_s = sq_body[:,1:2]
    TL_s = sq_body[:,2:3]
    AL_s = sq_body[:,3:4]
    FL_s = sq_body[:,4:5]
    AA_s = sq_body[:,5:6]

    # decomposing bike vector
    sq_bike = np.square(bike_vectors)

    SX = bike_vectors[:,0:1] * -1
    SY = bike_vectors[:,1:2]
    HX = bike_vectors[:,2:3]
    HY = bike_vectors[:,3:4]
    CL = bike_vectors[:,4:5]

    SX_s = sq_bike[:,0:1]
    SY_s = sq_bike[:,1:2]
    HX_s = sq_bike[:,2:3]
    HY_s = sq_bike[:,3:4]
    CL_s = sq_bike[:,4:5]

    #Using law of sines and checks for nan/angle validity
    x_1 = np.sqrt(LL_s + FL_s - (2 * LL * FL * np.cos(AA)))

    LX = CL * np.cos(CA) - SX
    LY = SY - CL * np.sin(CA)

    x_2 = np.sqrt((LX**2 + LY**2))

    alpha_1 = np.arccos((x_1**2 - UL_s - x_2**2) / (-2 * UL * x_2))

    alpha_2 = np.arctan2(LY, LX) - alpha_1
    #for use in kneeoverpedal check
    if ret_a2:
        return alpha_2

    LLY = LY - UL * np.sin(alpha_2)
    LLX = LX - UL * np.cos(alpha_2)

    alpha_3 = np.arctan2(LLY, LLX) - alpha_2

    alpha_4 = np.arccos((FL_s - LL_s - x_1**2) / (-2 * LL * x_1))

    return (alpha_3 + alpha_4) * (180/np.pi)



def back_armpit_angles(bike_vectors, body_vectors, elbow_angles):
    """
    Input: bike_vector, body_vector, elbow_angle in degrees
    Output: back angle, armpit to elbow angle, armpit to wrist angle in degrees

    np array bike vector:
            [SX, SY, HX, HY, CL]^T
    np array body vector:
            [LL, UL, TL, AL, FL, AA]
    """
    elbow_angle = elbow_angles * (np.pi/180)
    LL = body_vectors[:, 0:1]
    UL = body_vectors[:, 1:2]
    TL = body_vectors[:, 2:3]
    AL = body_vectors[:, 3:4]
    FL = body_vectors[:, 4:5]
    AA = body_vectors[:, 5:6]

    # decomposing bike vector
    SX = bike_vectors[:, 0:1] * -1
    SY = bike_vectors[:, 1:2]
    HX = bike_vectors[:, 2:3]
    HY = bike_vectors[:, 3:4]
    CL = bike_vectors[:, 4:5]

    #### BACK ANGLE ####
    # Calculating straightline distance between handlebars and seat
    sth_dist = ((HY - SY) ** 2 + (HX - SX) ** 2) ** 0.5

    # Calculating angle offset (horizontal to sth_dist) for torso angle
    sth_ang = np.arctan2((HY - SY), (HX - SX))


    # Uses new dist and law of cosines to find torso angle
    x_1 = (AL / 2) ** 2 + (AL / 2) ** 2 - 2 * (AL / 2) * (AL / 2) * np.cos(elbow_angle)

    tors_ang = np.arccos((TL**2 + sth_dist**2 - x_1) / (2 * TL * sth_dist))


    # Adds offset to get back angle with horizontal
    back_angle = tors_ang + sth_ang

    #### ARMPIT TO WRIST ANGLE ####
    armpit_to_wrist = np.arccos((TL**2 + x_1 - sth_dist**2)/ (2 * TL * (x_1**0.5)))

    #no check for triangle inequality because checked above

    # return angles in radians
    return (rad_to_d(back_angle), rad_to_d(armpit_to_wrist))



def all_angles(bike_vectors, body_vectors, arm_angles):
    """
    Input: bike, body, arm angle (at elbow) in degrees
    Output: tuple (min_ke angle, back angle, awrist angle) in degrees
    """
    #Min knee extension angle over sweep 0-2pi np.maximum propogates nans
    cur_min = knee_extension_angle(bike_vectors, body_vectors, 0)
    
    for test_ca in range(0,3000):
        cur_test = knee_extension_angle(bike_vectors, body_vectors, test_ca)
        cur_min = np.minimum(cur_min, cur_test)
        #print(f"Testing {test_ca}: cur_test = {cur_test} cur_min = {cur_min}")

    ke_ang = cur_min

    # back angle, armpit to wrist angle
    b_angs, aw_angs = back_armpit_angles(bike_vectors, body_vectors, arm_angles)

    out = np.hstack((ke_ang, b_angs, aw_angs))
    return out

############################
# FUNCTIONS FOR PROABILITY #
############################
# Calculates probability of a certain angle given reccomended angle and standard deviation
# in usecases.py

def prob(mean, sd, values):
    """
    Returns probability of value or larger given mean and sd
    """
    # Handle None type values

    dist = abs((values - mean))/sd
    #Double sided probability
    return (1 - norm.cdf(dist, loc=0, scale=1)) * 2

def prob_dists(bike_vectors, body_vectors, arm_angles, use="road"):
    """
    Input: bike, body, arm angle (degrees), [optional] usecase
    Output: Computes probability of deviation from reccomended angle for each body angle
    """
    # back angle, armpit to elbow angle, armpit to wrist angle
    knee_angles, back_angles, awrist_angles = all_angles(bike_vectors, body_vectors, arm_angles)

    k_ang_prob = prob(
        USE_DICT[use]["opt_knee_angle"][0],
        USE_DICT[use]["opt_knee_angle"][1],
        knee_angles,
    )
    b_ang_prob = prob(
        USE_DICT[use]["opt_back_angle"][0],
        USE_DICT[use]["opt_back_angle"][1],
        back_angles,
    )
    aw_ang_prob = prob(
        USE_DICT[use]["opt_awrist_angle"][0],
        USE_DICT[use]["opt_awrist_angle"][1],
        awrist_angles,
    )

    return np.hstack((k_ang_prob, b_ang_prob, aw_ang_prob))

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
# AA = 105
# body_3 = np.array([[LL, UL, TL, AL, FL, AA]])
# body_5 = np.array([[LL, UL, TL, AL, FL, AA]])
# body_4 = np.array([[LL, UL, TL, AL, FL, AA]])
# bodies= np.hstack((body_3, body_5, body_4))
# bike_4 = np.array([[-11., 29, 16.5, 25.25, 8.088]])
# bike_5 = np.array([[-11., 27, 16.5, 25.25, 7]])
# bike_6 = np.array([[-11., 27, 16.5, 25.25, 10]])
# bikes = np.hstack((bike_4, bike_5, bike_6))

# print(all_angles(bikes, bodies, np.array([150,130, 140])))
# print(prob_dists(bikes, bodies, np.array([150,130, 140]))) 
# #print(bikes)