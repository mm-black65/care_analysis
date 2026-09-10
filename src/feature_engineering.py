import pandas as pd
import numpy as np


def add_time_features(df):
    """
    Add calendar and reporting-period features.
    """

    df = df.copy()

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.month_name()
    df["year_month"] = df["date"].dt.to_period("M").astype(str)
    df["day_of_week"] = df["date"].dt.day_name()

    return df


def add_pressure_features(df):
    """
    Calculate operational pressure indicators.
    """

    df = df.copy()

    df["cbp_net_pressure"] = (
        df["apprehended"] -
        df["transferred"]
    )

    df["hhs_net_pressure"] = (
        df["transferred"] -
        df["discharged"]
    )

    return df


def add_efficiency_features(df):
    """
    Calculate aggregate efficiency indicators.
    """

    df = df.copy()

    df["transfer_efficiency"] = np.where(
        df["cbp_custody"] > 0,
        df["transferred"] / df["cbp_custody"],
        np.nan
    )

    df["discharge_effectiveness"] = np.where(
        df["hhs_care"] > 0,
        df["discharged"] / df["hhs_care"],
        np.nan
    )

    return df


def create_features(df):
    """
    Create all derived analytical features.
    """

    df = add_time_features(df)
    df = add_pressure_features(df)
    df = add_efficiency_features(df)

    return df