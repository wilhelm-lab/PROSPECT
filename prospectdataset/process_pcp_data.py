import os
import re

import numpy as np
import pandas as pd


def combine_files_into_df(
    directory_path="../data/",
    file_types=[".parquet", ".tsv", ".csv"],
    batch_size=42,
    process_test_ptm_only=False,
):
    """
    Combines all files in a directory and its subdirectories into one DataFrame based on specified file types.
    Processes files in batches to handle large datasets efficiently. Detects TMT directories and marks the data.

    Parameters:
    directory_path (str): Path to the directory containing the files.
    file_types (list): List of file extensions to include in the combination (e.g., ['.parquet', '.tsv', '.csv']).
    batch_size (int): Number of files to process in each batch.
    process_test_ptm_only (bool): If True, only processes files in the 'test_ptm' directory. If False, ignores 'test_ptm'.

    Returns:
    pd.DataFrame: A DataFrame consisting of combined data from files in the specified directory and its subdirectories.
    """
    read_funcs = {
        ".parquet": (pd.read_parquet, {"engine": "fastparquet"}),
        ".tsv": (pd.read_csv, {"sep": "\t"}),
        ".csv": (pd.read_csv, {}),
    }

    def get_all_files(directory):
        """Recursively gets all files in the directory and subdirectories."""
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if os.path.splitext(filename)[1] in file_types:
                    files.append(os.path.join(root, filename))
        return files

    def is_tmt_directory(file_path):
        """Checks if the file is in a TMT directory."""
        parts = file_path.split(os.sep)
        return "tmt" in parts

    def should_process_file(file_path):
        """Determines if a file should be processed based on the directory and process_test_ptm_only flag."""
        if process_test_ptm_only:
            return "test_ptm" in file_path.split(os.sep)
        else:
            return "test_ptm" not in file_path.split(os.sep)

    all_files = get_all_files(directory_path)
    df = pd.DataFrame()
    batch = []

    for i, file in enumerate(all_files):
        if not should_process_file(file):
            continue

        print(f"Reading {file}...")
        file_extension = os.path.splitext(file)[1]
        read_func, params = read_funcs.get(file_extension, (None, None))
        if read_func:
            try:
                df_part = read_func(file, **params)
                if file_extension == ".parquet":
                    package_name = os.path.basename(file).replace(
                        "_meta_data.parquet", ""
                    )
                    df_part["package"] = package_name

                # Detect TMT directory
                if is_tmt_directory(file):
                    df_part["is_tmt"] = True
                else:
                    df_part["is_tmt"] = False

                batch.append(df_part)
            except Exception as e:
                print(f"Error reading {file}: {e}")
        else:
            print(f"Skipping unsupported file type: {file_extension}")

        if (i + 1) % batch_size == 0 or (i + 1) == len(all_files):
            try:
                df = pd.concat([df] + batch, ignore_index=True)
                batch = []
                print(f"Processed batch of {batch_size} files.")
            except Exception as e:
                print(f"Error concatenating batch: {e}")

    if batch:
        try:
            df = pd.concat([df] + batch, ignore_index=True)
            print(f"Processed final batch of {len(batch)} files.")
        except Exception as e:
            print(f"Error concatenating final batch: {e}")

    print(f"Processed {len(all_files)} files from {directory_path}.")
    return df


def handle_tmt_data(df):
    """
    Processes the DataFrame to filter out sequences without UNIMOD:737 annotations for TMT data.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: The DataFrame after applying TMT-specific processing.
    """
    tmt_mask = df["is_tmt"]
    if tmt_mask.sum() == 0:
        print("No TMT data detected for processing.")
        return df

    print("Processing TMT data to remove sequences without UNIMOD:737 annotations...")
    len_before = len(df[tmt_mask])
    df_tmt_filtered = df[
        tmt_mask & df["modified_sequence"].str.contains(r"\[UNIMOD:737\]")
    ]
    print(
        f"Removed {len_before - len(df_tmt_filtered)} sequences without UNIMOD:737 annotations from TMT data."
    )
    df = pd.concat([df[~tmt_mask], df_tmt_filtered], ignore_index=True)
    return df


