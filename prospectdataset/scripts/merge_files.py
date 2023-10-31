import argparse
import sys
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--dir_path",
    help="Path to the directory with the metadata and annotation files",
)


def main(sys_args=sys.argv[1:]):
    args = parser.parse_args(sys_args)

    # Merge meta_data files
    print("Merging the meta data files:")
    for i, parquet_path in enumerate(Path(args.dir_path).glob("*meta_data.parquet")):
        print(parquet_path)
        meta_data = pd.read_parquet(parquet_path, engine="pyarrow")
        meta_data = pa.Table.from_pandas(meta_data)
        if i == 0:
            # Create a parquet writer object
            pqwriter = pq.ParquetWriter(
                "meta_data_merged.parquet", meta_data.schema, compression="GZIP"
            )
        pqwriter.write_table(meta_data)

    # Merge annotation files
    print("Merging the annotation files:")
    for i, parquet_path in enumerate(Path(args.dir_path).glob("*annotation.parquet")):
        print(parquet_path)
        annotation = pd.read_parquet(parquet_path, engine="pyarrow")
        annotation = pa.Table.from_pandas(annotation)
        if i == 0:
            pqwriter = pq.ParquetWriter(
                "annotation_merged.parquet", annotation.schema, compression="GZIP"
            )
        pqwriter.write_table(annotation)
