import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Load up the main cleaned dataset for this analysis phase
df = pd.read_csv("cleaned_chicago_crime_dataset.csv")

# Ensure the date column is parsed as a proper datetime object
df["date"] = pd.to_datetime(df["date"])


# =====================================================================
# 1. CRIME INTENSITY BY TIME OF DAY
# =====================================================================
print("--- 1. HOUR OF DAY ANALYSIS ---")

# Pull out the hour from our datetime field to spot daily cycles
df["Hour"] = df["date"].dt.hour

# Calculate total reported crimes grouped by each hour block
crimes_by_hour = df.groupby("Hour").size()
print("Crimes recorded per hour:\n", crimes_by_hour)

# Generate a line chart to visualize peak crime hours across the city
plt.figure(figsize=(10, 5))
plt.plot(
    crimes_by_hour.index, crimes_by_hour.values, marker="o", color="crimson"
)
plt.title("Crime Intensity by Hour")
plt.xlabel("Hour of Day (24-Hour Format)")
plt.ylabel("Crime Count")
plt.grid(True)
plt.show()
print("=" * 50)


# =====================================================================
# 2. COMMUNITY AREA ANALYSIS & GEOGRAPHIC OUTLIERS
# =====================================================================
print("\n--- 2. GEOGRAPHIC DISTRIBUTION AND OUTLIERS ---")

# Group records to count how many crimes happened in each community area
community_counts = df.groupby("community_code").size()

# Grab the mathematical average of crimes per community using NumPy
mean_crimes = np.mean(community_counts)
print("Average (Mean) Crime Count across communities:", mean_crimes)

# Throw the distribution into a boxplot to see the spread and identify outliers visually
plt.figure(figsize=(10, 5))
plt.boxplot(community_counts, vert=False)
plt.title("Distribution of Crime Counts per Community Area")
plt.xlabel("Crime Count")
plt.show()

# Mathematically pin down outliers using the Interquartile Range (IQR) method
Q1 = community_counts.quantile(0.25)
Q3 = community_counts.quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

# Filter communities that fall beyond typical thresholds
outliers = community_counts[
    (community_counts < lower) | (community_counts > upper)
]
print("\nCommunity areas flagging unusually high/outlier crime activity:\n", outliers)
print("=" * 50)


# =====================================================================
# 3. FEATURE CROSS-CORRELATION
# =====================================================================
print("\n--- 3. CROSS-CORRELATION MATRIX ---")

# Pull out target numeric variables and identifiers to check for linear relationships
numeric_df = df[
    [
        "year",
        "Month",
        "arrest",
        "domestic",
        "beat_num",
        "district_code",
        "ward_no",
        "community_code",
    ]
]

# Calculate the correlation coefficients matrix
corr_matrix = numeric_df.corr()
print("Correlation Matrix:\n", corr_matrix)

# Visualize relationships with a color-coded heatmap (coolwarm makes negatives/positives stand out)
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1)
plt.title("Crime Feature Correlation Matrix")
plt.tight_layout()
plt.show()

print("\nAll advanced analysis modules run successfully!")