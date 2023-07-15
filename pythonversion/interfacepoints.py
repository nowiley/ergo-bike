import numpy as np

## Calculate interface points from frame and bike parameters
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
        [0,12]: Hbar Type "(Drops, Mtb, Bullhorn)"
        [0,13]: Crank Length
    Output:
        Tuple of interface points: ((hand x, hand y), (seatx, seaty), (crank length))
    """
    def top_headtube():
        # Headtube functional length
        newHTL = bike[0,1] - bike[0,3]

        # Stack height - headtube length * sin(headtube angle)
        DTy = bike[0,4] - newHTL * np.sin(bike[0,2])
        
        # Pythagorean theorem
        DTx = np.sqrt(bike[0,0]**2 - DTy**2)
        
        # Offset from ht and dt intersection
        HTx_offset = newHTL * np.cos(bike[0,2]) 

        # Subtract offset (top of headtube is beind intersection)
        HTx = DTx - HTx_offset

        return (HTx, bike[0,4])

    def seat_check_and_pos():
        Sx = bike[0,8] * np.cos(bike[0,6])
        Sy = bike[0,8] * np.sin(bike[0,6])
        return (Sx, Sy)
    
    def hand_pos(headx, heady):
        # IN MM
        BEARING_STACK  = 10
        STEM_E = 20
        #Total extension of stem above headtube
        UXL = BEARING_STACK + bike[0,11] + STEM_E/2

        # X and Y of Middle of Stem clamp
        SCx = headx - (UXL * np.cos(bike[0,2]))
        SCy = heady + (UXL * np.sin(bike[0,2]))

        #X and Y of handlebar Clamp
        HBx = SCx + bike[0,9] * np.cos((np.pi/2) - bike[0,2] - bike[0,10])
        HBy = SCy + bike[0,9] * np.sin((np.pi/2) - bike[0,2] - bike[0,10])

        #x and y of hand
        match bike[0,12]:
            case "drops":
                Hx = HBx + 100
                Hy = HBy - 100
            case "mtb":
                Hx = HBx + 100
                Hy = HBy - 100
            case "bullhorn":
                Hx = HBx + 100
                Hy = HBy - 100
            case _:
                raise ValueError(f"Invalid handlebar type: {bike[0,12]}, must be 'drops', 'mtb', or 'bullhorn'")
        return (Hx, Hy)

    htx, hty = top_headtube()
    sx, sy = seat_check_and_pos()
    hx, hy = hand_pos()
    

    return ((hx, hy), (sx, sy), (bike[0,13]))