def filter_andromeda_score(df, threshold=70):
    """
    Filters out rows in the DataFrame where the andromeda_score is less than 70.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: A DataFrame with rows where andromeda_score >= 70.
    """
    print(f"Filtering rows based on andromeda_score >= {threshold}...")
    filtered_df = df[df["andromeda_score"] >= threshold]
    return filtered_df


def filter_dataframe_columns(
    df,
    columns_to_keep=[
        "modified_sequence",
        "precursor_charge",
        "precursor_intensity",
        "raw_file",
        "scan_number",
        "package",
    ],
):
    """
    Filters a DataFrame to retain only the specified columns.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    columns_to_keep (list): The names of the columns to keep in the DataFrame.

    Returns:
    pd.DataFrame: A DataFrame with only the specified columns.
    """
    print(f"Filtering DataFrame to keep columns: {columns_to_keep}...")
    df_filtered = (
        df[columns_to_keep].copy() if all(col in df for col in columns_to_keep) else df
    )
    return df_filtered


def drop_na(df, column="precursor_intensity"):
    """
    Drops all rows with NaN values in a specific column of the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame from which to drop rows.
    column (str): The column name where NaN values will be checked and rows dropped accordingly.

    Returns:
    pd.DataFrame: A DataFrame without NaN values in the specified column.
    """
    print(f"Dropping rows with NaN values in {column}...")
    df = df[df[column].notna()]
    return df


def keep_desired_charges(df, min_count=None):
    """
    Filters a DataFrame to keep only rows with charge states 1 to 6 and,
    optionally, where the count of each charge state is at least min_count.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    min_count (int, optional): Minimum count of charge states to be retained. If None, no minimum count is enforced.

    Returns:
    pd.DataFrame: A DataFrame containing only the rows with desired charge states and meeting the minimum count condition.
    """
    print("Filtering DataFrame for desired charge states...")
    charge_list = [1, 2, 3, 4, 5, 6]
    if min_count is not None:
        charge_counts = df["precursor_charge"].value_counts()
        charge_list = [
            charge
            for charge in charge_list
            if charge_counts.get(charge, 0) >= min_count
        ]

    df_filtered = df[df["precursor_charge"].isin(charge_list)]
    return df_filtered


def aggregate_unique_sequences(df):
    """
    Aggregates the DataFrame to group by 'modified_sequence' and collect lists of 'precursor_charge'
    and 'precursor_intensity' for each unique sequence.

    Parameters:
    df (pd.DataFrame): The DataFrame to be aggregated.

    Returns:
    pd.DataFrame: A DataFrame with each 'modified_sequence' as unique entries and corresponding lists
    of 'precursor_charge' and 'precursor_intensity'.
    """
    print("Aggregating DataFrame by 'modified_sequence'...")
    df = df.groupby("modified_sequence", as_index=False)[
        [
            "precursor_charge",
            "precursor_intensity",
            "raw_file",
            "scan_number",
            "package",
        ]
    ].agg(list)
    return df


def remove_rare_sequence_lengths(df, representation_threshold=100):
    """
    Removes sequences from the DataFrame that have lengths represented fewer than the specified threshold.

    Parameters:
    df (pd.DataFrame): The DataFrame containing a "modified_sequence" column where each entry is a sequence.
    representation_threshold (int): The minimum number of occurrences a sequence length must have to be retained.

    Returns:
    df (pd.DataFrame): A DataFrame containing only sequences whose lengths meet or exceed the representation threshold.
    """
    print(
        f"Removing rare sequences with lengths less than {representation_threshold} occurrences..."
    )
    before_len = len(df)
    sequence_lengths = df["modified_sequence"].str.len()
    valid_lengths = sequence_lengths.value_counts()[
        lambda x: x >= representation_threshold
    ].index
    df_filtered = df[sequence_lengths.isin(valid_lengths)].copy()
    after_len = len(df_filtered)
    print(f"Removed {before_len - after_len} of {before_len} sequences.")
    return df_filtered


def complete_vocabulary(df):
    """
    Compiles a list of all amino acids and their modifications (UNIMOD annotations) present in the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame containing 'modified_sequence' with potential UNIMOD annotations.

    Returns:
    tuple (list, int): A tuple where the first element is a list containing all unique amino acids and modifications
    found, and the second element is the total count of these unique entries, which can be used for further processing
    such as in an embedding layer.
    """
    vocabulary = []
    vocabulary += list("XACDEFGHIKLMNPQRSTVWY")
    annotations = re.findall(r"(\w\[UNIMOD:\d+])", " ".join(df["modified_sequence"]))
    for item in annotations:
        if item not in vocabulary:
            vocabulary.append(item)

    return vocabulary, len(vocabulary)


