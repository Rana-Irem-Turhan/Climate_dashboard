import pandas as pd
def preprocess(df, label):
    df["time"] = pd.to_datetime(df["time"])
    df[f"msl_mm_{label}"] = df["msl"] * 1000
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    return df

try:
    north = pd.read_csv("sea_north.csv")
except FileNotFoundError:
    print("North hemisphere file not found.")
    exit()
try:
    south = pd.read_csv("sea_south.csv")
except Exception as e:
    print("South hemisphere file not found.")
    exit()

north = preprocess(north, "north")
south = preprocess(south, "south")


print("seperated time and converted units.")

# calculating mean sea level per month
north_avg = north.groupby(["year", "month"])["msl_mm_north"].mean().reset_index()
south_avg = south.groupby(["year", "month"])["msl_mm_south"].mean().reset_index()
# use 1993–2023 range
north_avg= north_avg[(north_avg["year"] >= 1993) & (north_avg["year"] <= 2023)]
south_avg= south_avg[(south_avg["year"] >= 1993) & (south_avg["year"] <= 2023)]
# merge the hemisphere in one file
merged_sea = pd.merge(north_avg, south_avg, on=["year", "month"], how="inner")

try:
    merged_sea.to_csv("C:/Users/Victus/Downloads/sea_hemispherical_monthly.csv", index=False)
    print("Combined hemispheric data saved.")
except:
    print("Could not save combined hemispheric file.")