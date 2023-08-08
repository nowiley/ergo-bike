# Python Version of Bike Fit Calculator
#### Function Documentation
---

### bike_body_calculation(strucutural_bike_vectors, large_body_vector):
**Description:**
* Calculates the predicted body angles and aerodynamic drag for a given bike and body system.

**Input:**
- structural_bike_vectors (n x 14 matrix) **IN Millimeters and Degrees**
  - PD Dataframe with columns:
    - DT Lenength
    - HT Length
    - HT Angle
    - HT LX
    - Stack height
    - ST Length
    - ST Angle
    - Seatpost LENGTH
    - Saddle height
    - Stem length
    - Stem Angle
    - Headset spacers
    - Crank length
    - Handlebar Style
- large_body_vector (1 x 8 matrix)
  - np array:
    - (0,0): Lower Leg Length
    - (0,1): Upper Leg Length
    - (0,2): Trunk Length
    - (0,3): Arm Length
    - (0,4): Foot Length
    - (0,5): Ankle Angle
    - (0,6): Shoulder Witdh
    - (0,7): Height

**Output:**
- PD Dataframe:
  - Columns:
    - Knee Extension Angle
    - Back Angle
    - Armpit to Wrist Angle
    - Aerodynamic Drag

**Notes:**
- Uses default values for arm angle = 150 deg, headset bearing length = 10 mm, and stem clamp length = 40 mm. These can be changed in demoanalysis.py and interfa

---

### image_angles(image_path, bike_vector, body_vector, foot_length, (inference_count = 10), (ankle_angle = 105), (arm_angle = 150))

**Description:**
* Calculates the predicted user dimensions, angles, and knee over pedal spindle (KOPS) for a given image and bike vector.

**Input:**
- image_path: Path to image
- bike_vector
- body_vector
- foot_length 
- (optional) inference_count: Number of times to run inference on image (higher values may take longer but may be more accurate)
- (optional) ankle_angle in **degrees**
- (optional) arm_angle in **degrees**

**Output:**
- Tuple of (user, angles, kops)
  - user = predicition dictionary
  - angles = tuple of knee extension angle, back angle, and armpit to wrist angle in **degrees** or None if inputs violate triangle inequality for certain angle
  - kops = horizontal knee position relative to center of pedal at 3 O'clock position

---
### bike_offset(bike_vector, thickness, setback)
**Description:**
Calculates the bike vector for a bike with a given seat thickness and setback.

**Input:**
- bike_vector
- thickness: Seat thickness
- setback: Seat setback distance

**Output:**
- New bike vector with seat x and seat y adjusted for thickness and setback. Does not mutate input vector.

---

### knee_extension_angle(bike_vector, body_vector, CA)
**Description:**
Calculates knee extension angle for a given bike and body system and at a specific crank angle (CA)

**Input:**
- bike_vector
- body_vector
- CA in **radians**

**Output:**
Knee extension angle in **radians** or None if inputs violate triangle inequality.

---

### back_armpit_angles(bike_vector, body_vector, arm_angle)
**Description:**
Calculates back angle and armpit to wrist angle for a given bike and body system and at a specific arm angle.

**Input:**
- bike_vector
- body_vector
- arm_angle in **degrees**

**Output:**
Tuple of back angle in **radians** and armpit to wrist angle in **radians** or None if inputs violate triangle inequality.

---

### all_angles(bike_vector, body_vector, arm_angle)
**Description:**
* Uses knee_extension_angle and back_armpit_angles to produce one tuple corresponding to the minimum knee extension angle, back angle, and armpit to wrist angle. 
* Minimum knee extension angle is calculated on a [0, 2π] interval and returns None if it ever violates the triangle inequality (the bike body system cannot complete a full rotation of the cranks). 

**Input:**
- bike_vector
- body_vector
- arm_angle in **degrees**

**Output:**
Tuple of minimum knee extension angle in **degrees**, back angle in **degrees**, and armpit to wrist angle in **degrees** or None if inputs violate triangle inequality for certain angle.

---
### kops(bike_vector, body_vector)
**Description:**
Calculates the horizontal knee position relative to center of pedal at 3 O'clock position for a given bike and body system.

**Input:**
- bike_vector
- body_vector

**Output:**
Horizontal knee position relative to center of pedal at 3 O'clock position.

---

### prob_dists(bike_vector, body_vector, arm_angle, use="road")
**Description:**
Uses all angles and USE_DICT to calculate probabilities of the angles in the given bike and body system using Gaussian curve and CDF. Returns None for angles that are None.

**Input:**
- bike_vector
- body_vector
- arm_angle in **degrees**
- use: String corresponding to usecase in USE_DICT ("road", "mtb", "commute")

**Output:**
Tuple of probabilities of minimum knee extension angle, back angle, and armpit to wrist angle or None if inputs violate triangle inequality for certain angle.

---
## Analysis Functions
---

### all_noise(bike_vector, body_vector, step_size, n)
**Description:**  
* Produces tables mapping noise in each dimension of the bike/body system to the respective change to knee extension angle, back angle, and armpit wrist angle.
* Produces “nan” if a test violated the triangle inequality.
* Note: arm_angle is defaulted to 150 degrees.

**Input:**
- bike_vector
- body_vector
- step_size: Step size of noise in each dimension
- n: Number of tests to run for each dimension

**Output:**
Prints noise table for each dimension of bike and body with 2n-1 rows in each table.

---

### analyze_folder(folder_path, users_dictionary)
**Description:**
* Analyzes all images in a folder and compares the predicted dimensions of the body to the actual dimensions of the body.
* Produces a table comparing the predicted and actual dimensions.
* Also produces a list of tuples of predicted dimension, actual dimension, and the pose overlayed image. 

**Input:**
- folder_path: Path to folder containing images
- users_dictionary: Dictionary mapping user name to dictionary with body dimensions mapped to their name.

**Output:**
Prints table comparing predicted and actual dimensions.
Returns list of tuples of predicted dimension, actual dimension, and the pose overlayed image.

---

### print_analyze_table(out)
**Description:**
* Prints table comparing the predicted and actual dimensions given the output_list from analyze_folder.

**Input:**
- output_list: List of tuples of predicted dimension, actual dimension, and the pose overlayed image from analyze_folder.

**Output:**
Prints table comparing predicted and actual dimensions.

---

### print_analyze_images(out)
**Description:**
* Prints images with pose overlayed given the output list from analyze_folder.

**Input:**
- output_list: List of tuples of predicted dimension, actual dimension, and the pose overlayed image from analyze_folder.

**Output:**
Prints images with pose overlayed.

---

### interface_points(bike, hbar_type = "drops")
**Description:**
* Calculates the interface points (for standard bike_vector) from structural bike vector (13 Dim).

**Input:**
- bike: Structural bike vector (13 Dim)
  - Bike np array:
    - (0,0): DT Len,
    - (0,1): HT Len
    - (0,2): HT Angle
    - (0,3): HT Lower Extension
    - (0,4): Stack Height
    - (0,5): ST Len
    - (0,6): ST Angle
    - (0,7): Seatpost Len
    - (0,8): Saddle height
    - (0,9): Stem Len
    - (0,1): Stem Angle
    - (0,1): Spacer Amt
    - (0,1): Crank Length
- hbar_type: String corresponding to handlebar type ("drops", "mtb", "bullhorn")

**Output:**
- Tuple of (hbar, saddle, pedal)
  - hbar = Handlebar interface point (x, y)
  - saddle = Saddle interface point (x, y)
  - crank length = Crank length