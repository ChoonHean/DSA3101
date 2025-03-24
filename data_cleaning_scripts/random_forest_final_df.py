import pandas as pd
from itertools import product


if __name__ == "__main__":
    # Load cleaned metadata and review datasets
    df_final_metadata = pd.read_csv("../dataset/cleaned_data/final_cleaned_metadata.csv")
    df_final_review = pd.read_csv("../dataset/cleaned_data/final_cleaned_review.csv")

    df_combined = df_final_metadata.merge(df_final_review, on=["parent_asin"], how="left")

    # Find min year,quarter and max year,quarter to build a full date table
    min_year = int(df_combined["year"].min())
    max_year = int(df_combined["year"].max())
    min_quarter = int(df_combined.loc[df_combined["year"] == min_year, "quarter"].min())
    max_quarter = int(df_combined.loc[df_combined["year"] == max_year, "quarter"].max())

    date_combinations = []
    year, quarter = min_year, min_quarter

    while (year < max_year) or (year == max_year and quarter <= max_quarter):
        date_combinations.append((year, quarter))
        if quarter == 4:
            year += 1
            quarter = 1
        else:
            quarter += 1

    full_date_table = pd.DataFrame(product(df_combined["cluster_label"].unique(), date_combinations),
                                   columns=["cluster_label", "date"])

    full_date_table[["year", "quarter"]] = pd.DataFrame(full_date_table["date"].tolist(), index=full_date_table.index)
    full_date_table.drop(columns=["date"], inplace=True)

    # Merge the full date table with aggregated data to ensure all (year, quarter) combinations exist
    df_aggregated = df_combined.groupby(["cluster_label", "year", "quarter"]).agg({
        "review": "count",
        "sentiment_score": "mean",
        "rating": "mean"
    }).reset_index()

    df_aggregated.rename(columns={"review": "num_sales"}, inplace=True)

    df_final = full_date_table.merge(df_aggregated, on=["cluster_label", "year", "quarter"], how="left")
    df_final.fillna(0, inplace=True)
    df_final["year"] = df_final["year"].astype(int)
    df_final["num_sales"] = df_final["num_sales"].astype(int)
    df_final["cluster_label"] = df_final["cluster_label"].astype("category")
    df_final = df_final.sort_values(by=["cluster_label", "year", "quarter"])

    print(df_final.head())

    # save the final data into csv
    df_final.to_csv("../dataset/cleaned_data/final_combined_dataset.csv", index=False)

