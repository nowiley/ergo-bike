# ergo-bike
Includes tools to calculate and analyze the ergonomics of bike/body systems.

## Project Goals
1. Identify key factors for the ergonomics of a particular bike fit and their optimal ranges.
2. Provide tools to easily quantify and analyze the ergonomic performance of a given bike and body system and their intended use.
3. Integrate these tools with pose prediction software to speed up calculation, and provide tools to analyze the sensitivity and accuracy of the entire system.

## Process and Methodology
### 1. Identify key factors for the ergonomics of a particular bike fit and their optimal ranges.
1. Using "Bike Fit 2nd Edition" by Phil Burt and Chris Hoy as a reference, identified key factors of a unique bike fit to be the knee extension angle, back angle, and armpit to wrist angle.
    1. Knee extension angle is the angle between the upper and lower leg, measured at the knee, and is used to quantify the ergonomics of the saddle height.
    2. Back angle is the angle between the torso and horizontal plane and is used alongside the armpit to wrist angle to quantify the ergonomics of the handlebar height and reach of the bike.
2. Using the same reference, identified the optimal ranges of these factors. These correspond to the RETÜL bike fit system's reccomendations and are as follows:
    1. Knee extension angle: 45-30 degrees
    2. Back angle: 45-60 degrees
    3. Armpit to wrist angle: 80-100 degrees
### 2. Provide tools to easily quantify and analyze the ergonomic performance of a given bike and body system and their intended use.
1. Represented a bike and body system as a series of rigid bodies connected by joints. The bike is represented as 4 coordinates and the crank length (seat x, seat y, handelbar x, handelbar y, crank length). The body is represented as the dimensions of the body (lower leg, upper leg, torso length, arm length, foot length, ankle angle, arm angle).
    * The bike and body can be represented as two vectors.
2. Created a function to calculate the knee extension angle, back angle, and armpit to wrist angle of a given bike and body system. This function uses the law of cosines and other trigonometric functions to calculate these angles and to determine if a system violates the triangle inequality (not valid system).
3. Created a function to calculate the ergonomics of a given bike and body system. This function uses the angles calculated in the previous function and a usecase dictionary to determine the ergonomics of the system. The ergonomics are calculated by finding the distance between the angle and the optimal range as specified for the usecase in the usecase dictionary. The distance is then normalized by the optimal range to give a percentage of how close the angle is to the optimal range. 
### 3. Integrate these tools with pose prediction software to speed up calculation, and provide tools to analyze the sensitivity and accuracy of the entire system.