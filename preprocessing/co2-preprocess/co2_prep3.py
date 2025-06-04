import pandas as pd
import sys

print("✅ Script started.")
sys.stdout.flush()

try:
    df = pd.read_csv("C:/Users/Victus/Downloads/Co2_HEMISPHERE.csv")
except Exception as e:
    print("❌ Could not read hemisphere-labeled data:", e)
    sys.exit()
    
df.rename(columns={"Month_Num": "month", "Year": "year"}, inplace=True)

# Monthly hemisphere average
grouped = df.groupby(["year", "month", "Hemisphere"])["CO2_Emissions_Mt"].mean().reset_index()

# placing hemisphere names into separate columns
hemisphere_avg  = grouped.pivot (index=["year", "month"], columns="Hemisphere", values="CO2_Emissions_Mt").reset_index()
hemisphere_avg  =hemisphere_avg .rename(columns={"North": "north_co2_mt", "South": "south_co2_mt"})

# Save
hemisphere_avg.to_csv("C:/Users/Victus/Downloads/hemispheric_co2_monthly1.csv", index=False)
print(" Hemisphere monthly emissions file saved.")
# Load the hemispheric CO2 file
df = pd.read_csv("C:/Users/Victus/Downloads/hemispheric_co2_monthly1.csv")
# Calculate global emissions using the renamed columns
df["global_co2_mt"] = df["Northern"] + df["Southern"]
# Rename for clarity
df.rename(columns={
    "Northern": "north_co2_mt",
    "Southern": "south_co2_mt"
}, inplace=True)

# Reorder columns
df = df[["year", "month", "north_co2_mt", "south_co2_mt", "global_co2_mt"]]

# Save to file
df.to_csv("C:/Users/Victus/Downloads/glo_and_hem_emissions_co2.csv", index=False)
print(df.head(10))
print("Global and hemispheric CO2 emissions file saved.")