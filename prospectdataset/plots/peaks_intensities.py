import argparse
import statistics
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--dir_path", help="Path to the directory with the annotation files"
)


def main(sys_args=sys.argv[1:]):
    args = parser.parse_args(sys_args)
    all_peaks = pd.DataFrame()
    for i, parquet_path in enumerate(
        Path(args.dir_path).glob("*/**_annotation.parquet")
    ):
        annotation = pd.read_parquet(
            parquet_path,
            columns=[
                "raw_file",
                "scan_number",
                "experimental_mass",
                "scan_number",
                "ion_type",
                "no",
                "charge",
                "neutral_loss",
            ],
            engine="pyarrow",
        )
        annotation.drop_duplicates(
            subset=["raw_file", "scan_number", "experimental_mass"],
            keep="first",
            inplace=True,
        )
        annotation.drop_duplicates(
            subset=[
                "raw_file",
                "scan_number",
                "ion_type",
                "no",
                "charge",
                "neutral_loss",
            ],
            keep="first",
            inplace=True,
        )
        all_peaks = pd.concat([all_peaks, annotation])
    median_b_nl = round(
        statistics.median(
            all_peaks.loc[
                (all_peaks["ion_type"] == "b") & (all_peaks["has_neutral_loss"])
            ]["median"]
        ),
        2,
    )
    median_b = round(
        statistics.median(
            all_peaks.loc[
                (all_peaks["ion_type"] == "b") & (~all_peaks["has_neutral_loss"])
            ]["median"]
        ),
        2,
    )

    median_y_nl = round(
        statistics.median(
            all_peaks.loc[
                (all_peaks["ion_type"] == "y") & (all_peaks["has_neutral_loss"])
            ]["median"]
        ),
        2,
    )
    median_y = round(
        statistics.median(
            all_peaks.loc[
                (all_peaks["ion_type"] == "y") & (~all_peaks["has_neutral_loss"])
            ]["median"]
        ),
        2,
    )

    b_ions = all_peaks.loc[
        (all_peaks["ion_type"] == "b") & (~all_peaks["has_neutral_loss"])
    ]["count"].sum()
    b_ions_NL = all_peaks.loc[
        (all_peaks["ion_type"] == "b") & (all_peaks["has_neutral_loss"])
    ]["count"].sum()
    y_ions = all_peaks.loc[
        (all_peaks["ion_type"] == "y") & (~all_peaks["has_neutral_loss"])
    ]["count"].sum()
    y_ions_NL = all_peaks.loc[
        (all_peaks["ion_type"] == "y") & (all_peaks["has_neutral_loss"])
    ]["count"].sum()

    fig = plt.figure()
    ax = fig.gca()
    ax = sns.violinplot(
        x="ion_type",
        y="median",
        hue="has_neutral_loss",
        data=all_peaks,
        palette="Set2",
        split=True,
    )
    ax.axhline(
        median_b,
        color="black",
        linestyle="-",
        label="n_b_ions =" + str(b_ions) + " " + str(median_b),
        linewidth=1,
        xmax=0.25,
    )
    ax.axhline(
        median_b_nl,
        color="black",
        linestyle="-",
        label="n_b_ions_nl =" + str(b_ions_NL) + " " + str(median_b_nl),
        linewidth=1,
        xmin=0.25,
        xmax=0.47,
    )
    ax.axhline(
        median_y,
        color="black",
        linestyle="-",
        label="n_y_ions =" + str(y_ions) + " " + str(median_y),
        linewidth=1,
        xmin=0.55,
        xmax=0.75,
    )
    ax.axhline(
        median_y_nl,
        color="black",
        linestyle="-",
        label="n_y_ions_nl =" + str(y_ions_NL) + " " + str(median_y_nl),
        linewidth=1,
        xmin=0.75,
    )
    ax.set_ylim(-0.02, 0.5)
    plt.legend(loc="upper left")

    plt.savefig("violin_peaks.svg", bbox_inches="tight")
