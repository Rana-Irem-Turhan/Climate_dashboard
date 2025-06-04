import pandas as pd

north_land_ocean = pd.read_csv("1850-2025 (4).csv", comment="#")
north_land = pd.read_csv("1850-2025 (3).csv", comment="#")
south_land_ocean = pd.read_csv("1850-2025 (6).csv", comment="#")
south_land = pd.read_csv("1850-2025 (5).csv", comment="#")
# Manually checked the datasets files heading to ensure the name of the columns are correct and aligns 
# Renaming Anomaly columns for make it easier before merging
north_land_ocean.rename(columns={"Anomaly": "north_land_ocean_anomaly"}, inplace=True)
north_land.rename(columns={"Anomaly": "north_land_anomaly"}, inplace=True)
south_land_ocean.rename(columns={"Anomaly": "south_land_ocean_anomaly"}, inplace=True)
south_land.rename(columns={"Anomaly": "south_land_anomaly"}, inplace=True)
# Extracting year and month from 'Date' column in every datasets
for t in [north_land_ocean, south_land_ocean, north_land, south_land]:
    t["year"] = t["Date"] // 100
    t["month"] = t["Date"] % 100

print("Loaded and renamed datasets", t)
# combining them on year and month to align the datasets
temp1 = pd.merge(
    north_land_ocean[["year", "month", "north_land_ocean_anomaly"]],
    south_land_ocean[["year", "month", "south_land_ocean_anomaly"]],
    on=["year", "month"],
    how="inner"
)

temp2 = pd.merge(
    temp1,
    north_land[["year", "month", "north_land_anomaly"]],
    on=["year", "month"],
    how="inner"
)

merged_temp = pd.merge(
    temp2,
    south_land[["year", "month", "south_land_anomaly"]],
    on=["year", "month"],
    how="inner"
)

print("\nCombined data shape:", merged_temp.shape)

# Year filter to get exact data range
final = merged_temp[(merged_temp["year"] >= 1993) & (merged_temp["year"] <= 2023)]

# Checking if any values are marked as -999 indicates missing entries
missing = (final["north_land_ocean_anomaly"] == -999).any() or \
            (final["south_land_ocean_anomaly"] == -999).any() or \
            (final["south_land_anomaly"] == -999).any() or \
            (final["north_land_anomaly"] == -999).any()

print("Any missing flags (-999)?", missing)

# Saving it 
final.to_csv("C:/Users/Victus/Downloads/temp_hemisphere_monthly.csv", index=False)
print("Done.")