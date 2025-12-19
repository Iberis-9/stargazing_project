import pandas as pd

def locations_to_df(hits: list, country: str = "Sweden") -> pd.DataFrame:
    """
    Keep only useful columns + filter to Sweden + build a UI label.
    Returns empty df if no matches.
    """
    df = pd.DataFrame(hits)
    if df.empty:
        return df

    keep = ["name", "region", "country", "lat", "lon"]
    df = df[[c for c in keep if c in df.columns]].copy()

    df = df[df["country"].eq(country)].copy()
    if df.empty:
        return df

    # Nice label for selectbox
    region = df["region"].fillna("").astype(str).str.strip()
    df["label"] = df["name"].astype(str) + region.radd(", ").replace(", ", "", regex=False)

    # Stable ordering
    df = df.sort_values(["name", "region"], na_position="last").reset_index(drop=True)
    return df