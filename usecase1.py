import numpy as np
import pandas as pd
from sqlalchemy import create_engine

# =====================================================================
# 1. CLEANING THE COMMUNITY DATASET
# =====================================================================

# Load up the community dataset
df_community = pd.read_csv(r"Chicago_Datasets_Python\chicago_city_community.csv")

# Quick look at what we're working with: size and column types
print("--- COMMUNITY DATASET INSPECTION ---")
print("Shape:", df_community.shape)


# Make column names consistent by trimming spaces and converting to lowercase
df_community.columns = df_community.columns.str.strip().str.lower()

# Let's see if there are any missing values hiding anywhere
print("\nMissing Values:\n", df_community.isnull().sum())

# Get rid of any exact duplicate rows
print("\nDuplicate Rows:", df_community.duplicated().sum())
df_community = df_community.drop_duplicates()

# Clean up text columns by stripping out random leading/trailing whitespaces
for col in df_community.select_dtypes(include="object").columns:
    df_community[col] = df_community[col].str.strip()

# Sanity check: making sure populations and areas aren't negative
print("\nNegative Population:\n", df_community[df_community["population"] < 0])
print("\nNegative Area:\n", df_community[df_community["area_sqmile"] < 0])

# Using IQR to spot any weird outliers in the population data
Q1 = df_community["population"].quantile(0.25)
Q3 = df_community["population"].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

outliers = df_community[
    (df_community["population"] < lower) | (df_community["population"] > upper)
]
print("\nPopulation Outliers:\n", outliers)

# Save our freshly cleaned community dataset to a new CSV
df_community.to_csv("cleaned_chicago_city_community.csv", index=False)
print("\nCommunity dataset cleaned successfully!\n" + "=" * 50)


# =====================================================================
# 2. CLEANING THE CRIME DATASET
# =====================================================================

# Load up the main crime dataset
df_crime = pd.read_csv(r"Chicago_Datasets_Python\chicago_crime_dataset.csv")

print("\n--- CRIME DATASET INSPECTION ---")
print(df_crime.head(10))
print("Rows, Columns:", df_crime.shape)
print(df_crime.info())

# Force date columns into actual datetime objects (bad dates turn into NaT)
df_crime["date"] = pd.to_datetime(df_crime["date"], errors="coerce")
df_crime["date_of_update"] = pd.to_datetime(
    df_crime["date_of_update"], errors="coerce"
)

# Where are we missing data?
print("\nMissing Values:\n", df_crime.isnull().sum())

# Let's look at missing data as percentages to make better decisions
missing_pct = (df_crime.isnull().sum() / len(df_crime)) * 100
print("\nMissing Percentage:\n", missing_pct.sort_values(ascending=False))

# If a column is missing more than half its data, it's not very useful. Drop it.
cols_to_drop = missing_pct[missing_pct > 50].index
df_crime.drop(columns=cols_to_drop, inplace=True)

# For missing text fields, we'll just flag them as "UNKNOWN"
cat_cols = df_crime.select_dtypes(include="object").columns
for col in cat_cols:
    df_crime[col] = df_crime[col].fillna("UNKNOWN")

# For missing numbers, fallback to the median value of that column
num_cols = df_crime.select_dtypes(include=["int64", "float64"]).columns
for col in num_cols:
    df_crime[col] = df_crime[col].fillna(df_crime[col].median())

# Drop identical rows if there are any
df_crime.drop_duplicates(inplace=True)

# Capitalize and strip text columns so everything matches perfectly
for col in cat_cols:
    df_crime[col] = df_crime[col].str.strip().str.upper()

# --- BREAKING OUT NEW FEATURES ---
# Pulling year, month, and day names out of our timestamp
df_crime["Year"] = df_crime["date"].dt.year
df_crime["Month"] = df_crime["date"].dt.month
df_crime["DayOfWeek"] = df_crime["date"].dt.day_name()

# --- NUMPY & POST-CLEANING CHECKS ---
# Double check missing percentages now that we've filled things in
missing_percentage = np.round((df_crime.isnull().sum() / len(df_crime)) * 100, 2)
print("\nPost-Clean Missing Percentage:\n", missing_percentage)

# Quick breakdowns of the unique crime classifications we have here
print("\nUnique Crime Types:", df_crime["primary_type"].nunique())
print("\nCrime Categories:\n", df_crime["primary_type"].unique())

# See if any rows ended up with broken/invalid dates
print("\nInvalid Dates:\n", df_crime[df_crime["date"].isnull()])

# Save the final cleaned crime dataset
df_crime.to_csv("cleaned_chicago_crime_dataset.csv", index=False)
print("\nCrime dataset cleaning completed successfully!\n" + "=" * 50)


# =====================================================================
# 3. CLEANING THE POLICE STATIONS DATASET
# =====================================================================

# Load the police station information
df_stations = pd.read_csv(
    r"Chicago_Datasets_Python\chicago_district_ps_info.csv"
)

print("\n--- POLICE STATIONS INSPECTION ---")
print(df_stations.head(10))
print(df_stations.shape)
print(df_stations.info())

# Drop column names to lowercase and trim spaces
df_stations.columns = df_stations.columns.str.strip().str.lower()

# Check if we have missing data gaps and eliminate duplicate entries
print("\nMissing Values:\n", df_stations.isnull().sum())
print("Duplicate Rows:", df_stations.duplicated().sum())
df_stations = df_stations.drop_duplicates()

# Strip out trailing spaces from text fields
for col in df_stations.select_dtypes(include="object").columns:
    df_stations[col] = df_stations[col].str.strip()

