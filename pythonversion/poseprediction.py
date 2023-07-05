### Imports
import numpy as np
import os
import sys
import tensorflow as tf


######## ENSURE MODEL IS DOWNLOADED ########
# Download model from TF Hub and check out inference code from GitHub
# !wget -q -O movenet_thunder.tflite https://tfhub.dev/google/lite-model/movenet/singlepose/thunder/tflite/float16/4?lite-format=tflite
# !git clone https://github.com/tensorflow/examples.git

pose_sample_rpi_path = os.path.join(
    os.getcwd(), "pythonversion/examples/lite/examples/pose_estimation/raspberry_pi"
)
sys.path.append(pose_sample_rpi_path)

# Load MoveNet Thunder model
import utils
from data import BodyPart
from ml import Movenet

movenet = Movenet(
    "pythonversion/examples/lite/examples/pose_estimation/raspberry_pi/movenet_thunder.tflite"
)


# Define function to run pose estimation using MoveNet Thunder.
# You'll apply MoveNet's cropping algorithm and run inference multiple times on
# the input image to improve pose estimation accuracy.
def detect(input_tensor, inference_count=10):
    """Runs detection on an input image.

    Args:
      input_tensor: A [height, width, 3] Tensor of type tf.float32.
        Note that height and width can be anything since the image will be
        immediately resized according to the needs of the model within this
        function.
      inference_count: Number of times the model should run repeatly on the
        same input image to improve detection accuracy.

    Returns:
      A Person entity detected by the MoveNet.SinglePose.
    """

    # Detect pose using the full input image
    movenet.detect(input_tensor.numpy(), reset_crop_region=True)

    # Repeatedly using previous detection result to identify the region of
    # interest and only croping that region to improve detection accuracy
    for _ in range(inference_count - 1):
        person = movenet.detect(input_tensor.numpy(), reset_crop_region=False)

    return person


##################
### Calculation ##
##################
def calculation(heights, imgroute, camheight, camdist, inference_count = 10, output_overlayed=True):
    z = imgroute
    image = tf.io.read_file(z)
    height = heights
    image = tf.io.decode_jpeg(image)
    pheight = image.get_shape()[0]
    person = detect(image, inference_count=inference_count)
    keys = []

    # Y-axis Distortion Correction
    def ydistortionWrapper(cheight, cdistance, sheight, numpixels):
        def ydistortion(pycoord):
            a1 = np.arctan2(cheight, cdistance)
            a2 = np.arctan2((sheight - cheight), cdistance)
            p2a = numpixels / (a1 + a2)
            a3 = (pheight - pycoord) / p2a

            return cdistance * (np.tan(a1) - np.tan(a1 - a3))

        return ydistortion

    # X-axis Distortion Correction
    def xdistortionWrapper(cheight, cdistance, sheight, numpixels):
        def xdistortion(pxcoord):
            a1 = np.arctan2(cheight, cdistance)
            a2 = np.arctan2((sheight - cheight), cdistance)
            p2a = numpixels / (a1 + a2)
            a3 = pxcoord / p2a
            return pxcoord * cdistance / p2a

        return xdistortion

    # Distance Calculation
    def distance1(x1, y1, x2, y2):
        ydis = ydistortionWrapper(camheight, camdist, heights, pheight)
        xdis = xdistortionWrapper(camheight, camdist, heights, pheight)
        v = np.sqrt(pow(xdis(x1) - xdis(x2), 2) + pow(ydis(y1) - ydis(y2), 2))
        return v

    # Index the points to an array
    while len(keys) == 0:
        for z1 in range(len(person.keypoints)):
            if z1 in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]:
                keys.append(person.keypoints[z1])

    d1 = distance1(
        keys[6].coordinate.x,
        keys[6].coordinate.y,
        keys[8].coordinate.x,
        keys[8].coordinate.y,
    )

    d2 = distance1(
        keys[7].coordinate.x,
        keys[7].coordinate.y,
        keys[9].coordinate.x,
        keys[9].coordinate.y,
    )

    e1 = distance1(
        keys[1].coordinate.x,
        keys[1].coordinate.y,
        keys[3].coordinate.x,
        keys[3].coordinate.y,
    ) + distance1(
        keys[3].coordinate.x,
        keys[3].coordinate.y,
        keys[5].coordinate.x,
        keys[5].coordinate.y,
    )
    e2 = distance1(
        keys[0].coordinate.x,
        keys[0].coordinate.y,
        keys[2].coordinate.x,
        keys[2].coordinate.y,
    ) + distance1(
        keys[2].coordinate.x,
        keys[2].coordinate.y,
        keys[4].coordinate.x,
        keys[4].coordinate.y,
    )

    f1 = distance1(
        keys[0].coordinate.x,
        keys[0].coordinate.y,
        keys[1].coordinate.x,
        keys[1].coordinate.y,
    )
    b1 = distance1(0, pheight, 0, keys[0].coordinate.y)
    b2 = distance1(0, pheight, 0, keys[1].coordinate.y)
    c2 = (
        distance1(
            keys[9].coordinate.x,
            keys[9].coordinate.y,
            keys[11].coordinate.x,
            keys[11].coordinate.y,
        )
        + d2
    )
    c1 = (
        distance1(
            keys[8].coordinate.x,
            keys[8].coordinate.y,
            keys[10].coordinate.x,
            keys[10].coordinate.y,
        )
        + d1
    )

    pred = [
        (((b1 + b2) / 2)),
        (((c1 + c2) / 2)),
        (((d1 + d2) / 2)),
        (((e1 + e2) / 2)),
        (f1),
    ]

    # Return prediction or (prediction, overlayed image) for use in analyze_and_display
    if output_overlayed:
        overlayed = utils.visualize(image.numpy(), [person])
        return (pred, overlayed)

    return pred


