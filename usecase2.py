import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Let's get the cleaned dataset loaded in first
df = pd.read_csv("cleaned_chicago_crime_dataset.csv")

# =====================================================================
# 1. CRIME TREND OVER THE YEARS
# =====================================================================
print("--- 1. CRIME TRENDS OVER TIME ---")

# Group data by year to get total counts per year
crime_per_year = df.groupby("year").size()
print("Crimes per year:\n", crime_per_year)

# Plot a simple line chart to see if crime is rising or falling
plt.figure(figsize=(10, 5))
crime_per_year.plot(marker="o", color="b")
plt.title("Total Crimes Per Year")
plt.xlabel("Year")
plt.ylabel("Number of Crimes")
plt.grid(True)
plt.show()

# Quick calculation to see year-over-year percentage shifts
print("\nYear-over-Year Percentage Change:")
print(crime_per_year.pct_change() * 100)
print("=" * 50)


# =====================================================================
# 2. CRIME DISTRIBUTION BY CATEGORY
# =====================================================================
print("\n--- 2. CRIME BREAKDOWN BY CATEGORY ---")

# Grab the raw counts for the top 10 most common crimes
top10 = df["primary_type"].value_counts().head(10)
print("Top 10 Crime Types (Counts):\n", top10)

# Convert those top 10 categories into percentage of total crimes
crime_percent = df["primary_type"].value_counts(normalize=True).mul(100).head(10)
print("\nTop 10 Crime Types (Percentages):\n", crime_percent)

# Throw this into a horizontal bar chart so it's easy to read
plt.figure(figsize=(12, 6))
sns.barplot(x=top10.values, y=top10.index, palette="viridis")
plt.title("Top 10 Crime Categories")
plt.xlabel("Count")
plt.ylabel("Crime Type")
plt.tight_layout()
plt.show()
print("=" * 50)


# =====================================================================
# 3. ARRESTS AND CRIME OUTCOMES
# =====================================================================
print("\n--- 3. ARREST OUTCOMES AND STATISTICS ---")

# What percentage of these reported crimes actually lead to an arrest?
arrest_rate = df["arrest"].mean() * 100
print(f"Overall Arrest Rate: {arrest_rate:.2f}%")

# Let's see the raw true/false split for arrests
arrest_counts = df["arrest"].value_counts()
print("\nArrest vs No Arrest Counts:\n", arrest_counts)

# A pie chart works well here to visualize the overall ratio
plt.figure(figsize=(6, 6))
plt.pie(
    arrest_counts,
    labels=arrest_counts.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=["#ff9999", "#66b3ff"],
)
plt.title("Arrest Outcomes")
plt.show()
print("=" * 50)


# =====================================================================
# 4. HEATMAP OF CRIME BY MONTH AND DAY OF WEEK
# =====================================================================
print("\n--- 4. TIME PATTERNS (MONTH VS DAY OF WEEK) ---")

# Making sure our days of the week follow logical chronological order, not alphabetical
day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

# Build a pivot table counting crime instances across months and days
heatmap_data = pd.pivot_table(
    df, index="DayOfWeek", columns="Month", values="id", aggfunc="count"
)
heatmap_data = heatmap_data.reindex(day_order)
print("Crime Pivot Table Matrix:\n", heatmap_data)

# Render the heatmap to easily spot dark spots/high-activity times
plt.figure(figsize=(12, 6))
sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlOrRd")
plt.title("Crime Frequency by Month and Day of Week")
plt.xlabel("Month")
plt.ylabel("Day Of Week")
plt.tight_layout()
plt.show()
print("=" * 50)


# =====================================================================
# 5. TOP COMMUNITY AREAS
# =====================================================================
print("\n--- 5. GEOGRAPHIC HOTSPOTS (COMMUNITY AREAS) ---")

# Identify the top 10 neighborhood community codes with the highest crime counts
top_communities = df["community_code"].value_counts().head(10)
print("Top 10 Hotspot Community Codes:\n", top_communities)

# Map these communities out visually on a bar chart
plt.figure(figsize=(10, 6))
sns.barplot(
    x=top_communities.index,
    y=top_communities.values,
    order=top_communities.index,
    palette="magma",
)
plt.title("Top 10 Community Areas by Crime Count")
plt.xlabel("Community Code")
plt.ylabel("Crime Count")
plt.show()
print("=" * 50)




print("\nAll analyses and visualization plots generated successfully!")