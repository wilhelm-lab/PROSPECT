import sys
import argparse
from typing import List
import re
import seaborn as sns
from itertools import combinations
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import numpy as np
from Levenshtein import distance as levenshtein_distance



parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--dir_path",
    help="Path to the directory with the metadata files"
)

def internal_without_mods(
        sequences: List[str]
) -> List[str]:
    """
    Function to remove any mod identifiers and return the plain AA sequence.
    :param sequences: List[str] of sequences
    :return: List[str] of modified sequences.
    """
    regex = "\[.*?\]|\-"
    return [re.sub(regex, "", seq) for seq in sequences]


def main(sys_args=sys.argv[1:]):
    args = parser.parse_args(sys_args)
    pools = []
    for i, parquet_path in enumerate(Path(args.dir_path).glob("*meta_data.parquet")):
        pool_meta_data = pd.read_parquet(parquet_path)
        pool_meta_data.drop_duplicates('modified_sequence', inplace=True)
        pool_meta_data['unmod_seq'] = internal_without_mods(pool_meta_data['modified_sequence'])
        pool_meta_data.drop_duplicates('unmod_seq', inplace=True)
        pools.append(pool_meta_data)

    pools_meta_data = pd.concat(pools)
    pools_meta_data.drop_duplicates('unmod_seq', inplace=True)
    lv_dict = {}
    pep_groups = pools_meta_data.groupby('peptide_length')
    available_lengths = pools_meta_data.peptide_length.unqiue()

    for length, peptides in pep_groups:
        current_list = []
        if len(peptides.index) > 1000:
            samples = peptides['unmod_seq'].sample(n=1000, random_state=1)
        else:
            samples = peptides['unmod_seq'].values
        a = combinations(samples, 2)
        for pep_tuple in a:
            current_list.append(levenshtein_distance(pep_tuple[0], pep_tuple[1]) - 1)
        lv_dict[str(length)] = current_list

    sns.set_palette("rocket_r", n_colors=36)

    for length in available_lengths:
        fig = sns.kdeplot(np.array(lv_dict[str(length)]), bw_method=0.5, label=str(length), cbar=True, shade=True)
        plt.legend()

    plt.savefig('vs_dist.svg')
