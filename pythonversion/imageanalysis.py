# Analyze all pictures in folder; name format: "[name]-[identifier]-[cam dist]-[cam height].jpg" can end in "".JPG" also
import glob
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
from angles import all_angles, deg_to_r, prob_dists
from poseprediction import decompose_to_dictionary, analyze
from kneeoverpedal import kops


# To print table from output of analyze_folder
def print_analyze_table(out):
    """
    Input: Output of analyze_folder
    Output: Prints table of results
    """
    # new out folder to discard numpy images
    new_out = [line[:-1] for line in out]
    print(
        tabulate(
            new_out,
            headers=[
                "file",
                "pred torso",
                "pred upleg",
                "pred lowleg",
                "pred arm",
                "dtorso",
                "dupleg",
                "dlowleg",
                "darm",
                "avgdif",
            ],
        )
    )


def display_images(input_list, save_path=None):
    """Displays images in input list: [image, title, differences]"""
    rows = int(len(input_list) / 2) + 1
    columns = 2
    plt.rcParams["figure.figsize"] = [16, 6 * rows]
    plt.rcParams["figure.autolayout"] = True

    for i, tup in enumerate(input_list):
        # adds overlay and title to img plot
        plt.subplot(rows, columns, i + 1)
        plt.axis("off")
        plt.imshow(tup[0])
        plt.title(tup[1])
        plt.text(0, 60, tup[2], fontsize="x-large", color="grey")

    if save_path:
        plt.savefig(save_path)
        plt.clf() #clear fig so things don't overlap
        return
    plt.show()


# To display images from output of analyze_folder
def display_analyze_images(out, save_path=None):
    """
    Input: Output of analyze_folder
    Output: Displays images of results
    """
    new_out = []
    for line in out:
        img = line[-1]
        x_label = line[0]
        title = f"dtorso: {round(line[5], 2)}, dupleg: {round(line[6], 2)}, dlowleg: {round(line[7], 2)}, darm: {round(line[8], 2)}, avgdif: {round(line[9], 2)}"
        new_out.append((img, title, x_label))
    display_images(new_out, save_path=save_path)


def analyze_folder(folder, users, display_images=False, save_path=None):
    """
    Input:
        1. Folder of pics
              IMPORTANT: name format: "[name]-[identifier]-[cam dist]-[cam height].jpg"
        2. User dimensions dictionary: {"name": {"height": height... "torso", "upleg", "lowleg", "arm"}}
    Output:
      Prints table: Picure Name: Predicted Dimensions | Difference From Actual Dimensions
      Returns: List of tuples corresponding to rows of table + POSE IMAGE AS NP ARRAY
        (file name, pred torso, pred upleg, pred lowleg, pred arm, dtorso, dupleg, dlowleg, darm, image)
    """
    # iterator for all pictures (end in .jpg) in folder path
    paths = glob.glob((folder + "/*.jpg")) + glob.glob((folder + "/*.JPG"))

    out = []
    for i, pic in enumerate(paths):
        # break up file name
        file_name = pic.split("/")[-1][:-4]
        file_name = file_name.split("-")

        # skip file if doesn't match format
        if len(file_name) != 4:
            continue

        name, identifier, camheight, camdist = file_name
        camheight = int(camheight)
        camdist = int(camdist)
        print(f"Processing: {i}/{len(paths)}: {pic}")

        if name in users:
            # run model on file
            result, overlayed = analyze(users[name]["height"], pic, camheight, camdist)
            pred = decompose_to_dictionary(result)

            # calculate difference pred - real value
            dtorso = pred["tor_len"] - users[name]["torso"]
            dupleg = pred["up_leg"] - users[name]["upleg"]
            dlowleg = pred["low_leg"] - users[name]["lowleg"]
            darm = pred["arm_len"] - users[name]["arm"]
            # using square distance instead of avg
            davg = np.sqrt(dtorso**2 + dupleg**2 + dlowleg**2 + darm**2)

            # store to output list
            line = (
                (name + "-" + identifier),
                pred["tor_len"],
                pred["up_leg"],
                pred["low_leg"],
                pred["arm_len"],
                dtorso,
                dupleg,
                dlowleg,
                darm,
                davg,
                overlayed,
            )
            out.append(line)

    # print table
    print_analyze_table(out)

    # display images if desired
    if display_images:
        display_analyze_images(out, save_path=save_path)

    return out

def sort_analysis(out, header="avgdif"):
    """
    Input: Output of analyze_folder
    Output: MUTATES input to be sorted by specified header
    """
    header_name = {
        "file": 0,
        "pred torso": 1,
        "pred upleg": 2,
        "pred lowleg": 3,
        "pred arm": 4,
        "dtorso": 5,
        "dupleg": 6,
        "dlowleg": 7,
        "darm": 8,
        "avgdif": 9,
    }
    # modify header_name to column of interest
    out.sort(key=lambda x: x[header_name[header]])
    return out

def dict_to_body_vector(user_dict, foot_len, ankle_angle):
    """
    Input: dict from decompose_to_dictionary, foot length, ankle angle degrees
    Output: body vector
    """
    return np.array([user_dict["low_leg"], user_dict["up_leg"], user_dict["tor_len"], user_dict["arm_len"], foot_len, deg_to_r(ankle_angle)]).reshape(6,1)

#Image to body dimensions and angles
def image_angles(height, img, bike, foot_len, camheight, camdist, ankle_angle = 105, arm_angle = 150, inference_count=10, output_overlayed = False):
    """ 
    Input: height, img, bike vector, foot length, ankle angle
    Output: body dimensions in user dict form, angles
    """
    print(f"Analyzing With Inference Count = {inference_count}: {img}")
    pred, overlayed = analyze(height, img, camheight, camdist, inference_count=inference_count)
    user = decompose_to_dictionary(pred)
    body = dict_to_body_vector(user, foot_len, ankle_angle)
    angles = all_angles(bike, body, arm_angle)
    kover = kops(bike, body)
    # print("\n Predicted Dims: ", user)
    # print("\n Predicted Angles: ", angles)
    # print("\n Probabiltiy of Angles", prob_dists(bike, body, arm_angle))
    # print("\n Predicted KOPS: ", kover)

    if output_overlayed:
        plt.imshow(overlayed)
        plt.show()
        return (user, angles, kover, overlayed)
    return (user, angles, kover)