# Make sure the latitude and longitude ranges look sane
print("\nCoordinate Validation:\n", df_stations[["latitude", "longitude"]].describe())

# Save it to a clean CSV file
df_stations.to_csv("cleaned_chicago_district_ps_info.csv", index=False)
print("\nPolice stations dataset cleaned successfully!\n" + "=" * 50)


# =====================================================================
# 4. CLEANING THE POLICE BEATS DATASET
# =====================================================================

# Load the beat configuration data
df_beats = pd.read_csv(r"Chicago_Datasets_Python\chicago_police_beat_info.csv")

print("\n--- POLICE BEATS INSPECTION ---")
print(df_beats.head(10))
print("Rows, Columns:", df_beats.shape)
print(df_beats.info())

# Uniform column headers: lowercase and stripped of spaces
df_beats.columns = df_beats.columns.str.strip().str.lower()

# Print out counts for missing rows and duplicates
print("\nMissing Values:\n", df_beats.isnull().sum())
print("\nDuplicate Rows:", df_beats.duplicated().sum())
df_beats = df_beats.drop_duplicates()

print("\nData Types:\n", df_beats.dtypes)

# Trim text columns just in case there's hidden padding
for col in df_beats.select_dtypes(include="object").columns:
    df_beats[col] = df_beats[col].str.strip()

# Validation step: Districts, sectors, and beats shouldn't be zero or negative
print("\nInvalid Records Check:")
print(df_beats[df_beats["district"] <= 0])
print(df_beats[df_beats["sector"] <= 0])
print(df_beats[df_beats["beat_num"] <= 0])

# Save out the finished file
df_beats.to_csv("cleaned_chicago_police_beat_info.csv", index=False)
print("\nPolice beats dataset cleaned successfully!\n" + "=" * 50)


# =====================================================================
# 5. CLEANING THE WARD OFFICES DATASET
# =====================================================================

# Fetch the ward offices data
df_wards = pd.read_csv(r"Chicago_Datasets_Python\chicago_ward_offices.csv")

print("\n--- WARD OFFICES INSPECTION ---")
print(df_wards.head(10))
print("Shape:", df_wards.shape)
print(df_wards.info())

# Standardize column headers
df_wards.columns = df_wards.columns.str.strip().str.lower()

# Spot missing values and drop exact duplicates
print("\nMissing Values:\n", df_wards.isnull().sum())
print("\nDuplicate Rows:", df_wards.duplicated().sum())
df_wards = df_wards.drop_duplicates()

# Clean up all text fields by removing extra spaces
for col in df_wards.select_dtypes(include="object").columns:
    df_wards[col] = df_wards[col].str.strip()

# Quick manual look at contact details to verify their format looks okay
print("\nContact Fields Sample:")
print(df_wards["email"].head())
print(df_wards["website"].head())

# Export the clean file
df_wards.to_csv("cleaned_chicago_ward_offices.csv", index=False)
print("\nWard offices dataset cleaned successfully!\n" + "=" * 50)


# =====================================================================
# 6. CLEANING THE IUCR CODES DATASET
# =====================================================================

# Load up the internal Illinois Uniform Crime Reporting codes dataset
df_iucr = pd.read_csv(r"Chicago_Datasets_Python\iucr_codes.csv")

print("\n--- IUCR CODES INSPECTION ---")
print(df_iucr.head(10))
print("Shape:", df_iucr.shape)
print(df_iucr.info())

# Standardize the headers
df_iucr.columns = df_iucr.columns.str.strip().str.lower()

# Track down nulls and duplicates
print("\nMissing Values:\n", df_iucr.isnull().sum())
print("\nDuplicate Rows:", df_iucr.duplicated().sum())
df_iucr = df_iucr.drop_duplicates()

# Standardize text columns to uppercase and trim spaces
for col in df_iucr.select_dtypes(include="object").columns:
    df_iucr[col] = df_iucr[col].str.strip().str.upper()

# Ensure that numeric IUCR codes are valid and positive
print("\nInvalid IUCR Codes:\n", df_iucr[df_iucr["iucr_code"] <= 0])

# See how many unique broad crime types we have mapped here
print("Unique Crime Types:", df_iucr["primary_type"].nunique())

# Export our finalized codes dataset
df_iucr.to_csv("cleaned_iucr_codes.csv", index=False)
print("\nIUCR codes dataset cleaned successfully!\n" + "=" * 50)


# =====================================================================
# 7. LOADING TO SQLITE DATABASE
# =====================================================================

print("\n--- LOADING CLEANED DATA TO SQLITE ---")

# Initialize connection to our local SQLite database file
engine = create_engine("sqlite:///chicago_crime.db")

# Load our freshly minted clean crime data back from storage
df_to_load = pd.read_csv("cleaned_chicago_crime_dataset.csv")

# We don't need 'Year' as a standalone column if we already have the full timestamp
if "Year" in df_to_load.columns:
    df_to_load.drop(columns=["Year"], inplace=True)

# Stream the data straight into the 'crimes' table inside SQLite
df_to_load.to_sql(name="crimes", con=engine, if_exists="replace", index=False)
print("Data inserted successfully into 'crimes' table!")

# Verification step: Write a quick query to fetch the top 5 rows
query = "SELECT * FROM crimes LIMIT 5"
result = pd.read_sql(query, engine)

# Print results to make sure everything looks right inside the DB
print("\nDatabase Sample Check (Top 5 rows):\n", result)
print("\nAll pipeline tasks executed successfully!")