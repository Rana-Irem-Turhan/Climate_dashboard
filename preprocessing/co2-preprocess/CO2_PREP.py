import pandas as pd

try:
    # Pulling the data with where the header starts from row 10
    df = pd.read_excel("C:/Users/Victus/Downloads/IEA_EDGAR_CO2_m_1970_2023.xlsx", sheet_name="TOTALS BY COUNTRY", header=9)
except Exception as e:
    print("❌ Failed to load Excel sheet:", e)
    exit() 

# Just cleaning columns and choosing only rows includes CO₂ 
df.columns = df.columns.astype(str).str.strip()
co2 = df[df["Substance"] == "CO2"]
# Converting months structure from wide to long format
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

melted = co2.melt(
    id_vars=["Name", "Year"],
    value_vars=months,
    var_name="Month",
    value_name="CO2_Emissions_Gg"
)
# Conversion to megatonnes plus make monthly names to numbers
melted["CO2_Emissions_Mt"] = melted["CO2_Emissions_Gg"].astype(float) / 1000
month_nums = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
              'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
melted["Month_Num"] = melted["Month"].map(month_nums)

# organizing the columns for readability
final = melted[["Name", "Year", "Month_Num", "CO2_Emissions_Mt"]].copy()
final.rename(columns={"Name": "Country"}, inplace=True)
final.sort_values(by=["Country", "Year", "Month_Num"], inplace=True)


final.to_csv("cleaned_CO2_emissions.csv", index=False)
print("✅ Exported cleaned CO₂ file.")
# Get unique countries
unique_countries = sorted(final["Country"].dropna().unique())

print("Total countries:", len(unique_countries))
for country in unique_countries:
    print(country)