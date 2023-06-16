from angles import all_angles
from tabulate import tabulate
##### Noise Generation #####
def all_noise(bike, body, step_size, n):
  """
  Input: bike, body, step size, n output points
  Output: prints tables corresponding to dimension noise changes
  for all bike and body dimensions
  """

  def test_noise(dim_type, dimension_i):
    """
    Input: dimension type ("bike" or "body"), dimension index to test
    Output: Returns list of 2n-1 tuples: (new_dim value, new_t_angels values, noise amt, t_angles changes)
    """
    out = []
    step = step_size
    new_bike = bike[:,:]
    new_body = body[:,:]
    o_ke, o_ba, o_aw = all_angles(new_bike, new_body, 150)

    #Generate line for table that handles none values
    def line_gen(dim, noise_amt, ke, back, awrist):
      if ke is None:
        ke_dif = "NaN"
        new_ke = "NaN"
      else:
        ke_dif = ke-o_ke
        new_ke = ke

      if back is None:
        ba_dif = "NaN"
        new_back = "NaN"
      else:
        ba_dif = back-o_ba
        new_back = back

      if awrist is None:
        aw_dif = "NaN"
        new_awrist = "NaN"
      else:
        aw_dif = awrist-o_aw
        new_awrist = awrist

      return (dim, noise_amt, ke_dif, ba_dif, aw_dif, new_ke, new_back, new_awrist)

    #makes 2n - 1 Data Points
    for i in range(0, n):
      noise_amt = i * step

      if dim_type == "bike":
        #positive noise
        new_bike[dimension_i, 0] += noise_amt
        ke, back, awrist = all_angles(new_bike, new_body, 150)
        out.append(line_gen(new_bike[dimension_i, 0], noise_amt, ke, back, awrist))

        #negative noise
        new_bike[dimension_i, 0] -= (2*noise_amt)
        ke, back, awrist = all_angles(new_bike, new_body, 150)
        if i != 0:
          out.append(line_gen(new_bike[dimension_i, 0], -noise_amt, ke, back, awrist))

        #reset bike
        new_bike[dimension_i, 0] += noise_amt


      elif dim_type == "body":
        #positive noise
        new_body[dimension_i, 0] += noise_amt
        ke, back, awrist = all_angles(new_bike, new_body, 150)
        out.append(line_gen(new_body[dimension_i, 0], noise_amt, ke, back, awrist))


        #negative noise
        new_body[dimension_i, 0] -= (2*noise_amt)
        ke, back, awrist = all_angles(new_bike, new_body, 150)
        if i != 0:
          out.append(line_gen(new_body[dimension_i, 0], -noise_amt, ke, back, awrist))

        #reset body
        new_body[dimension_i, 0] += noise_amt

      else:
        raise ValueError("dim_type must be either 'bike' or 'body'", dim_type)

    out.sort(key = lambda x: x[1])
    print(tabulate(out, headers=["Dim Value", "Noise Amt", "ke dif", "back dif", "awrist diff", "ke", "back", "awrist"]))

  #dict for dimension
  bike_dims = {
      0: "Seat X",
      1: "Seat Y",
      2: "Handlebar X",
      3: "Handlebar Y",
  }
  body_dims = {
      0: "Lower Leg",
      1: "Upper Leg",
      2: "Torso Length",
      3: "Arm Length",
      4: "Foot Length",
      5: "Ankle Angle",
  }
  #bike noise
  print("#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*\n#*#*#*#*# BIKE NOISE #*#*#*#*#\n#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*")

  for key, name in bike_dims.items():
    print(f"\n ***** {name} Dimension *****")
    test_noise("bike", key)


  #body noise
  print("\n\n\n#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*\n#*#*#*#*# BODY NOISE #*#*#*#*#\n#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*")
  for key, name in body_dims.items():
    print(f"\n ***** {name} Dimension *****")
    test_noise("body", key)






