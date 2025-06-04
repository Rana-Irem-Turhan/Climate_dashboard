import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np

""" calculation of the emissions of CO₂ baseline anomaly/ year f ilter/ fianlize"""
try:
    df = pd.read_csv("C:/Users/Victus/Downloads/glo_and_hem_emissions_co2.csv")
except Exception as e:
    print("Data file load error:", e)
    df= None
if df is not None and not df.empty:
    baseline_global = df[(df["year"] <= 2000)]["global_co2_mt"].mean()
    baseline_north = df[(df["year"] <= 2000)]["north_co2_mt"].mean()
    baseline_south = df[(df["year"] <= 2000)]["south_co2_mt"].mean()

    print(f"1970–2000 Baselines : Global= {baseline_global:.2f}, North= {baseline_north:.2f}, South= {baseline_south:.2f}")
    filtered = df[(df["year"] >= 1993) & (df["year"] <= 2023)].copy()
    filtered["global_co2_anomaly"] = filtered["global_co2_mt"] - baseline_global
    filtered["north_co2_anomaly"] = filtered["north_co2_mt"] - baseline_north
    filtered["south_co2_anomaly"] = filtered["south_co2_mt"] - baseline_south

    scaler = MinMaxScaler()
    try:
# making sure  no NaNs and at least two unique values for normalization
        for col in ["global_co2_anomaly", "north_co2_anomaly", "south_co2_anomaly"]:
            if filtered[col].isnull().any() or filtered[col].nunique() <= 1:
                raise ValueError(f"Column {col} has invalid data for normalization")

        filtered["norm_global_co2"] = scaler.fit_transform(filtered[["global_co2_anomaly"]])
        filtered["norm_north_co2"] = scaler.fit_transform(filtered[["north_co2_anomaly"]])
        filtered["norm_south_co2"] = scaler.fit_transform(filtered[["south_co2_anomaly"]])
    except ValueError as ve:
        print("Normalization skipped:", ve)
        filtered["norm_global_co2"] = np.nan
        filtered["norm_north_co2"] = np.nan
        filtered["norm_south_co2"] = np.nan

    
    final = filtered[[
        "year", "month",
        "global_co2_anomaly", "norm_global_co2",
        "north_co2_anomaly", "norm_north_co2",
        "south_co2_anomaly", "norm_south_co2"
    ]]

    
    final.to_csv("C:/Users/Victus/Downloads/co2_global_hemispheric_anomalies_cleaned1.csv", index=False)
    print(" Final co2 dataset saved")
