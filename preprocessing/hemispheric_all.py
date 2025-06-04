import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def load_dataset(path, label):
    try:
        df = pd.read_csv(path)
        print(f"{label} dataset loaded successfully: {df.shape[0]} records.")
        return df
    except Exception as e:
        print(f"Failed to load {label} dataset from {path}. Error: {e}")
        exit()

co2 = load_dataset("C:/Users/Victus/Downloads/co2_global_hemispheric_anomalies_cleaned1.csv", "CO2")
sea = load_dataset("C:/Users/Victus/Downloads/sea_hemispherical_monthly.csv", "Sea Level")
temp = load_dataset("C:/Users/Victus/Downloads/temp_hemisphere_monthly.csv", "Temperature")

# Select required columns from each dataset
co2 = co2[["year", "month", "north_co2_anomaly", "norm_north_co2", "south_co2_anomaly", "norm_south_co2"]]
sea = sea[["year", "month", "msl_mm_north", "msl_mm_south"]]
temp = temp[["year", "month", "north_land_ocean_anomaly", "south_land_ocean_anomaly","north_land_anomaly", "south_land_anomaly"]]

# Normalize sea level and temperature anomalies
scaler = MinMaxScaler()
sea["norm_msl_north"] = scaler.fit_transform(sea[["msl_mm_north"]])
sea["norm_msl_south"] = scaler.fit_transform(sea[["msl_mm_south"]])

temp["norm_north_land_ocean"] = scaler.fit_transform(temp[["north_land_ocean_anomaly"]])
temp["norm_south_land_ocean"] = scaler.fit_transform(temp[["south_land_ocean_anomaly"]])
temp["norm_north_land"] = scaler.fit_transform(temp[["north_land_anomaly"]])
temp["norm_south_land"] = scaler.fit_transform(temp[["south_land_anomaly"]])


print("First few rows of sea data after normalization:")
print(sea[["year", "month", "msl_mm_north", "norm_msl_north", "msl_mm_south", "norm_msl_south"]].head(3))
print("First few rows of temperature data after normalization:")
print(temp[["year", "month", "north_land_ocean_anomaly", "norm_north_land_ocean", "south_land_ocean_anomaly", "norm_south_land_ocean", "north_land_anomaly", "norm_north_land", "south_land_anomaly", "norm_south_land"]].head(3))
# Basic null check - just in case
if temp.isnull().any().any():
    print("Warning: Temperature dataset contains missing values!")
else:
    print("Temperature dataset no missing value.")
if sea.isnull().any().any():
    print("Warning: Sea level dataset contains missing values!")
else:
    print("Sea level dataset no missing value.")
# Merge all datasets on common year and month to align corresponding data across other variables 
merged = pd.merge(co2, sea, on=["year", "month"], how="inner")
merged = pd.merge(merged, temp, on=["year", "month"], how="inner")
print(f"Final merged dataset shape: {merged.shape}")

try:
    merged.to_csv("C:/Users/Victus/Desktop/New Folder/hemispheric_merged.csv", index=False)
    print("Saved hemispheric merged data")
except Exception as err:
    print("Failed to save merged data:", err)
