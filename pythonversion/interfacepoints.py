import numpy as np

## Calculate interface points from frame and bike parameters
def interface_points(bike, hbar_type = "drops"):
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
        bike = np.array([[DTL, HTL, HTA, HTLE, SH, STL, STA, SPL, SH, SL, SA, SpA, CL]]]])
        
    Output:
        Tuple of interface points: ((hand x, hand y), (seatx, seaty), (crank length))
    """
    # Constants in mm
    BEARING_STACK = 10 # Stack height of bearing
    STEM_E = 40 # Stem extension


    def top_headtube():
        # Headtube functional length
        newHTL = bike[:,1] - bike[:,3]

        # Stack height - headtube length * sin(headtube angle)
        DTy = bike[:,4] - newHTL * np.sin(bike[:,2])
        
        # Pythagorean theorem
        DTx = np.sqrt(bike[:,0]**2 - DTy**2)
        
        # Offset from ht and dt intersection
        HTx_offset = newHTL * np.cos(bike[:,2]) 

        # Subtract offset (top of headtube is beind intersection)
        HTx = DTx - HTx_offset
        
        # HTy and HTx matrix 
        # [[HTx1, HTy1]
        # [HTx2, HTy2]...]
        # np.hstack((HTx, bike[:,4]))
        # 2 vectors HTx and HTy
        return (HTx, bike[:,4])

    def seat_check_and_pos():
        Sx = bike[:,8] * np.cos(bike[:,6])
        Sy = bike[:,8] * np.sin(bike[:,6])
        # 2 Vectors Sx and Sy
        return (Sx, Sy)
    
    def hand_pos(headx, heady):
        #Total extension of stem above headtube
        UXL = BEARING_STACK + bike[:,11] + STEM_E/2

        # X and Y of Middle of Stem clamp
        SCx = headx - (UXL * np.cos(bike[:,2]))
        SCy = heady + (UXL * np.sin(bike[:,2]))

        #X and Y of handlebar Clamp
        HBx = SCx + bike[:,9] * np.cos((np.pi/2) - bike[:,2] - bike[:,10])
        HBy = SCy + bike[:,9] * np.sin((np.pi/2) - bike[:,2] - bike[:,10])
        print("HBX, HBY", HBx, HBy)

        #x and y of hand
        match hbar_type:
            case "drops":
                Hx = HBx + 100
                Hy = HBy + 20
            case "mtb":
                Hx = HBx - 20
                Hy = HBy + 0
            case "bullhorn":
                Hx = HBx + 100
                Hy = HBy + 10
            case _:
                raise ValueError(f"Invalid handlebar type: {hbar_type}, must be 'drops', 'mtb', or 'bullhorn'")
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
    print("reshaped", reshaped)

    # n x 5 array: hx, hy, sx, sy, crank length
    interface_points = np.hstack(reshaped)

    return interface_points

# # bike = np.array([[DTL, HTL, HTA, HTLE, SH, STL, STA, SPL, SH, SL, SA, SpA, CL]]]])
bike1 = np.array([[500, 100, (75/180)*np.pi, 40, 450, 440, (74/180)*np.pi, 200, 700, 100, (15/180)*np.pi, 10, 175]])
bike2 = np.array([[600, 100, (70/180)*np.pi, 40, 450, 440, (74/180)*np.pi, 200, 600, 100, (110/180)*np.pi, 10, 175]])
bike3 = np.array([[400, 100, (75/180)*np.pi, 40, 450, 440, (74/180)*np.pi, 200, 400, 100, (15/180)*np.pi, 10, 175]])
all_bikes = np.vstack((bike1, bike2, bike3))
# print(np.shape(all_bikes))
print(interface_points(all_bikes, hbar_type="drops"))
# #print(np.shape(interface_points(all_bikes, hbar_type="drops")))