##################
## Analysis#######
##################
# from __future__ import print_function
# import pickle


## height of user and file path for image
def analyze(height, imgroute, camheight, camdist, inference_count=10):
    calc, overlayed = calculation(
        height, imgroute, camheight, camdist, output_overlayed=True, 
    inference_count=inference_count)
    calc = [height] + calc
    return (calc, overlayed)
    # Bypassing lin regression model
    # with open('/content/drive/MyDrive/Bike Pose Detection Folder/file.pkl', 'rb') as fid:
    #    reg = pickle.load(fid)
    #    calc, overlayed = calculation(height,imgroute, output_overlayed=True)
    #    ogpredict = [calc]
    #    prediction=reg.predict(ogpredict)
    #    final_prediction=[height,prediction[0][0],prediction[0][1],prediction[0][2],prediction[0][3]]
    #    return (ogpredict, overlayed)


#################
### Decompose ###
#################
def decompose_to_dictionary(prediction_array):
    """
    Input: Array format [B: shoulder height, C: Inseam, D: Thigh, E:Arm length, F: Eye to shoulder]
    DOES NOT MODIFY INPUT
    Output: Returns dictionary "dimension name": Value in inches
      INCLUDES OFFSET BY HEIGHT
    """
    base = {
        "height": prediction_array[0],
        "sh_height": prediction_array[1],
        "hip_to_ankle": (prediction_array[2]),
        "hip_to_knee": prediction_array[3],
        "shoulder_to_wrist": prediction_array[4],
        # "sh_width": prediction_array[5],
    }
    # GETTING OFFSETS
    # Ankle height from floor to lateral malleolus and grip center to wrist are the same ratio
    ankle_wrist_offset = 0.04 * base["height"]
    base["arm_len"] = base["shoulder_to_wrist"] + ankle_wrist_offset
    base["tor_len"] = base["sh_height"] - base["hip_to_ankle"] - ankle_wrist_offset
    base["low_leg"] = base["hip_to_ankle"] - base["hip_to_knee"] + ankle_wrist_offset
    base["up_leg"] = base["hip_to_knee"]

    return base
