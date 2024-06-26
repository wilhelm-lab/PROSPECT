import glob
import warnings
from os.path import dirname, join, splitext

from .download import download_dataset

COLUMNS_TO_DROP = [
    "precursor_intensity",
    "precursor_mz",
    "retention_time",
    "orig_collision_energy",
    "indexed_retention_time",
    "mz",
]


# ??? ToDo: split download and process into two functions
def download_process_pool(
    annotations_data_dir=None,
    metadata_path=None,
    pool_name=None,
    save_filepath=None,
    metadata_filtering_criteria=None,
    parquet_engine="fastparquet",
):
    import pandas as pd
    from spectrum_fundamentals.constants import FRAGMENTATION_ENCODING

    # if (not annotations_data_dir and not metadata_path) or (not pool_name and not save_path):
    #    raise ValueError("You should either provide path to metadata and annotations or a pool name to download.")
    # if a pool name is provided, trigger download
    if pool_name:
        print("Downloading pool: ", pool_name)
        save_dir = dirname(save_filepath)
        downloaded_files = download_dataset("all", save_dir, pool_name)
        for f in downloaded_files:
            if f.endswith(".parquet"):
                metadata_path = f
            if f.endswith(".zip"):
                annotations_data_dir = splitext(f)[0]

    print("-" * 80)
    print("Starting processing and filtering the pool, this may take a while...")
    print("-" * 80)

    # read meta data file
    print("Reading metadata file from", metadata_path)
    metadata_df = pd.read_parquet(metadata_path, engine=parquet_engine)
    columns_to_drop = list(set(metadata_df.columns).intersection(set(COLUMNS_TO_DROP)))
    metadata_df.drop(columns_to_drop, axis=1, inplace=True)

    # read annotation files
    annotation_files = glob.glob(
        join(annotations_data_dir, "*.parquet"), recursive=True
    )

    # time consuming ???
    print("Reading and processing annotation files...")
    annotation_df = read_process_annotation_files(annotation_files)

    # rename comlumns for fundamentals # ToDo
    if "experimental_mass" in list(annotation_df.columns):
        annotation_df.rename(columns={"experimental_mass": "exp_mass"}, inplace=True)

    # time consuming ???
    print("Building annotation dataframe...")
    annotation_matrix_df = build_annotation_df(annotation_df, metadata_df)
    del annotation_df

    meta_data_merge = metadata_df.merge(
        annotation_matrix_df, on=["raw_file", "scan_number"], how="inner"
    )
    del metadata_df

    print("Applying metadata filters...")
    if metadata_filtering_criteria:
        meta_data_merge = apply_metadata_filters(
            meta_data_merge, metadata_filtering_criteria
        )

    print("Scaling and adding encoded columns...")
    # scale CE
    if "aligned_collision_energy" in list(meta_data_merge.columns):
        meta_data_merge["collision_energy_aligned_normed"] = meta_data_merge[
            "aligned_collision_energy"
        ].apply(lambda x: x / 100.0)

    # encoding fragmentation methods
    if "fragmentation" in list(meta_data_merge.columns):
        meta_data_merge["method_nbr"] = meta_data_merge["fragmentation"].map(
            FRAGMENTATION_ENCODING
        )

    # one-hot encoding  of precursor charge
    if "precursor_charge" in list(meta_data_merge.columns):
        meta_data_merge["precursor_charge_onehot"] = meta_data_merge[
            "precursor_charge"
        ].apply(precursor_int_to_onehot)

    if not save_filepath:
        # return dataframe in-memory
        return meta_data_merge

    # save to disk as parquet file and return file path
    meta_data_merge.to_parquet(save_filepath, index=False)

    return save_filepath


def apply_metadata_filters(df, metadata_filtering_criteria):
    # example
    # metadata_filtering_criteria = {
    #    "andromeda_score" :">= 0.1",
    #    "peptide_length": "<= 20",
    #    "precursor_charge": "<= 6",
    # }

    for column_name, condition in metadata_filtering_criteria.items():
        print("Filtering Column: ", column_name)
        print("Condition: ", condition)

        if column_name not in df.columns:
            warnings.warn(
                RuntimeWarning(
                    f"Skipping attribute {column_name} since it is not in metadata columns {list(df.columns)}."
                )
            )
            continue
        filter_query = column_name.strip() + condition.strip()
        df = df.query(filter_query)
    return df


