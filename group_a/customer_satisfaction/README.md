# Analyzing and finding ways to increase user satisfaction.

In this section, we would focus on how the potential relationships between user reviews and the items themselves. The
scope of this would be limited to [Amazon fashion](https://amazon-reviews-2023.github.io/).

---

## How to run

Download postgresql and create a database [here](https://www.postgresql.org/)

```
python customer_anlysis.py
```

Set your configurations in ```config/cofig.yaml``` based on the dataset(s) you would like to download.

Do note that due to the large dataset sizes, ```customer_analysis.py``` script might take a long time to run.

Our insights are present in [report.md](./report.md).

---

## Raw data schema

For each item, there would be a corresponding review, as well as a corresponding metadata attached to it. The structure
of the data obtained would be as follows. [structure](https://amazon-reviews-2023.github.io/)