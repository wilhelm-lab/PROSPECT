import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--dir_path", help="Path to the directory with the metadata files"
)


def main(sys_args=sys.argv[1:]):
    args = parser.parse_args(sys_args)
    pools = []
    for i, parquet_path in enumerate(Path(args.dir_path).glob("*meta_data.parquet")):
        pool_meta_data = pd.read_parquet(parquet_path)
        pools.append(pool_meta_data)

    meta_data = pd.concat(pools)
    df_pie = (
        meta_data.groupby(["precursor_charge", "peptide_length"])
        .size()
        .unstack(fill_value=0)
    )
    colors = sns.color_palette()[0:6]

    f, axes = plt.subplots(
        1, len(meta_data["peptide_length"].unique()), figsize=(20, 5)
    )
    for ax, col in zip(axes, df_pie.columns):
        patches, text = ax.pie(df_pie[col].values, colors=colors)
        ax.set(title=col)

    plt.legend(
        labels=["1", "2", "3", "4", "5", "6"],
        loc="center",
        ncol=6,
        bbox_to_anchor=(0.5, 2),
        fancybox=True,
        shadow=True,
    )
    plt.axis("off")

    plt.savefig("peptides_charges_dist.svg", dpi=300, bbox_inches="tight")
