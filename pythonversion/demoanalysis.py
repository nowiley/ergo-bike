from interfacepoints import interface_points
from vectorizedangles import all_angles, validity_mask
import numpy as np
import pickle
import pandas as pd
import time
#from sklearn.neural_network import MLPRegressor


####################
# Bike and Body Ergonomics and Aerodynamics Calculation
# Main Function to Call: bike_body_calculation(bikes, body)
# 
# Inputs are bike vector array (nx14) and body vector (1x8)
# Input Units: mm and degrees SX is behind BB
# 
# Output: Pandas dataframe of knee extension, back angle, armpit angle, aerodynamic drag (nx4)
# Output Units: degrees and Newtons (at 10m/s wind speed)
####################


#GLOBAL MODEL
global_model = pickle.load(open("pythonversion/new_formatted_model.pkl", "rb"))[2]

def augmented_parameters(int_points, body):
    """
    Input:
    array of interface points (nx5) and body dimensions (1x8)
        int_pts = [sx, sy, hx, hy, cl]
        body = [ll, ul, tl, al, fl, aa, sw, ht]
    Output: array of augmented parameters (nx5)
        [back vertical height, thigh width, leg area, frontal surface area, arm height]
    
    !! WARNING: Calculates area in (input units)^2 !!!
    !!! SX is behind BB !!! (Different from vectorizedangles.py)
    """
    # Calculate new body for neckhead & broadcast
    neckhead = body[:, 7] - body[:, 0] - body[:, 1] - body[:, 2]
    new_body = np.hstack((body[0, :4], body[0, 6], neckhead)) # [ll, ul, tl, al] + [sw] + [neckhead]
    br_new_body = np.broadcast_to(new_body, (len(int_points), 6))

    # Create joined array config
    # [hx, hy, sx, sy, cl, ll, ul, tl, al, sw, neckhead]
    config = np.hstack((int_points, br_new_body))

    # Calculate key dimensions of interest and augmented parameters
    additionaldata=np.zeros((len(config[:,1]),5))
    for i in range(len(config)):
        # Decompose config per row
        hx = config[i, 0]
        hy = config[i, 1]
        sx = config[i, 2]
        sy = config[i, 3]
        cl = config[i, 4]
        ll = config[i, 5]
        ul = config[i, 6]
        back = config[i, 7]
        arm = config[i, 8]
        sw = config[i, 9]
        neckhead = config[i, 10]
        
        # Calculate augmented parameters
        Lsh=np.sqrt((sx-0.2+hx)**2+(sy-hy)**2) #distance from saddle to handlebar
        Lspl=np.sqrt((sx-0.2)**2+sy**2)+cl #distance from saddle to pedals in farthest pos
        #Lsps=np.sqrt((sx-0.2)**2+sy**2)-cl #distance from saddle to pedals in closest pos
        Tsh=np.arctan((hy-sy)/(sx-0.2+hx)) #angle from saddle to handlebar in degrees
        Tsp2=np.arctan(-(sy+cl)/(sx-0.2)) #angle from saddle to lower pedal in degrees
        Tssh=np.arccos((back**2+Lsh**2-arm**2)/(2*back*Lsh)) #angle from shoulders to saddle to handle
        #Tksp=np.arccos((ul**2+Lsps**2-ll**2)/(2*ul*Lsps)) #angle from knee to saddle to closest pedal pos
        #Tskp=np.arccos((ul**2+ll**2-Lsps**2)/(2*ul*ll)) #angle from saddle to knee to closest pedal pos
        Tksp2=np.arccos((ul**2+Lspl**2-ll**2)/(2*ul*Lspl)) #angle from knee to saddle to farthest pedal pos
        #Tskp2=np.arccos((ul**2+ll**2-Lspl**2)/(2*ul*ll)) #angle from saddle to knee to farthest pedal pos
        backverticalheight=back*np.sin(Tsh+Tssh)
        shoulderheight=backverticalheight+sy
        headheight=(back+neckhead)*np.sin(Tsh+Tssh)
        armheight=shoulderheight-hx
        theighwidth=(sw/2-.16)/2
        lowerkneeheight=ul*np.sin(Tksp2+Tsp2)
        if lowerkneeheight<sy:
            legarea=(sy-lowerkneeheight)*(theighwidth-.12)+2*sy*.12
        else:
            legarea=2*sy*.12
        frontalsa=armheight*.1+shoulderheight*sw+np.pi/16+.1*sw*np.cos(Tsh+Tssh)
        additionaldata[i,:]=[backverticalheight,headheight,theighwidth,legarea,frontalsa]
    afdf = pd.DataFrame(additionaldata, columns=["Back Vertical Height","Head Height","Theigh Width","Leg Area","Frontal Surface Area"])
    return afdf

