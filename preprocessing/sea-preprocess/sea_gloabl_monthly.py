import pandas as pd

""" It should read "sea_global.csv" otherwise  maybe due to it's missing or the path is wrong, it prints an error and exits.
 It converts the "time" column from a string to a datetime object so that it  easily extract the year and month later.
the mean sea level was initially in meters to ensure it is standard for climate studies, I have  converted these values to millimeters by multiplying by 1000.
 It extracts the year and month from the "time" column and adds them as new column to make it to group the data by month and year like the others.
 grouping by the year and the month script calculates the average sea level for each month by doing this we have new DataFrame with the average sea level for each month.
 filtered the grouped data to only include years from the range from 1993 to 2023.
"""
try:
    sea = pd.read_csv("sea_global.csv")
except:
    print("Couldn't read sea_global.csv")
    exit()

# datetime
sea["time"] = pd.to_datetime(sea["time"])

#  Convert msl to millimeters
sea["msl_mm"] = sea["msl"] * 1000

#  get the year and month
sea["year"] = sea["time"].dt.year
sea["month"] = sea["time"].dt.month

# average  mean sea level per month
monthly_sea_level = sea.groupby(["year", "month"])["msl_mm"].mean().reset_index()
# Filter to 1993–2023 range
monthly_sea= monthly_sea_level[(monthly_sea_level["year"] >= 1993) & (monthly_sea_level["year"] <= 2023)]


try:
    monthly_sea.to_csv("C:/Users/Victus/Downloads/sea_global_monthly.csv", index=False)
    print("Saved global sea level file.")
except Exception as err:
    print("Export failed:", err)