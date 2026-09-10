import matplotlib.pyplot as plt


def plot_pipeline_activity(df):
    """
    Plot aggregate pipeline activity.
    """

    values = {
        "Apprehended": df["apprehended"].sum(),
        "Transferred": df["transferred"].sum(),
        "Discharged": df["discharged"].sum()
    }

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(
        values.keys(),
        values.values()
    )

    ax.set_title("Aggregate UAC Care Pipeline Activity")
    ax.set_ylabel("Children")

    fig.tight_layout()

    return fig


def plot_efficiency_trends(df):
    """
    Plot transfer and discharge efficiency.
    """

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        df["date"],
        df["transfer_efficiency"],
        label="Transfer Efficiency"
    )

    ax.plot(
        df["date"],
        df["discharge_effectiveness"],
        label="Discharge Effectiveness"
    )

    ax.set_title(
        "Transfer Efficiency and Discharge Effectiveness"
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Ratio")
    ax.legend()

    fig.tight_layout()

    return fig


def plot_pressure_trends(df):
    """
    Plot CBP and HHS operational pressure.
    """

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        df["date"],
        df["cbp_net_pressure"],
        label="CBP Net Pressure"
    )

    ax.plot(
        df["date"],
        df["hhs_net_pressure"],
        label="HHS Net Pressure"
    )

    ax.axhline(0, linewidth=1)

    ax.set_title("Operational Pressure Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Net Pressure")
    ax.legend()

    fig.tight_layout()

    return fig


def plot_temporal_activity(df):
    """
    Plot monthly transfer and discharge activity.
    """

    monthly = (
        df.groupby("year_month")
        [["transferred", "discharged"]]
        .sum()
    )

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        monthly.index,
        monthly["transferred"],
        label="Transferred"
    )

    ax.plot(
        monthly.index,
        monthly["discharged"],
        label="Discharged"
    )

    ax.set_title(
        "Monthly Transfer and Discharge Activity"
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Children")
    ax.legend()

    plt.xticks(rotation=45)

    fig.tight_layout()

    return fig