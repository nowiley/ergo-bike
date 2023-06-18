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
1. Created a function to calculate the dimensions of certain body parts given the height of the person which can be used to make a body vector.
2. Created a function to compare the predicted dimensions of the body to the actual dimensions of the body. This function can analyze all images in a certain file path following a naming format and can output a table to compare the predicted and actual dimensions.

## Usage and Documentation
### Common Inputs
bike_vector: NumPy array in form [seat x, seat y, handlebar x, handlebar y, crank length].T

body_vector: NumPy array in form [lower leg, upper leg, torso length, arm length, foot length, ankle angle].T

arm_angle: Angle between the upper arm and lower arm at the elbow.

users_dictionary: Dictionary mapping user name to dictionary with body dimensions mapped to their name. See example below.
```
users_dictionary = {}
john_dictionary = {"height": 70, "torso": 28.3, "upleg": 15.5, "lowleg": 19., "arm": 21.25}
users_dictionary["john"] = john_dictionary
```

### Functions
### knee_extension_angle(bike_vector, body_vector, CA)
**Description:**
	Calculates knee extension angle for a given bike and body system and at a specific crank angle (CA)
**Input:**
    bike_vector
    body_vector
    CA in **radians**
**Output:**
Knee extension angle in **radians** or None if inputs violate triangle inequality.

### back_armpit_angles(bike_vector, body_vector, arm_angle)
**Description:**
    Calculates back angle and armpit to wrist angle for a given bike and body system and at a specific arm angle.
**Input:**
    bike_vector
    body_vector
    arm_angle in **degrees**
**Output:**
    Tuple of back angle in **radians** and armpit to wrist angle in **radians** or None if inputs violate triangle inequality.

### all_angles(bike_vector, body_vector, arm_angle)
**Description:**
* Uses knee_extension_angle and back_armpit_angles to produce one tuple corresponding to the minimum knee extension angle, back angle, and armpit to wrist angle. 
* Minimum knee extension angle is calculated on a [0, 2π] interval and returns None if it ever violates the triangle inequality (the bike body system cannot complete a full rotation of the cranks). 
**Input:**
    bike_vector
    body_vector
    arm_angle in **degrees**
**Output:**
    Tuple of minimum knee extension angle in **degrees**, back angle in **degrees**, and armpit to wrist angle in **degrees** or None if inputs violate triangle inequality for certain angle.

### prob_dists(bike_vector, body_vector, arm_angle, use="road")
**Description:**
    Uses all angles and USE_DICT to calculate probabilities of the angles in the given bike and body system using Gaussian curve and CDF. Returns None for angles that are None.
**Input:**
    bike_vector
    body_vector
    arm_angle in **degrees**
    use: String corresponding to usecase in USE_DICT ("road", "mtb", "commute")
**Output:**
    Tuple of probabilities of minimum knee extension angle, back angle, and armpit to wrist angle or None if inputs violate triangle inequality for certain angle.

### all_noise(bike_vector, body_vector, step_size, n)
**Description:**  
* Produces tables mapping noise in each dimension of the bike/body system to the respective change to knee extension angle, back angle, and armpit wrist angle.
* Produces “nan” if a test violated the triangle inequality.
* Note: arm_angle is defaulted to 150 degrees.
**Input:**
    bike_vector
    body_vector
    step_size: Step size of noise in each dimension
    n: Number of tests to run for each dimension
**Output:**
    Prints noise table for each dimension of bike and body with 2n-1 rows in each table.

### analyze_folder(folder_path, users_dictionary)
**Description:**
* Analyzes all images in a folder and compares the predicted dimensions of the body to the actual dimensions of the body.
* Produces a table comparing the predicted and actual dimensions.
**Input:**
    folder_path: Path to folder containing images
    users_dictionary: Dictionary mapping user name to dictionary with body dimensions mapped to their name.
**Output:**
    Prints table comparing predicted and actual dimensions.