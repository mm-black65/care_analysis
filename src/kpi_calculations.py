import numpy as np


def calculate_transfer_efficiency(df):
    """
    Aggregate transfer efficiency.
    """
    total_custody = df["cbp_custody"].sum()

    if total_custody == 0:
        return np.nan

    return df["transferred"].sum() / total_custody


def calculate_discharge_effectiveness(df):
    """
    Aggregate discharge effectiveness.
    """
    total_hhs_care = df["hhs_care"].sum()

    if total_hhs_care == 0:
        return np.nan

    return df["discharged"].sum() / total_hhs_care


def calculate_pipeline_throughput(df):
    """
    Total discharges relative to total apprehensions.
    """
    total_apprehended = df["apprehended"].sum()

    if total_apprehended == 0:
        return np.nan

    return df["discharged"].sum() / total_apprehended


def calculate_average_pressure(df):
    """
    Calculate average CBP and HHS operational pressure.
    """

    return {
        "average_cbp_pressure": df["cbp_net_pressure"].mean(),
        "average_hhs_pressure": df["hhs_net_pressure"].mean()
    }


def calculate_outcome_stability(df):
    """
    Calculate coefficient of variation for
    aggregate efficiency indicators.
    """

    transfer_mean = df["transfer_efficiency"].mean()
    discharge_mean = df["discharge_effectiveness"].mean()

    transfer_cv = (
        df["transfer_efficiency"].std() / transfer_mean
        if transfer_mean != 0 else np.nan
    )

    discharge_cv = (
        df["discharge_effectiveness"].std() / discharge_mean
        if discharge_mean != 0 else np.nan
    )

    return {
        "transfer_efficiency_cv": transfer_cv,
        "discharge_effectiveness_cv": discharge_cv
    }


def calculate_all_kpis(df):
    """
    Return the complete KPI dictionary.
    """

    pressure = calculate_average_pressure(df)
    stability = calculate_outcome_stability(df)

    return {
        "total_apprehended": df["apprehended"].sum(),
        "total_transferred": df["transferred"].sum(),
        "total_discharged": df["discharged"].sum(),

        "transfer_efficiency":
            calculate_transfer_efficiency(df),

        "discharge_effectiveness":
            calculate_discharge_effectiveness(df),

        "pipeline_throughput":
            calculate_pipeline_throughput(df),

        **pressure,
        **stability
    }