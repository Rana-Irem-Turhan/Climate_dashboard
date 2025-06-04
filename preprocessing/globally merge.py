import pandas as pd
from sklearn.preprocessing import MinMaxScaler

try:
    sea = pd.read_csv("C:/Users/Victus/Downloads/sea_global_monthly.csv")
except Exception as e:
    print("Error reading sea file:", e)
    exit()
try:
    temp= pd.read_csv("C:/Users/Victus/Downloads/temp_global_monthly.csv")
except Exception as er:
    print("Error reading temperature file:", er)
    exit()
try:
    co2 = pd.read_csv("C:/Users/Victus/Downloads/co2_global_hemispheric_anomalies_cleaned1.csv")
except Exception as err:
    print("Error reading co2 file:", err)
    exit()

# Normalize sea level and temperature anomalies
scaler = MinMaxScaler()
sea["norm_sea_level"] = scaler.fit_transform(sea[["msl_mm"]])

temp["norm_land_ocean_temp"] = scaler.fit_transform(temp[["land_ocean_anomaly"]])
temp["norm_land_temp"] = scaler.fit_transform(temp[["land_anomaly"]])

#before the merging making sure everything looks column names looks correct and ther eis no missing values in btoh datasets tem and sea level 
print("First few rows of sea data after normalization:")
print(sea[["year", "month", "msl_mm", "norm_sea_level"]].head(3))
print("First few rows of temperature data after normalization:")
print(temp[["year", "month", "land_ocean_anomaly", "norm_land_ocean_temp", "land_anomaly", "norm_land_temp"]].head(3))
# Basic null check - just in case
if temp.isnull().any().any():
    print(" Temperature dataset contains missing values!")
else:
    print("Temperature dataset no missing value.")
if sea.isnull().any().any():
    print(" Sea level dataset contains missing values!")
else:
    print("Sea level dataset no missing value.")
# excludign unnecesaary columns for global merging
co2= co2.drop(columns=["north_co2_anomaly", "norm_north_co2", "south_co2_anomaly", "norm_south_co2"])
# Merge all datasets on common year and month to align corresponding data across other variables 
merged = pd.merge(co2, sea, on=["year", "month"], how="inner")
merged = pd.merge(merged, temp, on=["year", "month"], how="inner")
print(f"\n Final merged dataset: {merged.shape[0]} rows, {merged.shape[1]} columns.")

try:
    merged.to_csv("C:/Users/Victus/Desktop/New Folder/global_merged.csv", index=False)
    print("Saved global merged data")
except Exception as err:
    print("Failed to save merged data:", err)

