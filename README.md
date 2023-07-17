# ergo-bike
Includes tools to calculate and analyze the ergonomics of bike/body systems.

**Author:** Noah Wiley

## Table of Contents
1. [Project Goals](#project-goals)
2. [Process and Methodology](#process-and-methodology)
3. [Usage and Documentation](#usage-and-documentation)
    1. [What are these dimensions and angles?](#what-are-these-dimensions-and-angles) 
    2. [Common Inputs](#common-inputs)
    3. [Most Useful Function Examples](#most-useful-function-examples)
    4. [Functions](#functions)


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
1. Created a function to calculate the dimensions of certain body parts given the height of the person which can be used to make a body vector.
2. Created a function to compare the predicted dimensions of the body to the actual dimensions of the body. This function can analyze all images in a certain file path following a naming format and can output a table to compare the predicted and actual dimensions.
3. **ONE** function to to calculate predicted dimensions and angles given an image and a bike vector.

## Usage and Documentation

### What are these dimensions and angles?
![bike angles diagram](angles-diagram.jpeg)

### Quick Start
1. Download the repository
2. Navigate to the pythonversion folder
3. Run the following code in a Python interpreter
```python
import numpy as np
from imageanalysis import *

# Define bike vector
bike_vector = np.array([[-9., 27, 16.5, 25.5, 7.]]).T

# Defining user dimensions
user_height = 71
user_foot_length = 5.5

# Image path following naming convention (can override with optional camdist/camheight in image_angles)
image_path = ".../name-idenifier-camheight-camdist.jpg"

# Run image_angles
result = image_angles(user_height, user_foot_length, image_path, bike_vector)
print(result)
```
Will output something like this:
```python
>>> #Analyzing With Inference Count = 10: /Users/noahwiley/Documents/Bike UROP/MeasureML-main/ergo-bike/pictures/Bright/noah-dpalmclosed-62-111.jpg
(
  {
    'height': 71, 
  'sh_height': 56.67393743138017, 
  'hip_to_ankle': 33.72468993690645, 
  'hip_to_knee': 16.09842413704969, 
  'shoulder_to_wrist': 21.318759732980737, 
  'arm_len': 24.158759732980737, 
  'tor_len': 20.109247494473717, 
  'low_leg': 20.46626579985676, 
  'up_leg': 16.09842413704969
  }, 
  [51.50336286206853, 49.01949672595183, 78.81088800155787], 
  -2.7450928099733733
)
```


### Useful Function Examples

**all_angles and prob_dists**
```python
LL = 19
UL = 15.5
TL = 21
AL = 24
FL = 5.5
AA = deg_to_r(107)
# Defining user and bike dimensions for body bike system
body_4 = np.array([[LL, UL, TL, AL, FL, AA]]).T
bike_4 = np.array([[-9., 27, 16.5, 25.25, 7]]).T

print(all_angles(bike_4, body_4, 150))
>>> ### (knee extension angle, back angle, armpit to wrist angle)
>>>[45.40954825869782, 54.825079651532384, 70.49433849070087]

print(prob_dists(bike_4, body_4, 150))
>>>### (knee extension angle, back angle, armpit to wrist angle) probabilities
>>>(0.056835098630212744, 0.02470619689536746, 4.7871902035923064e-05)
```

**all_noise**
```python
body_4 = np.array([[LL, UL, TL, AL, FL, AA]]).T
bike_4 = np.array([[-9., 27, 16.5, 25.5, 7.]]).T

all_noise(bike_4, body_4, 2, 2)
>>> ### Noise table for each dimension of bike and body
>>> #*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
#*#*#*#*# BIKE NOISE #*#*#*#*#
#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*

 ***** Seat X Dimension *****
  Dim Value    Noise Amt    ke dif    back dif    awrist diff       ke     back    awrist
-----------  -----------  --------  ----------  -------------  -------  -------  --------
        -11           -2  -9.37977    -3.45231        6.50258  36.0298  51.9613   76.9462
         -9            0   0           0              0        45.4095  55.4136   70.4436
         -7            2   6.18105     3.34192       -6.25349  51.5906  58.7556   64.1901

 ***** Seat Y Dimension *****
  Dim Value    Noise Amt    ke dif    back dif    awrist diff        ke     back    awrist
-----------  -----------  --------  ----------  -------------  --------  -------  --------
         25           -2   17.7696     4.56148      -0.124946   63.1792  59.9751   70.3187
         27            0    0          0             0          45.4095  55.4136   70.4436
         29            2  nan         -4.80618       0.623295  nan       50.6075   71.0669

#More data

#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
#*#*#*#*# BODY NOISE #*#*#*#*#
#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*

 ***** Lower Leg Dimension *****
  Dim Value    Noise Amt    ke dif    back dif    awrist diff        ke     back    awrist
-----------  -----------  --------  ----------  -------------  --------  -------  --------
         17           -2  nan                0              0  nan       55.4136   70.4436
         19            0    0                0              0   45.4095  55.4136   70.4436
         21            2   16.0404           0              0   61.45    55.4136   70.4436

#More data
```

**analyze_folder**
```python
our_users = {}
noah_dict = {"height": 71, "torso": 21., "upleg": 15.5, "lowleg": 19., "arm": 24.}
faez_dict = {"height": 70, "torso": 28.3, "upleg": 15.5, "lowleg": 19., "arm": 21.25}
our_users["noah"]= noah_dict
our_users["faez"] = faez_dict

folder = "/content/drive/MyDrive/Bike Pose Detection Folder/Bright "
analyze_folder(folder, our_users)
>>> ### Table comparing predicted and actual dimensions
>>>
file                pred torso    pred upleg    pred lowleg    pred arm    dtorso    dupleg    dlowleg      darm
----------------  ------------  ------------  -------------  ----------  --------  --------  ---------  --------
noah-spalmback         18.7244       19.1177        21.9539     22.2936  -2.27555   3.6177     2.95388  -1.70643
noah-dpalmback         18.8007       19.5824        21.9863     22.3149  -2.19927   4.08238    2.98634  -1.68509
noah-tpalmopen         19.0336       19.4478        21.7123     22.0601  -1.96645   3.9478     2.71234  -1.93986
#More data
```

### Common Inputs
bike_vector: NumPy array in form [seat x, seat y, handlebar x, handlebar y, crank length].T

body_vector: NumPy array in form [lower leg, upper leg, torso length, arm length, foot length, ankle angle].T

arm_angle: Angle between the upper arm and lower arm at the elbow.

users_dictionary: Dictionary mapping user name to dictionary with body dimensions mapped to their name. See example below.
```python
users_dictionary = {}
john_dictionary = {"height": 70, "torso": 28.3, "upleg": 15.5, "lowleg": 19., "arm": 21.25}
users_dictionary["john"] = john_dictionary
```

### Functions
In /pythonversion/README.md

