import os
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# =====================================================================
# 1. DESIGN & POPULATE SUMMARY TABLES (Adapted to SQLite)
# =====================================================================
print("--- Step 1: Designing & Populating Summary Tables ---")

db_name = "chicago_crime.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()
print(f"Connected Successfully to local database instance: {db_name}")

csv_filename = "cleaned_chicago_crime_dataset.csv"
if not os.path.exists(csv_filename):
    print(f"\nERROR: File '{csv_filename}' not found!")
    conn.close()
    exit()

df = pd.read_csv(csv_filename)

if "Year" in df.columns:
    df.drop(columns=["Year"], inplace=True)

df = df.where(pd.notnull(df), None)

cursor.execute("""
CREATE TABLE IF NOT EXISTS crimes (
    id INT,
    case_number VARCHAR(50),
    date DATETIME,
    block VARCHAR(255),
    iucr_code VARCHAR(20),
    primary_type VARCHAR(100),
    description VARCHAR(255),
    location_desc VARCHAR(255),
    arrest BOOLEAN,
    domestic BOOLEAN,
    beat_num INT,
    district_code INT,
    ward_no INT,
    community_code INT,
    fbi_code VARCHAR(20),
    x_coordinate FLOAT,
    y_coordinate FLOAT,
    year INT,
    date_of_update DATETIME,
    latitude FLOAT,
    longitude FLOAT,
    location TEXT,
    Month INT,
    DayOfWeek VARCHAR(20)
)
""")

for _, row in df.iterrows():
    sql = """
    INSERT INTO crimes VALUES (
        ?,?,?,?,?,?,?,?,?,?,
        ?,?,?,?,?,?,?,?,?,?,
        ?,?,?,?
    )
    """
    cursor.execute(sql, tuple(row))

conn.commit()
print("Staging data uploaded and tables populated successfully.")


# =====================================================================
# 2. SQL QUERIES (Directly Matching image_8e12e2.png Section 2)
# =====================================================================
print("\n--- Step 2: Running Targeted SQL Queries ---")

print("\n[A] Crime count per year:")
cursor.execute("""
SELECT year, COUNT(*) AS crime_count
FROM crimes
GROUP BY year
ORDER BY year
""")
for row in cursor.fetchall():
    print(f" Year: {row[0]} -> Total Crimes: {row[1]}")

print("\n[B] Top 5 crime types and their percentages:")
cursor.execute("""
SELECT primary_type,
       COUNT(*) AS total_crimes,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM crimes), 2) AS percentage
FROM crimes
GROUP BY primary_type
ORDER BY total_crimes DESC
LIMIT 5
""")
for row in cursor.fetchall():
    print(f" Type: {row[0]} | Count: {row[1]} | Percentage: {row[2]}%")

print("\n[C] Arrest count per year:")
cursor.execute("""
SELECT year, SUM(CASE WHEN arrest = 1 OR arrest = 'True' THEN 1 ELSE 0 END) AS arrest_count
FROM crimes
GROUP BY year
ORDER BY year
""")
for row in cursor.fetchall():
    print(f" Year: {row[0]} -> Successful Arrests: {row[1]}")


# =====================================================================
# 3. DATABASE STORED VIEWS & 4. PANDAS INTEGRATION
# =====================================================================
print("\n--- Step 3 & 4: Initializing Views and Syncing DataFrames ---")

# View 1: Yearly Volume
cursor.execute("DROP VIEW IF EXISTS vw_crime_yearly")
cursor.execute("""
CREATE VIEW vw_crime_yearly AS
SELECT year, COUNT(*) AS crime_count
FROM crimes
GROUP BY year
""")

# View 2: Category Volume
cursor.execute("DROP VIEW IF EXISTS vw_crime_by_category")
cursor.execute("""
CREATE VIEW vw_crime_by_category AS
SELECT primary_type, COUNT(*) AS total_crimes
FROM crimes
GROUP BY primary_type
""")

# View 3: Arrests Volume (Created to pass SQL data directly to Pandas for plotting)
cursor.execute("DROP VIEW IF EXISTS vw_arrests_yearly")
cursor.execute("""
CREATE VIEW vw_arrests_yearly AS
SELECT year, SUM(CASE WHEN arrest = 1 OR arrest = 'True' THEN 1 ELSE 0 END) AS arrest_count
FROM crimes
GROUP BY year
""")
conn.commit()

# Read views into Pandas DataFrames
yearly_df = pd.read_sql("SELECT * FROM vw_crime_yearly", conn)
category_df = pd.read_sql("SELECT * FROM vw_crime_by_category", conn)
arrests_df = pd.read_sql("SELECT * FROM vw_arrests_yearly", conn)


# =====================================================================
# 5. VISUALIZATION FROM DATABASE DATA 
# =====================================================================
print("\n--- Step 5: Launching Figure Windows via Matplotlib & Seaborn ---")

# --- CHART 1: Yearly Crime Volume Window ---
plt.figure(figsize=(10, 5))
sns.barplot(data=yearly_df, x="year", y="crime_count", palette="Blues_d")
plt.title("Crime Count Per Year", fontsize=14, fontweight="bold")
plt.xlabel("Year", fontsize=12)
plt.ylabel("Number of Crimes", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.7)

print(" -> Launching Year Volume popup window... (Close it to load next chart)")
plt.show() 


# --- CHART 2: Top 5 Crime Categories Window ---
plt.figure(figsize=(10, 5))
top5_categories = category_df.sort_values(by="total_crimes", ascending=False).head(5)
sns.barplot(data=top5_categories, x="total_crimes", y="primary_type", palette="viridis")
plt.title("Top 5 Broad Crime Categories", fontsize=14, fontweight="bold")
plt.xlabel("Total Crime Incidents", fontsize=12)
plt.ylabel("Crime Category Classification", fontsize=12)
plt.tight_layout()

print(" -> Launching Category Share popup window... (Close it to load next chart)")
plt.show() 


# --- CHART 3: Arrest Count Per Year Window ---
plt.figure(figsize=(10, 5))
# Using a line plot with markers to cleanly show trends over time
sns.lineplot(data=arrests_df, x="year", y="arrest_count", marker="o", color="#e74c3c", linewidth=2.5)
plt.title("Total Arrests Per Year", fontsize=14, fontweight="bold")
plt.xlabel("Year", fontsize=12)
plt.ylabel("Number of Successful Arrests", fontsize=12)
plt.grid(True, linestyle=":", alpha=0.6)

print(" -> Launching Arrest Trends popup window...")
plt.show() 


# =====================================================================
# CLEANUP DECONSTRUCTION
# =====================================================================
cursor.close()
conn.close()
print("\n[SUCCESS] Pipeline completed safely. All 3 figures displayed successfully.")