def select_most_abundant_charge_by_intensity(
    df, aggregation="max", intensity_column="precursor_intensity"
):
    """
    Selects the most abundant precursor charge based on intensity from lists of charges and intensities in a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame containing lists of 'precursor_charge' and 'precursor_intensity'.
    aggregation (str): The method used to determine abundance ('max' for maximum intensity, 'avg' for average intensity).

    Returns:
    pd.DataFrame: The DataFrame updated with new columns for the most abundant charge and the corresponding intensity
    based on the specified aggregation method.
    """
    print(f"Selecting the most abundant charge by {aggregation} intensity...")
    charge_col = f"charge_by_{aggregation}_intensity"
    intensity_col = f"{aggregation}_intensity"
    df[charge_col] = None
    df[intensity_col] = None

    for index, row in df.iterrows():
        charges = row["precursor_charge"]
        intensities = row[intensity_column]

        # Aggregate intensities for each unique charge
        charge_intensity_dict = {}
        for charge, intensity in zip(charges, intensities):
            if charge in charge_intensity_dict:
                charge_intensity_dict[charge].append(intensity)
            else:
                charge_intensity_dict[charge] = [intensity]

        # Calculating the average or maximum intensity for each charge
        if aggregation == "avg":
            avg_intensity = {
                charge: sum(charge_intensity_dict[charge])
                / len(charge_intensity_dict[charge])
                for charge in charge_intensity_dict
            }
            most_abundant_charge = max(avg_intensity, key=avg_intensity.get)
            selected_intensity = avg_intensity[most_abundant_charge]
        elif aggregation == "max":
            max_intensity = {
                charge: max(charge_intensity_dict[charge])
                for charge in charge_intensity_dict
            }
            most_abundant_charge = max(max_intensity, key=max_intensity.get)
            selected_intensity = max_intensity[most_abundant_charge]

        df.at[index, charge_col] = most_abundant_charge
        df.at[index, intensity_col] = selected_intensity

    return df


def top_k_abundant_charges_by_intensity(df, k=1, aggregation="max"):
    """
    Selects the top k most abundant precursor charges based on intensity from lists of charges and intensities
    in a DataFrame, using specified aggregation method (maximum or average).

    Parameters:
    df (pd.DataFrame): The DataFrame containing lists of 'precursor_charge' and 'precursor_intensity'.
    k (int): The number of top charges to select based on their abundance.
    aggregation (str): The method used to determine abundance ('max' for maximum intensity, 'avg' for average intensity).

    Returns:
    pd.DataFrame: The DataFrame updated with new columns listing the top k charges and their corresponding intensities
    based on the specified aggregation method.
    """
    print(f"Selecting top {k} abundant charges by {aggregation} intensity...")
    charge_col = f"top_{k}_abundant_charges_by_{aggregation}"
    intensity_col = f"top_{k}_{aggregation}_intensities"
    df[charge_col] = None
    df[intensity_col] = None

    for index, row in df.iterrows():
        charges = row["precursor_charge"]
        intensities = row["precursor_intensity"]

        # Aggregate intensities for each unique charge
        charge_intensity_dict = {}
        for charge, intensity in zip(charges, intensities):
            charge_intensity_dict.setdefault(charge, []).append(intensity)

        # Calculating the average or maximum intensity for each charge
        if aggregation == "avg":
            charge_intensity_aggregated = {
                charge: sum(intensities) / len(intensities)
                for charge, intensities in charge_intensity_dict.items()
            }
        elif aggregation == "max":
            charge_intensity_aggregated = {
                charge: max(intensities)
                for charge, intensities in charge_intensity_dict.items()
            }

        # Sort the charges by their aggregated intensity and select the top-k
        sorted_charges = sorted(
            charge_intensity_aggregated.items(), key=lambda item: item[1], reverse=True
        )[:k]
        top_k_charges, top_k_intensities = (
            zip(*sorted_charges) if sorted_charges else ([], [])
        )

        df.at[index, charge_col] = list(top_k_charges)
        df.at[index, intensity_col] = list(top_k_intensities)

    return df


