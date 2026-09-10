import pandas as pd


COLUMN_MAPPING = {
    "Date": "date",
    "Children apprehended and placed in CBP custody*": "apprehended",
    "Children in CBP custody": "cbp_custody",
    "Children transferred out of CBP custody": "transferred",
    "Children in HHS Care": "hhs_care",
    "Children discharged from HHS Care": "discharged"
}


def load_raw_data(filepath):
    """
    Load the raw UAC dataset.
    """
    return pd.read_csv(filepath)


def clean_data(df):
    """
    Clean and standardize the UAC dataset.
    """

    df = df.copy()

    # Remove completely blank rows
    df = df.dropna(how="all").copy()

    # Rename columns
    df = df.rename(columns=COLUMN_MAPPING)

    # Convert date
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # Convert numeric columns
    numeric_columns = [
        "apprehended",
        "cbp_custody",
        "transferred",
        "hhs_care",
        "discharged"
    ]

    for column in numeric_columns:
        df[column] = (
            df[column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Sort chronologically
    df = df.sort_values("date").reset_index(drop=True)

    return df


def validate_data(df):
    """
    Perform basic data-quality checks.
    """

    validation = {
        "rows": len(df),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_dates": int(df["date"].duplicated().sum()),
        "negative_values": int(
            (df.select_dtypes(include="number") < 0)
            .sum()
            .sum()
        )
    }

    return validation


def save_cleaned_data(df, filepath):
    """
    Save the cleaned dataset.
    """
    df.to_csv(filepath, index=False)