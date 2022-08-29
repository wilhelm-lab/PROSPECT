import sys
import argparse
import itertools
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--dir_path",
    help="Path to the directory with the metadata files"
)


def main(sys_args=sys.argv[1:]):
    args = parser.parse_args(sys_args)
    pools = []
    for i, parquet_path in enumerate(Path(args.dir_path).glob("*meta_data.parquet")):
        pool_meta_data = pd.read_parquet(parquet_path)
        pools.append(pool_meta_data)

    meta_data = pd.concat(pools)
    palette = itertools.cycle(sns.color_palette("YlOrRd_r", n_colors=len(meta_data["peptide length"].unique())))
    
    plt.rcParams['figure.figsize'] = [18, 10]
    lengths = sorted(meta_data["peptide length"].unique())
    plot = plt.scatter(lengths, lengths, c=lengths, cmap='YlOrRd_r')
    plt.clf()
    cbar = plt.colorbar(plot)
    cbar.ax.set_ylabel('peptide length', rotation=270)
    cbar.ax.yaxis.set_label_coords(2.2, .5)
    
    for i in range(meta_data["peptide length"].min(), meta_data["peptide length"].max()+1):
        if len(meta_data[meta_data["peptide length"] == i]["retention_time"]) != 1 and \
                len(meta_data[meta_data["peptide length"] == i]["retention_time"]) != 2:
            ax = sns.kdeplot(data=meta_data[meta_data["peptide length"] == i]["retention_time"], color=next(palette))
    
    ax.set(xlabel='retention time', ylabel='density')
        
    plt.savefig('distrib.svg', dpi=300, bbox_inches='tight')
