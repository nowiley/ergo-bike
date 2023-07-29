import numpy as np

## Calculate interface points from frame and bike parameters
def deg_to_r(deg):
    """ 
    Converts degrees to radians
    """
    return (deg.astype(float) / 180) * np.pi
def interface_points(bike):
    """
    Input: in relation to bottom bracket
        Bike np array:
        [0,0]: DT Len,
        [0,1]: HT Len
        [0,2]: HT Angle
        [0,3]: HT Lower Extension
        [0,4]: Stack Height
        [0,5]: ST Len
        [0,6]: ST Angle
        [0,7]: Seatpost Len
        [0,8]: Saddle height
        [0,9]: Stem Len
        [0,10]: Stem Angle
        [0,11]: Spacer Amt
        [0,12]: Crank Length
        [0,13]: Hbar Style (0 = drops, 1 = mtb, 2 = bullhorn)
        bike = np.array([[DTL, HTL, HTA, HTLE, SH, STL, STA, SPL, SH, SL, SA, SpA, CL]]]])
        
    Output:
        Tuple of interface points: ((hand x, hand y), (seatx, seaty), (crank length))
    """
    # Constants in mm
    BEARING_STACK = 15 # Stack height of bearing
    STEM_E = 40 # Stem extension

    #convert angles to radians
    HTA = deg_to_r(bike[:,2])
    STA = deg_to_r(bike[:,6])
    SA = deg_to_r(bike[:,10])

    def top_headtube():
        # Headtube functional length
        newHTL = bike[:,1] - bike[:,3]

        # Stack height - headtube length * sin(headtube angle)
        DTy = bike[:,4] - (newHTL * np.sin(HTA))
        
        # Pythagorean theorem
        DTx = np.sqrt(bike[:,0]**2 - DTy**2)
        
        # Offset from ht and dt intersection
        HTx_offset = newHTL * np.cos(HTA)

        # Subtract offset (top of headtube is beind intersection)
        HTx = DTx - HTx_offset
        
        # HTy and HTx matrix 
        # [[HTx1, HTy1]
        # [HTx2, HTy2]...]
        # np.hstack((HTx, bike[:,4]))
        # 2 vectors HTx and HTy
        return (HTx, bike[:,4])

    def seat_check_and_pos():
        Sx = bike[:,8] * np.cos(STA)
        Sy = bike[:,8] * np.sin(STA)
        # 2 Vectors Sx and Sy
        return (Sx, Sy)
    
    def hand_pos(headx, heady):
        #Total extension of stem above headtube
        UXL = BEARING_STACK + bike[:,11] + STEM_E/2

        # X and Y of Middle of Stem clamp
        SCx = headx - (UXL * np.cos(HTA))
        SCy = heady + (UXL * np.sin(HTA))

        #X and Y of handlebar Clamp
        HBx = SCx + bike[:,9] * np.cos((np.pi/2) - HTA - SA)
        HBy = SCy + bike[:,9] * np.sin((np.pi/2) - HTA - SA)
        #print("HBX, HBY", HBx, HBy)

        #x and y of hand by handlebar type
        # Handlebar type mask deals with floating point errors
        drops_mask = bike[:,13] <= 0.5
        mtb_mask = abs(bike[:,13] - 1) <= 0.25
        bullhorn_mask = abs(bike[:,13] - 2) <= 0.25

        #Drops are last to make default
        Hx = np.zeros(len(bike[:,0]))
        Hy = np.zeros(len(bike[:,0]))
        #Bullhorns
        Hx[bullhorn_mask] = HBx[bullhorn_mask] + 100
        Hy[bullhorn_mask] = HBy[bullhorn_mask] + 10
        #MTB
        Hx[mtb_mask] = HBx[mtb_mask] - 20
        Hy[mtb_mask] = HBy[mtb_mask] + 0
        #Drops
        Hx[drops_mask] = HBx[drops_mask] + 100
        Hy[drops_mask] = HBy[drops_mask] + 20

        # 2 vectors Handx and Handy
        return (Hx, Hy)

    # Calculate interface points
    htx, hty = top_headtube() # Top of headtube
    sx, sy = seat_check_and_pos() # Seat position uses saddle height
    hx, hy = hand_pos(htx, hty) # Hand position uses top of headtube position
    
    # Reshaping to 2D arrays
    reshaped = []
    for vec in [hx, hy, sx, sy, bike[:,12]]:
        reshaped.append(vec.reshape((len(vec), 1)))

    # n x 5 array: hx, hy, sx, sy, crank length
    interface_points = np.hstack(reshaped)

    return interface_points

# # bike = np.array([[DTL, HTL, HTA, HTLE, SH, STL, STA, SPL, SH, SL, SA, SpA, CL]]]])
# bike1 = np.array([[500, 100, (75/180)*np.pi, 40, 450, 440, (74/180)*np.pi, 200, 700, 100, (15/180)*np.pi, 10, 175, 1]])
# bike2 = np.array([[600, 100, (70/180)*np.pi, 40, 450, 440, (74/180)*np.pi, 200, 600, 100, (110/180)*np.pi, 10, 175, 1]])
# bike3 = np.array([[400, 100, (75/180)*np.pi, 40, 450, 440, (74/180)*np.pi, 200, 400, 100, (15/180)*np.pi, 10, 175, 0]])
# all_bikes = np.vstack((bike1, bike2, bike3))
# # print(np.shape(all_bikes))
# print(interface_points(all_bikes))
# # #print(np.shape(interface_points(all_bikes, hbar_type="drops")))