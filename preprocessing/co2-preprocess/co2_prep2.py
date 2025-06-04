import pandas as pd

co2 = pd.read_csv("cleaned_CO2_emissions.csv")
co2['Country'] = co2['Country'].astype(str).str.strip().str.replace(r"[\,\.\'_]", "", regex=True)

regions = pd.read_csv("C:/Users/Victus/Downloads/UNSD — Methodology.csv", delimiter=";")
regions.rename(columns={"Country or Area": "UN_Country"}, inplace=True)
# Mapping CO₂ names to UNSD standard
match_to_unsd = {
    "Serbia and Montenegro": "Serbia",
    "Macedonia the former Yugoslav Republic of": "North Macedonia",
    "Swaziland": "Eswatini",
    "Venezuela": "Venezuela (Bolivarian Republic of)",
    "United States": "United States of America",
    "United Kingdom": "United Kingdom of Great Britain and Northern Ireland",
    "TanzaniaUnited Republic of": "United Republic of Tanzania",
    "Korea Republic of": "Republic of Korea",
    "Korea Democratic Peoples Republic of": "Democratic People's Republic of Korea",
    "Netherlands": "Netherlands (Kingdom of the)",
    "Moldova Republic of": "Republic of Moldova",
    "Lao Peoples Democratic Republic": "Lao People's Democratic Republic",
    "Iran Islamic Republic of": "Iran (Islamic Republic of)",
    "Hong Kong": "China, Hong Kong Special Administrative Region",
    "Falkland Islands Malvinas": "Falkland Islands (Malvinas)",
    "Congo_the Democratic Republic of the": "Democratic Republic of the Congo",
    "Cote dIvoire": "Côte d’Ivoire",
    "Cape Verde": "Cabo Verde",
    "Bolivia": "Bolivia (Plurinational State of)",
    "Wallis and Futuna": "Wallis and Futuna Islands",
    "Micronesia Federated States of": "Micronesia (Federated States of)",
    "Reunion": "Réunion",
    "Taiwan_Province of China": "Taiwan",
    "Czech Republic": "Czechia",
    "Libyan Arab Jamahiriya": "Libya",
    "Virgin IslandsBritish": "British Virgin Islands",
    "Virgin IslandsUSA": "United States Virgin Islands"
}
co2['Country'] = co2['Country'].replace(match_to_unsd)

# Rename for merge
regions.rename(columns={"UN_Country": "Country", "Region Name": "Region", "Sub-region Name": "Subregion"}, inplace=True)

# Merge regions
merged = co2.merge(regions[["Country", "Region", "Subregion"]], on="Country", how="left")


# Subregion to hemisphere mapping for certain regions
subregion_to_hemisphere = {
    "Australia and New Zealand": "Southern",
    "Central Asia": "Northern",
    "Eastern Asia": "Northern",
    "Eastern Europe": "Northern",
    "Melanesia": "Southern",
    "Northern Africa": "Northern",
    "Northern America": "Northern",
    "Northern Europe": "Northern",
    "Southern Asia": "Northern",
    "Southern Europe": "Northern",
    "Western Asia": "Northern",
    "Western Europe": "Northern"
}

# now for the uncertain ones acc to the worldpopulation southern Hemisphere source adjustments
country_to_hemisphere = {
    "Kiribati": "Southern",
    "American Samoa": "Southern",
    "Cook Islands": "Southern",
    "French Polynesia": "Southern",
    "Samoa": "Southern",
    "Timor-Leste": "Southern",
    "Indonesia": "Southern",
    "Angola": "Southern",
    "Botswana": "Southern",
    
    "Burundi": "Southern",
    "Comoros": "Southern",
    "Democratic Republic of the Congo": "Southern",
    "Gabon": "Southern",
    "Lesotho": "Southern",
    "Madagascar": "Southern",
    "Malawi": "Southern",
    "Mauritius": "Southern",
    "Mozambique": "Southern",
    "Namibia": "Southern",
    "Rwanda": "Southern",
    "Saint Helena": "Southern",
    "South Africa": "Southern",
    "Eswatini": "Southern",
    "United Republic of Tanzania": "Southern",
    "Zambia": "Southern",
    "Zimbabwe": "Southern",
    "Argentina": "Southern",
    "Bolivia (Plurinational State of)": "Southern",
    "Brazil": "Southern",
    "Chile": "Southern",
    "Ecuador": "Southern",
    "Falkland Islands (Malvinas)": "Southern",
    "Peru": "Southern",
    "Uruguay": "Southern",

}
"""first assigning hemisphere using specific country mapping
 then i have assigned  remaining  using subregion mapping and
   if its still empty than assigning as Northern"""
merged["Hemisphere"] = merged["Country"].map(country_to_hemisphere)

merged["Hemisphere"] = merged["Hemisphere"].fillna(merged["Subregion"].map(subregion_to_hemisphere))


merged["Hemisphere"] = merged["Hemisphere"].fillna("Northern")

"""Find countries with missing hemisphere assignment
Check if any country is still unassigned"""
missing = merged[merged["Hemisphere"].isna()]
if not missing.empty:
    print("❌ Still missing Hemisphere:", missing["Country"].unique())
else:
    print("🎉 All countries have Hemisphere assigned based on updated rules!")

# Count and print how many countries are in each hemisphere
print("\n🌎 Hemisphere breakdown (unique countries):")
hemisphere_counts = merged.drop_duplicates(subset=["Country"])[["Country", "Hemisphere"]].value_counts()
print(hemisphere_counts)

print("\n✅ Total countries per hemisphere:")
print(merged[["Country", "Hemisphere"]].drop_duplicates().groupby("Hemisphere").count())

merged.to_csv("C:/Users/Victus/Downloads/Co2_HEMISPHERE.csv", index=False)
print(" Hemisphere tagging complete.")

