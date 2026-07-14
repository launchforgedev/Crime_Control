import base64
import io
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from flask import Flask, render_template_string, request
from sqlalchemy import create_engine, text

# Prevents GUI thread crashes inside headless VM environments
matplotlib.use("Agg")

app = Flask(__name__)

# Point directly to your local SQLite database file generated in the previous step
DB_URL = "sqlite:///chicago_crime.db"
db_engine = create_engine(DB_URL)

# HTML template with modern styling for a professional presentation
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CPD Predictive Crime Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }
        .container { max-width: 1100px; margin: 0 auto; }
        .header { background: #1a252f; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .grid { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; }
        .panel { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        h3 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #34495e; }
        input { width: 100%; padding: 10px; border: 1px solid #bdc3c7; border-radius: 4px; box-sizing: border-box; }
        button { background: #3498db; color: white; padding: 12px 20px; border: none; border-radius: 4px; width: 100%; cursor: pointer; font-size: 16px; font-weight: bold; }
        button:hover { background: #2980b9; }
        .badge { display: inline-block; padding: 6px 12px; font-weight: bold; border-radius: 4px; text-transform: uppercase; margin-bottom: 10px; }
        .badge-high { background-color: #e74c3c; color: white; }
        .badge-medium { background-color: #f39c12; color: white; }
        .badge-low { background-color: #2ecc71; color: white; }
        .recommendation-box { background: #ecf0f1; padding: 15px; border-left: 5px solid #3498db; border-radius: 4px; font-style: italic; }
        .chart-container { text-align: center; }
        .chart-img { max-width: 100%; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Chicago Police Department (CPD)</h2>
            <p>Tactical Resource Allocation & Near Real-Time Recommendation Engine</p>
        </div>

        <div class="grid">
            <div class="panel">
                <h3>Target Parameters</h3>
                <form method="POST" action="/">
                    <div class="form-group">
                        <label for="community_code">Community Area Code (1-77):</label>
                        <input type="number" id="community_code" name="community_code" value="{{ community_code }}" min="1" max="77" required>
                    </div>
                    <div class="form-group">
                        <label for="hour">Target Deployment Hour (0-23):</label>
                        <input type="number" id="hour" name="hour" value="{{ hour }}" min="0" max="23" required>
                    </div>
                    <button type="submit">Generate Strategy Recommendation</button>
                </form>
                
                {% if risk_level %}
                <div style="margin-top: 30px;">
                    <h3>Live Assessment</h3>
                    <span class="badge {% if 'HIGH' in risk_level %}badge-high{% elif 'MEDIUM' in risk_level %}badge-medium{% else %}badge-low{% endif %}">
                        {{ risk_level }}
                    </span>
                    <p><strong>Historical Hour Weight:</strong> {{ incident_count }} recorded incidents</p>
                    <div class="recommendation-box">
                        "{{ recommendation }}"
                    </div>
                </div>
                {% endif %}
            </div>

            <div class="panel chart-container">
                <h3>Localized Crime Trend Analysis</h3>
                {% if chart_url %}
                    <img class="chart-img" src="data:image/png;base64,{{ chart_url }}" alt="Hourly Crime Trend Chart">
                {% else %}
                    <p style="color: #7f8c8d; margin-top: 100px;">Submit target area codes to view granular visual reports.</p>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def dashboard():
    # Set fallback defaults for initial page render
    community_code = 25
    hour = 23
    risk_level = None
    recommendation = None
    incident_count = 0
    chart_url = None

    if request.method == "POST":
        community_code = int(request.form.get("community_code"))
        hour = int(request.form.get("hour"))

        # 1. Fetch metrics from SQLite using explicit cast tracking for text dates
        query_count = text("""
            SELECT COUNT(*) FROM crimes 
            WHERE CAST(community_code AS INT) = :comm 
            AND CAST(strftime('%H', date) AS INT) = :hour
        """)

        with db_engine.connect() as conn:
            incident_count = conn.execute(
                query_count, {"comm": community_code, "hour": hour}
            ).scalar()

        # 2. Heuristic rule matrix mapping weights to dynamic deployment recommendations
        if incident_count > 4:
            risk_level = "CRITICAL HIGH RISK"
            recommendation = "Deploy targeted preventive presence. High baseline risk of localized property/violent incidents."
        elif incident_count >= 2 and incident_count <= 4:
            risk_level = "ELEVATED MEDIUM RISK"
            recommendation = "Increase random patrol sweeps and maintain visibility at major transit/commercial junctions."
        else:
            risk_level = "STABLE LOW RISK"
            recommendation = "Maintain standard baseline monitoring. No additional tactical unit shifts required."

        # 3. Use Pandas + Matplotlib to build an on-the-fly visualization report
        query_trend = text("""
            SELECT CAST(strftime('%H', date) AS INT) as crime_hour, COUNT(*) as volume 
            FROM crimes 
            WHERE CAST(community_code AS INT) = :comm 
            GROUP BY crime_hour 
            ORDER BY crime_hour
        """)

        df_trend = pd.read_sql(
            query_trend, db_engine, params={"comm": community_code}
        )

        if not df_trend.empty:
            plt.figure(figsize=(7, 4))
            sns.lineplot(
                data=df_trend,
                x="crime_hour",
                y="volume",
                marker="o",
                color="#2c3e50",
                linewidth=2.5,
            )
            plt.axvline(
                x=hour,
                color="#e74c3c",
                linestyle="--",
                label=f"Selected Deployment Hour ({hour}:00)",
            )
            plt.title(
                f"24-Hour Historical Crime Profile: Community {community_code}",
                fontsize=12,
                fontweight="bold",
            )
            plt.xlim(0, 23)
            plt.xlabel("Hour of Day")
            plt.ylabel("Total Incidents")
            plt.grid(True, linestyle=":", alpha=0.6)
            plt.legend(loc="upper left")
            plt.tight_layout()

            # Encode plot data bytes to memory directly for HTML rendering without storing local images
            img = io.BytesIO()
            plt.savefig(img, format="png", bbox_inches="tight")
            img.seek(0)
            chart_url = base64.b64encode(img.getvalue()).decode("utf-8")
            plt.close()

    return render_template_string(
        DASHBOARD_TEMPLATE,
        community_code=community_code,
        hour=hour,
        risk_level=risk_level,
        recommendation=recommendation,
        incident_count=incident_count,
        chart_url=chart_url,
    )


if __name__ == "__main__":
    # Launch interactive web application framework pipeline locally
    app.run(host="0.0.0.0", port=5000, debug=True)