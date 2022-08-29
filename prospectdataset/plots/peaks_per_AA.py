import sys
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import seaborn as sns
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    "-a",
    "--dir_path_annotation",
    help="Path to the directory with the annotation files"
)
parser.add_argument(
    "-m",
    "--dir_path_metadata",
    help="Path to the directory with the meta data files"
)


def main(sys_args=sys.argv[1:]):
    args = parser.parse_args(sys_args)
    meta_data_list = []
    for j, parquet_path_md in enumerate(Path(args.dir_path_metadata).glob("*meta_data.parquet")):

        file_name = str(parquet_path_md).split("/")[-1].replace("_meta_data.parquet", "")
        path_ann = args.dir_path_annotation + '/' + file_name
        meta_data = pd.read_parquet(parquet_path_md, columns=['raw_file', 'scan_number', 'peptide_length'],
                                    engine="pyarrow")
        count = 0

        for f, parquet_path in enumerate(Path(path_ann).glob("*annotation.parquet")):

            annotation = pd.read_parquet(parquet_path, columns=['raw_file', 'scan_number', 'experimental_mass',
                                                                'ion_type', 'no', 'charge', 'neutral_loss'],
                                         engine="pyarrow")
            annotation.drop_duplicates(subset=['raw_file', 'scan_number', 'experimental_mass'], keep="first",
                                       inplace=True)
            annotation.drop_duplicates(subset=['raw_file', 'scan_number', 'ion_type', 'no', 'charge', 'neutral_loss'],
                                       keep="first", inplace=True)
            meta_data = meta_data.merge(annotation.groupby(['raw_file', 'scan_number']).size().to_frame().reset_index(),
                                        left_on=['raw_file', 'scan_number'], right_on=['raw_file', 'scan_number'],
                                        how="left")
            count += 1

        meta_data["peaks"] = meta_data.iloc[:, -count:].sum(axis=1)
        meta_data_list.append(meta_data[['raw_file', 'scan_number', "peptide_length", "peaks"]])

    concat_meta_data = pd.concat(meta_data_list, ignore_index=True)
    concat_meta_data.dropna(inplace=True)
    concat_meta_data.to_csv('meta_data_concat.csv')
    plt.rcParams['figure.figsize'] = [30, 15]
    concat_meta_data["peaks/length"] = concat_meta_data["peaks"] / concat_meta_data["peptide_length"]
    ax = sns.boxplot(y="peaks/length", x="peptide_length", data=concat_meta_data, color="seagreen", showfliers=False)
    ax.set_xlabel('peptide length')
    plt.savefig('peaks_per_AA_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close()