def generate_charge_state_encodings(df, aggregation="max"):
    """
    Calculates the most abundant charge state for each sequence based on precursor intensity and generates
    both a charge state vector and a one-hot encoded vector for the most abundant charge.

    Parameters:
    df (pd.DataFrame): The DataFrame containing 'precursor_charge' and 'precursor_intensity' lists for each sequence.
    aggregation (str): Method to determine the most abundant charge ('max' for maximum intensity, 'avg' for average intensity).

    Returns:
    pd.DataFrame: The DataFrame updated with two new columns: 'most_abundant_charge_state' and 'observed_charge_states'.
    The first column is a one-hot encoded vector representing the most abundant charge, and the second column is a
    binary vector representing the presence of each possible charge state up to the maximum found in the data.
    """
    print("Generating charge state labels...")
    df["most_abundant_charge_state"] = None
    df["observed_charge_states"] = None

    charge_states = 6

    for index, row in df.iterrows():
        charges = row["precursor_charge"]
        intensities = row["precursor_intensity"]

        # Map intensities to their respective charge states
        charge_intensity_dict = {charge: [] for charge in charges}
        for charge, intensity in zip(charges, intensities):
            charge_intensity_dict[charge].append(intensity)

        # Aggregate intensities
        if aggregation == "avg":
            aggregated_intensity = {
                charge: sum(intensities) / len(intensities)
                for charge, intensities in charge_intensity_dict.items()
            }
        else:  # max
            aggregated_intensity = {
                charge: max(intensities)
                for charge, intensities in charge_intensity_dict.items()
            }

        most_abundant_charge = max(aggregated_intensity, key=aggregated_intensity.get)

        # Generate the one-hot encoded vector for the most abundant charge
        one_hot_vector = [
            1 if charge == most_abundant_charge else 0
            for charge in range(1, charge_states + 1)
        ]

        # Generate the charge state vector for all charges
        observed_charge_states = [
            1 if charge in charges else 0 for charge in range(1, charge_states + 1)
        ]

        df.at[index, "most_abundant_charge_state"] = one_hot_vector
        df.at[index, "observed_charge_states"] = observed_charge_states

    return df


def generate_charge_state_dist(df, intensity_column="precursor_intensity"):
    """
    Computes the normalized precursor charge state intensity distribution for each sequence in the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame containing 'precursor_charge' and 'precursor_intensity' lists for each sequence.
    Each 'precursor_charge' entry is a list of charge states, and 'precursor_intensity' is a corresponding list of
    intensities for these charges.

    Returns:
    pd.DataFrame: The DataFrame updated with a new column 'charge_state_dist', which contains a
    list of normalized intensities for each possible charge state up to the maximum found in the data.
    """
    print("Computing intensity distributions...")
    charge_states = 6

    charge_state_dist = []
    for charges, intensities in zip(df["precursor_charge"], df[intensity_column]):
        total_intensity = sum(intensities)
        charge_intensity_dict = {i: 0 for i in range(1, charge_states + 1)}
        for charge, intensity in zip(charges, intensities):
            if charge in charge_intensity_dict:
                charge_intensity_dict[charge] += intensity

        distribution = [
            charge_intensity_dict[i] / total_intensity if total_intensity > 0 else 0
            for i in range(1, charge_states + 1)
        ]
        charge_state_dist.append(distribution)

    df["charge_state_dist"] = charge_state_dist
    return df


def apply_unique_to_columns(df, column_names):
    """
    Applies np.unique to each specified column in the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    column_names (list of str): List of column names to which np.unique will be applied.

    Returns:
    pd.DataFrame: The modified DataFrame with unique values in the specified columns.
    """
    for column in column_names:
        if column in df.columns:
            df[column] = df[column].apply(
                lambda x: np.unique(x) if isinstance(x, (list, np.ndarray)) else x
            )
        else:
            print(f"Warning: Column '{column}' not found in DataFrame.")
    return df


def remove_duplicates_in_columns(df, columns):
    """
    Removes duplicates in the specified columns of the DataFrame by converting lists to sets and back to lists.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    columns (list): List of column names to remove duplicates from.

    Returns:
    pd.DataFrame: The DataFrame with duplicates removed in the specified columns.
    """
    for column in columns:
        if column in df.columns:
            df[column] = df[column].apply(
                lambda x: list(set(x)) if isinstance(x, list) else x
            )
    return df