def aerodynamic_drag(int_points, body, augmented_params):
    """
    Input: bike vector array (nx14), body vector array (1x8)
        int_points = [hx, hy, sx, sy, cl]
        body = [LL, UL, TL, AL, FL, AA, SW, HT]
        augmented_params = [back vertical height, head height, thigh width, leg area, frontal surface area]
    Output: 
        aerodynamic drag (nx1) in Newtons
    !!! Units in Meters !!!
    !!! Will not work if there are NaNs in input !!!
    """
    # Calculate new body for neckhead & broadcast in METERS
    neckhead = body[:, 7] - body[:, 0] - body[:, 1] - body[:, 2]
    new_body = np.hstack((body[0, :4], body[0, 6], neckhead)) * 0.001 # [ll, ul, tl, al] + [sw] + [neckhead]
    br_new_body = np.broadcast_to(new_body, (len(int_points), 6))

    # Making input array for aerodynamic drag calculation model (nx16)
    # [hx, hy, sx, sy, cl, ll, ul, tl, al, sw, neckhead, back vertical height, head height, thigh width, leg area, frontal surface area]
    joined_arr = np.hstack((int_points, br_new_body, augmented_params))

    # Check for NaNs
    if np.isnan(joined_arr).any():
        raise ValueError("NaNs in input array")

    # Convert to dataframe to input into model
    input_df = pd.DataFrame(joined_arr, columns=["hx", "hy", "sx", "sy", "cl", "ll", "ul", "tl", "al", "sw", "neckhead", "back vertical height", "head height", "thigh width", "leg area", "frontal surface area"])
    pred_aero = global_model.predict(input_df)
    return pred_aero

def bike_body_calculation(bikes, body):
    """
    Input: bike vector array (nx14), body vector(1x8)
        BV = [HTx, HTy, STx, STy, CL, LL, UL, TL, AL, FL, AA, SW, HT, HB]
        Body = [LL, UL, TL, AL, FL, AA, SW, HT]
    Output: knee extension, back angle, armpit angle, aerodynamic drag (nx4)
    !!! UNITS: mm and degrees !!!
    !!! Positive SX is behind BB !!! (Different from vectorizedangles.py)
    !!! LOAD MODEL IN GLOBAL FRAME TO SAVE TIME !!!
    """
    # **** LOAD THIS IN WRAPPER FUNCTION ****
    # Initializing model from pkl file 
    #model = pickle.load(open("model.pkl", "rb"))[2]
    #model = GLOBAL_AERO_MODEL
    # **** LOAD THIS IN WRAPPER FUNCTION ****

    # Constants
    DEFAULT_ARM_ANGLE = 150
    
    # Calculate interface points 
    #   NOTE: standard offsets are in mm 
    #   input and output should be treated as mm
    int_points = interface_points(bikes) # convert to m
    int_points_df = pd.DataFrame(int_points, columns=["hx", "hy", "sx", "sy", "cl"])

    # Calculate ergonomic angles (nx3)
    # Broadcast body array and arm_angles for ergonomic angles calculation
    br_arm_angles = np.ones((len(bikes), 1)) * DEFAULT_ARM_ANGLE
    br_angles_body = np.broadcast_to(body, (len(bikes), 8))
    out_angles = pd.DataFrame(all_angles(int_points, br_angles_body, br_arm_angles), columns=["Knee Extension", "Back Angle", "Armpit Angle"])

    # Calculate augmented parameters
    out_aug = augmented_parameters(int_points, body)
    out_aug = out_aug.div(1000) # convert to m
    out_aug[["Leg Area", "Frontal Surface Area"]] = out_aug[["Leg Area", "Frontal Surface Area"]].div(1000) # convert areas to m^2

    # Create NaN Masks for augmented parameters and angles
    valid_mask = validity_mask(int_points, br_angles_body, br_arm_angles).flatten()
    aug_nan_mask = np.isnan(out_aug.values).any(axis=1)
    angle_nan_mask = np.isnan(out_angles.values).any(axis=1)
    combined_nan_mask = aug_nan_mask | valid_mask

    # Remove NaN rows from interface points, augmented parameters, and angles
    no_nan_int_points = int_points_df[~combined_nan_mask]/1000 # convert to m
    no_nan_aug = out_aug[~combined_nan_mask]
    no_nan_angles = out_angles[~combined_nan_mask]
    print("no_nan_int_points\n",no_nan_int_points)

    # Calculate aero drag
    #pred_aero = aerodynamic_drag(no_nan_int_points, body, no_nan_aug)[:, np.newaxis]
    pred_aero = np.zeros((len(no_nan_angles), 1))

    # Concatenate angle outputs and aerodynamic drag
    out = np.hstack((no_nan_angles.values, pred_aero))
    out_df = pd.DataFrame(out, columns=["Knee Extension", "Back Angle", "Armpit Angle", "Aerodynamic Drag"])
    return out_df



bikes_df = pd.read_csv("/Users/noahwiley/Documents/Bike UROP/MeasureML-main/Frame Datasets/bike_vector_df_with_id.csv").iloc[:, 2:]
# print("bikes df\n",bikes_df)
int_points_global = interface_points(bikes_df.values)
# print("int_points_global\n", int_points_global)
LL = 22 * 25.4 
UL = 22 * 25.4
TL = 21 * 25.4
AL = 24 * 25.4
FL = 5.5 * 25.4
AA = 105
SW = 12 * 25.4
HT = 71 * 25.4
body = np.array([[LL, UL, TL, AL, FL, AA, SW, HT]])
#body = np.broadcast_to(body, (len(bikes_df), 8))
# print("body\n",body)

# #Test bike_body_calculation
start = time.time()
res = bike_body_calculation(bikes_df.values, body)
tot_time = time.time() - start
print(f"Result in {tot_time} time:\n", res)

