import argparse
import pandas as pd
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file_path",
        help="Path to the file"
    )
    parser.add_argument(
        "-thr",
        "--threshold",
        help="Threshold for filtering the var irt values",
        default=2000
    )
    args = parser.parse_args()

    meta_data = pd.read_parquet(args.file_path, engine="fastparquet")


    # Group by raw file and seq -> select only seq with max andromeda score
    max_score_df = meta_data.sort_values(['andromeda_score'], ascending=False)\
        .groupby(['modified_sequence', 'raw_file']).first().reset_index()

    # Group by seq -> calculate mean, var for irt
    md = max_score_df[["modified_sequence", "indexed_retention_time"]].groupby("modified_sequence")\
        .agg([np.mean, np.var, np.size, np.std]).reset_index()
    md.columns = md.columns.droplevel(0)
    md.columns = ['modified_sequence', 'mean', 'var', 'size', "std"]

    # Filter metadata based on the var
    df_out = max_score_df.merge(md[md["var"] < 2], on='modified_sequence', suffixes=('_l', '_r'))
    print(df_out)
    print(df_out["andromeda_score"])

    meta_data.to_parquet('meta_data_median_irt.parquet', compression='gzip')
