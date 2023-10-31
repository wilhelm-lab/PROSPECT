import argparse
import collections
import random
import sys
import time

import numpy
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--seed", default=42, help="A seed for RNG")
parser.add_argument(
    "-t",
    "--trainingsplit",
    default=0.9,
    help="The fraction to use for training data (e.g. 0.9 would mean that the train-test split is 90-10 percent).",
)

parser.add_argument(
    "-f",
    "--splitfile",
    help="Should the file split in two files: One with train one with validation/holdout data.",
    action="store_true",
)

parser.add_argument("-m", "--metadata", help="Path to the metadata file")
parser.add_argument("-a", "--annotation", help="Path to the annotation file")
parser.add_argument(
    "-thr", "--threshold", help="Threshold for Andromeda score", default=70
)


def argshuffle_splits(idx, traininsplit):
    train_idx = list(numpy.random.permutation(idx[:traininsplit]))
    test_idx = list(numpy.random.permutation(idx[traininsplit:]))
    return train_idx, test_idx


def peptide_argsort(sequence_integer, seed=42):
    random.seed(seed)
    peptide_groups = collections.defaultdict(list)
    for index, row in enumerate(sequence_integer):
        peptide_groups[tuple(row)].append(index)

    # shuffle within peptides
    for indeces in peptide_groups.values():
        random.shuffle(indeces)

    # shuffle peptides
    peptides = list(peptide_groups.keys())
    random.shuffle(peptides)

    # join indeces
    indeces = []
    for peptide in peptides:
        indeces.extend(peptide_groups[peptide])
    return indeces


def main(sys_args=sys.argv[1:]):
    start = time.time()

    args = parser.parse_args(sys_args)

    # Read the meta data and annotation files
    meta_data = pd.read_parquet(args.metadata, engine="fastparquet")
    annotation_df = pd.read_parquet(args.annotation, engine="fastparquet")

    # Filter meta data based on Andromeda score threshold
    initial_size = len(meta_data)
    print("initial number of peptides", initial_size)
    meta_data = meta_data[meta_data["SCORE"] > args.threshold]
    print("removing", initial_size - len(meta_data), "peptides")

    sequence_integer = meta_data["MODIFIED_SEQUENCE"][...]
    n = sequence_integer.shape[0]
    n_split = int(n * float(args.trainingsplit))
    print("training split at: ", n_split, "/", n)
    print("shuffling peptides")
    idx = peptide_argsort(sequence_integer, seed=args.seed)
    del sequence_integer
    print("shuffling train and test")
    train_idx, test_idx = argshuffle_splits(idx, n_split)

    if args.splitfile:
        meta_data_train = meta_data.iloc[train_idx]
        meta_data_test = meta_data.iloc[test_idx]

        annotation_df_train = annotation_df[
            annotation_df["scan_number"].isin(meta_data_train["SCAN_NUMBER"])
        ]
        annotation_df_test = annotation_df[
            annotation_df["scan_number"].isin(meta_data_test["SCAN_NUMBER"])
        ]

        # Save training + testing annotation and metadata files as parquet files
        meta_data_train.to_parquet("meta_data_train.parquet", compression="gzip")
        meta_data_test.to_parquet("meta_data_test.parquet", compression="gzip")

        annotation_df_train.to_parquet("annotation_train.parquet", compression="gzip")
        annotation_df_test.to_parquet("annotation_test.parquet", compression="gzip")

    else:
        dx = train_idx + test_idx
        meta_data_combined = meta_data.iloc[dx]
        annotation_combined = annotation_df[
            annotation_df["scan_number"].isin(meta_data["SCAN_NUMBER"])
        ]

        meta_data_combined.to_parquet("meta_data_combined.parquet", compression="gzip")
        annotation_combined.to_parquet(
            "annotation_combined.parquet", compression="gzip"
        )

    end = time.time()
    print("Time:", end - start)
