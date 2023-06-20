# Analyze all pictures in folder; name format: "[name]-[identifier]-[cam dist]-[cam height].jpg"
import glob
from tabulate import tabulate
def analyze_folder(folder, users):
  """
  Input:
      1. Folder of pics
            IMPORTANT: name format: "[name]-[identifier]-[cam dist]-[cam height].jpg"
      2. User dimensions dictionary: {"name": {"height": height... "torso", "upleg", "lowleg", "arm"}}
  Output: 
    Prints table: Picure Name: Predicted Dimensions | Difference From Actual Dimensions
    Returns: List of tuples corresponding to rows of table
      (file name, pred torso, pred upleg, pred lowleg, pred arm, dtorso, dupleg, dlowleg, darm)
  """
  #iterator for all pictures (end in .jpg) in folder path
  paths = glob.iglob((folder + "/*.jpg"))

  out = []
  for pic in paths:
    #break up file name
    file_name = pic.split("/")[-1][:-4]
    file_name = file_name.split("-")
    
    #skip file if doesn't match format
    if len(file_name) != 4:
        continue
    
    name, identifier, camx, camy = file_name
    print("Processing:", pic)

    if name in users:
      #run model on file
      result = analyze(users[name]["height"], pic)
      pred = decompose_to_dictionary(result)

      #calculate difference pred - real value
      dtorso = pred["tor_len"] - users[name]["torso"]
      dupleg = pred["up_leg"] - users[name]["upleg"]
      dlowleg = pred["low_leg"] - users[name]["lowleg"]
      darm = pred["arm_len"] - users[name]["arm"]

      #store to output list
      line = ((name + "-" + identifier), pred["tor_len"], pred["up_leg"], pred["low_leg"], pred["arm_len"], dtorso, dupleg, dlowleg, darm)
      out.append(line)

  print(tabulate(out, headers = ["file", "pred torso", "pred upleg", "pred lowleg", "pred arm", "dtorso", "dupleg", "dlowleg", "darm"]))
  return out