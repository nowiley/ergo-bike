import numpy as np
from ultralytics import YOLO
from poseprediction import analyze, decompose_to_dictionary
from imageanalysis import dict_to_body_vector

#Using nano model for faster detection
GLOBAL_IMGCHECK_MODEL = YOLO("yolov8n.pt")

def image_check(image_path):
  """
  Checks for poorly formatted images or images that are not humans 
  using YOLO object detection and comparing box to total image size
  Input: input image
  Output: (True, confidence level)/(False, -1) if valid person detected/not detected
  """
  # Run model
  res = GLOBAL_IMGCHECK_MODEL.predict(image_path)[0]
  # List of tuples (x1, y1, x2, y2, conf, obj type)
  detected_objects = res.boxes.data
  #Orig height to compare 
  orig_height = res.orig_shape[0]

  for obj in detected_objects:
    # If person object not detected (obj[5] != 0)
    if obj[5] != 0:
      continue

    #Get height of detection box & conf level
    person_height = obj[1] - obj[3]
    conf = obj[4]

    if abs(person_height/orig_height) >= 0.8 and (conf > 0.5):
      return (True, float(conf))

  #If no people objects detected
    return (False, -1)


# Basic person check make sure all dimensions are reasonable
def basic_check(body):
    """
    Checks that body dimensions are reasonable
    Input: Body Vector in INCHES
    Body = [LL, UL, TL, AL, FL, AA, SW, HT]
    Output: (True, "okay") / (False, ["reason1", "reason2", ...])
    """
    reason_list = []
    # Check that all dimensions are positive and less than 100 inches
    if np.any((body < 0 ) or (body > 100)):
        reason_list.append("Negative dimensions or dimensions greater than 100 inches")

    # Check that torso is about 1/4 - 1/3 of total height
    if not (body[2] > body[7] * 0.25 and body[2] < body[7] * 0.33):
        reason_list.append("Torso is not between 1/4 and 1/3 of total height")
    
    # Check that 2 arm lengths plus shoulder width is about total height
    if not (body[3] * 2 + body[6] > body[7] * 0.85 and body[3] * 2 + body[6] < body[7] * 1.15):
        reason_list.append("2 arm lengths plus shoulder width is not within 15% total height")

    # Check that low leg and upper leg are about equal
    if not (body[0] > body[1] * 0.8 and body[0] < body[1] * 1.2):
        reason_list.append("Low leg is not within 20% of upper leg")
    
    # Return True if no reasons, else return False and reasons
    if len(reason_list) == 0:
        return (True, "okay")
    else:
        return (False, reason_list)
    