def read_process_annotation_files(annotation_files, parquet_engine="fastparquet"):
    import pandas as pd

    a_dfs = []

    for file in annotation_files:
        print("Reading file: ", file)
        df = pd.read_parquet(file, engine=parquet_engine)

        # filtering
        print("Filtering annotation file...")
        mask = ((df.neutral_loss) == "") & (df.ion_type != "precursor")
        df = df[mask]

        df.drop("neutral_loss", axis=1, inplace=True)

        # drop duplicates

        # pick the annotation fragement ion with the highest fragment_score
        if "fragment_score" in list(df.columns):
            print("Sorting by fragment_score...")
            df.sort_values(by="fragment_score", ascending=False, inplace=True)

        print("Dropping duplicates...")
        df.drop_duplicates(
            subset=["raw_file", "scan_number", "experimental_mass"],
            keep="first",
            inplace=True,
        )

        # select peak with highest intensity
        print("Sorting by intensity...")
        df.sort_values(by="intensity", ascending=False, inplace=True)

        print("Dropping duplicates...")
        df.drop_duplicates(
            subset=["raw_file", "scan_number", "ion_type", "no", "charge"],
            keep="first",
            inplace=True,
        )

        ##To get from metadata --> send raw file and  scan number  --> get charge

        a_dfs.append(df)
        del df
        print("Done.")
        print("-" * 80)

    return pd.concat(a_dfs)


def precursor_int_to_onehot(charge):
    import numpy as np

    precursor_charge = np.full((6), 0)
    precursor_charge[charge - 1] = 1
    return precursor_charge


def build_annotation_df(annotation_df, metadata_df):
    import numpy as np
    import pandas as pd
    from spectrum_fundamentals.annotation.annotation import generate_annotation_matrix
    from spectrum_fundamentals.mod_string import internal_without_mods

    print("Grouping annotation by scan number and raw file...")
    annotation_scans = annotation_df.groupby(["raw_file", "scan_number"])

    print("Grouping metadata by scan number and raw file...")
    charge_seq = metadata_df.groupby(["raw_file", "scan_number"]).agg(
        {
            "precursor_charge": lambda x: np.unique(x)[0],
            "modified_sequence": lambda x: np.unique(x)[0],
        }
    )

    # Create annotation matrix
    intensities_raw = []
    masses_raw = []
    scans = []
    raw_files = []

    # new column with apply function --> get unmodified sequence

    for scan, spectrum in annotation_scans:
        # select the two columns from meta data
        raw_file, scan_number = scan

        try:
            charge_modseq = charge_seq.loc[raw_file, scan_number]
            charge, mod_sequence = meta_data[
                (meta_data["scan_number"] == scan[1])
                & (meta_data["raw_file"] == scan[0])
            ][["precursor_charge", "modified_sequence"]].values[0]

        except IndexError:
            print("IndexError: ", raw_file, scan_number)
            continue
        except KeyError:
            print("KeyError: ", raw_file, scan_number)
            continue
        charge = charge_modseq.precursor_charge
        mod_sequence = charge_modseq.modified_sequence

        # remove all modifications and return strings
        unmod_seq = internal_without_mods([mod_sequence])[0]

        # keep track of index
        scans.append(scan_number)
        raw_files.append(raw_file)

        intensities, mz = generate_annotation_matrix(spectrum, unmod_seq, charge)
        intensities_raw.append(intensities)
        masses_raw.append(mz)

    annotation_matrix_df = pd.DataFrame()
    annotation_matrix_df["scan_number"] = scans
    annotation_matrix_df["raw_file"] = raw_files
    annotation_matrix_df["intensities_raw"] = intensities_raw
    annotation_matrix_df["masses_raw"] = masses_raw
    return annotation_matrix_df
