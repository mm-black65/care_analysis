import pandas as pd
import numpy as np


def calculate_pressure_thresholds(df):
    """
    Calculate high-pressure thresholds using
    the 75th percentile.
    """

    return {
        "cbp_threshold":
            df["cbp_net_pressure"].quantile(0.75),

        "hhs_threshold":
            df["hhs_net_pressure"].quantile(0.75)
    }


def identify_high_pressure_periods(df):
    """
    Identify observations where operational pressure
    is above the 75th percentile.
    """

    df = df.copy()

    thresholds = calculate_pressure_thresholds(df)

    df["cbp_high_pressure"] = (
        df["cbp_net_pressure"] >=
        thresholds["cbp_threshold"]
    )

    df["hhs_high_pressure"] = (
        df["hhs_net_pressure"] >=
        thresholds["hhs_threshold"]
    )

    return df


def calculate_cumulative_pressure(df):
    """
    Calculate cumulative operational pressure.
    """

    df = df.copy()

    df["cbp_cumulative_pressure"] = (
        df["cbp_net_pressure"].cumsum()
    )

    df["hhs_cumulative_pressure"] = (
        df["hhs_net_pressure"].cumsum()
    )

    return df


def standardize_pressure(series):
    """
    Convert pressure values to z-scores.
    """

    std = series.std()

    if std == 0:
        return pd.Series(0, index=series.index)

    return (series - series.mean()) / std


def add_pressure_scores(df):
    """
    Add standardized CBP and HHS pressure scores.
    """

    df = df.copy()

    df["cbp_pressure_z"] = standardize_pressure(
        df["cbp_net_pressure"]
    )

    df["hhs_pressure_z"] = standardize_pressure(
        df["hhs_net_pressure"]
    )

    return df


def prepare_bottleneck_analysis(df):
    """
    Run the complete bottleneck analysis pipeline.
    """

    df = identify_high_pressure_periods(df)
    df = calculate_cumulative_pressure(df)
    df = add_pressure_scores(df)

    return df