import pandas as pd

from src.data_cleaning import load_raw_data, clean_data, validate_data
from src.feature_engineering import create_features
from src.kpi_calculations import calculate_all_kpis
from src.bottleneck_analysis import prepare_bottleneck_analysis
from src.visualization import (
    plot_pipeline_activity,
    plot_efficiency_trends,
    plot_pressure_trends,
    plot_temporal_activity
)


# --------------------------------------------------
# 1. Load raw data
# --------------------------------------------------

raw_path = "data/raw/HHS_Unaccompanied_Alien_Children_Program.csv"

raw_df = load_raw_data(raw_path)

print("\nRAW DATA")
print("Shape:", raw_df.shape)


# --------------------------------------------------
# 2. Clean data
# --------------------------------------------------

df = clean_data(raw_df)

print("\nCLEANED DATA")
print("Shape:", df.shape)
print(df.head())


# --------------------------------------------------
# 3. Validate
# --------------------------------------------------

validation = validate_data(df)

print("\nVALIDATION")
for key, value in validation.items():
    print(f"{key}: {value}")


# --------------------------------------------------
# 4. Feature engineering
# --------------------------------------------------

df = create_features(df)

print("\nFEATURES CREATED")
print(df.columns.tolist())


# --------------------------------------------------
# 5. KPI calculations
# --------------------------------------------------

kpis = calculate_all_kpis(df)

print("\nKPI RESULTS")

for key, value in kpis.items():
    if isinstance(value, float):
        print(f"{key}: {value:.4f}")
    else:
        print(f"{key}: {value}")


# --------------------------------------------------
# 6. Bottleneck analysis
# --------------------------------------------------

df = prepare_bottleneck_analysis(df)

print("\nBOTTLENECK ANALYSIS")

print(
    "High CBP pressure periods:",
    df["cbp_high_pressure"].sum()
)

print(
    "High HHS pressure periods:",
    df["hhs_high_pressure"].sum()
)

print(
    "Maximum CBP pressure:",
    df["cbp_net_pressure"].max()
)

print(
    "Maximum HHS pressure:",
    df["hhs_net_pressure"].max()
)


# --------------------------------------------------
# 7. Visualization tests
# --------------------------------------------------

print("\nCREATING VISUALIZATIONS...")

fig1 = plot_pipeline_activity(df)
fig1.savefig("pipeline_test.png")

fig2 = plot_efficiency_trends(df)
fig2.savefig("efficiency_test.png")

fig3 = plot_pressure_trends(df)
fig3.savefig("pressure_test.png")

fig4 = plot_temporal_activity(df)
fig4.savefig("temporal_test.png")

print("\nALL TESTS COMPLETED SUCCESSFULLY!")
print("Generated:")
print("- pipeline_test.png")
print("- efficiency_test.png")
print("- pressure_test.png")
print("- temporal_test.png")