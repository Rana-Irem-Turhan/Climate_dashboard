import pandas as pd

try:
    land_ocean = pd.read_csv("1850-2025.csv", comment="#")
except Exception as e:
    print("Error reading land_ocean file:", e)
    exit()
try:
    land = pd.read_csv("1850-2025 (1).csv", comment="#")
except Exception as er:
    print("Error reading land file:", er)
    exit()
# Renaming Anomaly columns similarly done to the  hemispheric file
land_ocean.rename(columns={"Anomaly": "land_ocean_anomaly"}, inplace=True)
land.rename(columns={"Anomaly": "land_anomaly"}, inplace=True)

# splitting date into two parts
for d in [land_ocean, land]:
    d["year"] = d["Date"] // 100
    d["month"] = d["Date"] % 100
print("Year/month split done.", land_ocean.shape, land.shape)
# Merge them on year and month
merged_temp = pd.merge(
    land_ocean[["year", "month", "land_ocean_anomaly"]],land[["year", "month", "land_anomaly"]],on=["year", "month"],how="inner")


#get only same year range as hemispherical file
final = merged_temp[(merged_temp["year"] >= 1993) & (merged_temp["year"] <= 2023)]

# Check for -999 this means missing in any anomaly columns
contains_missing = (final["land_ocean_anomaly"] == -999).any() or \
                   (final["land_anomaly"] == -999).any()
print("Has -999s?", contains_missing)

try:
    final.to_csv("C:/Users/Victus/Downloads/temp_global_monthly.csv", index=False)
    print("Exported to CSV.")
except Exception as err:
    print("Failed to save:", err)