def reduce_output_columns(df):
    """
    Reduces the DataFrame to contain only the specified columns:
    'modified_sequence', 'raw_file', 'scan_number', 'package',
    'most_abundant_charge_state', 'observed_charge_states', 'charge_state_dist'.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: The reduced DataFrame with only the specified columns.
    """
    output_colums = [
        "modified_sequence",
        "raw_file",
        "scan_number",
        "package",
        "most_abundant_charge_state",
        "observed_charge_states",
        "charge_state_dist",
    ]
    df_reduced = df[output_colums].copy()
    return df_reduced


def save_df_as_parquet(df, data_dir, file_name="preprocessed_pcp_data.parquet"):
    """
    Saves a DataFrame as a Parquet file in the specified directory with the given file name.

    Parameters:
    df (pd.DataFrame): The DataFrame to save.
    data_dir (str): Directory where the Parquet file will be saved.
    file_name (str, optional): Name of the Parquet file. Defaults to 'preprocessed_pcp_data.parquet'.
    """
    print(f"Saving DataFrame as Parquet file at {data_dir}/{file_name}...")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    file_path = os.path.join(data_dir, file_name)
    df.to_parquet(file_path, engine="pyarrow")
    print(f"File saved successfully at {file_path}")


def annotate_data(
    data_dir,
    andromeda_threshold=70,
    intensity_column="precursor_intensity",
    columns_to_keep=[
        "modified_sequence",
        "precursor_charge",
        "precursor_intensity",
        "raw_file",
        "scan_number",
        "package",
    ],
    min_count=None,
    aggregation="max",
    save_dir=".",
    file_name="processed_data.parquet",
    process_test_ptm_only=False,
):
    """
    Processes the PCP data by performing a series of steps including filtering, aggregating, and generating new features
    based on the specified parameters.

    Parameters:
    data_dir (str): Directory path where the data files are stored.
    andromeda_threshold (int): The threshold for filtering out rows based on 'andromeda_score'.
    intensity_column (str): The name of the column containing precursor intensities.
    columns_to_keep (list): The columns to retain in the DataFrame.
    min_count (int, optional): The minimum count of charge states to be retained. If None, no minimum count is enforced.
    aggregation (str): The method used to determine abundance ('max' for maximum intensity, 'avg' for average intensity).
    tmt (bool): If True, run additional steps specific to TMT data.
    save_dir (str): Directory where the processed data will be saved.
    file_name (str): Name of the processed data file.

    Returns:
    pd.DataFrame: The processed DataFrame.
    """

    print("Starting data processing...")
    df = combine_files_into_df(data_dir, process_test_ptm_only=process_test_ptm_only)

    df = handle_tmt_data(df)

    df = filter_andromeda_score(df, andromeda_threshold)

    df = filter_dataframe_columns(df, columns_to_keep)

    df = drop_na(df, column=intensity_column)

    df = keep_desired_charges(df, min_count)

    df = aggregate_unique_sequences(df)

    df = apply_unique_to_columns(df, ["raw_file", "scan_number"])

    df = remove_duplicates_in_columns(df, ["package"])

    df = remove_rare_sequence_lengths(df)

    df = select_most_abundant_charge_by_intensity(
        df, aggregation="max", intensity_column=intensity_column
    )

    df = generate_charge_state_encodings(df, aggregation)

    df = generate_charge_state_dist(df, intensity_column=intensity_column)

    df = reduce_output_columns(df)

    save_df_as_parquet(
        df,
        data_dir=save_dir,
        file_name=file_name,
    )

    print("_" * 80)
    print("Data processing completed.")
    print("_" * 80)
    print(df.info())
    return df


# Example usage
if __name__ == "__main__":
    df = annotate_data(
        data_dir="downloaded_data/test_ptm",
        andromeda_threshold=70,
        intensity_column="precursor_intensity",
        columns_to_keep=[
            "modified_sequence",
            "precursor_charge",
            "precursor_intensity",
            "raw_file",
            "scan_number",
            "package",
        ],
        min_count=None,
        aggregation="max",
        save_dir="processed_data/test_ptm",
        file_name="test_ptm_processed.parquet",
        process_test_ptm_only=True,
    )
