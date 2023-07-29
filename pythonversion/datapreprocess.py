import pandas as pd
import numpy as np
from interfacepoints import interface_points
from vectorizedangles import all_angles,prob_dists


bike_vector_df = pd.read_csv("/Users/noahwiley/Documents/Bike UROP/MeasureML-main/Frame Datasets/bike_vector_df_with_id.csv")
# Col with down tube length
#print("bike_vector_df\n", bike_vector_df)
without_id_array = bike_vector_df.iloc[:, 2:].values
#print("without_id_array", without_id_array)
int_point_array = interface_points(without_id_array)
int_point_df = pd.DataFrame(columns=["hand_x", "hand_y", "seat_x", "seat_y", "crank_length"])
for i, col in enumerate(["hand_x", "hand_y", "seat_x", "seat_y", "crank_length"]):
    int_point_df[col] = int_point_array[:, i]
print("int_point_df\n", int_point_df)
combined_df = bike_vector_df.merge(int_point_df, left_index=True, right_index=True, how="inner")

combined_df.to_csv("/Users/noahwiley/Documents/Bike UROP/MeasureML-main/Frame Datasets/bikes_with_int_points.csv")

print(combined_df[np.isnan(combined_df["hand_x"])])