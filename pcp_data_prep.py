import os
import re

import pandas as pd


def combine_files_into_df(
    directory_path="../data/", file_types=[".parquet", ".tsv", ".csv"]
):
    """
    Combines all files in a directory into one DataFrame.
    @param directory_path: str, path to the directory containing the files
    @param file_types: list, list of file types to be imported
    @return: df: DataFrame
    """
    # Map file extensions to their respective pandas read functions and parameters
    read_funcs = {
        ".parquet": (pd.read_parquet, {"engine": "fastparquet"}),
        ".tsv": (pd.read_csv, {"sep": "\t"}),
        ".csv": (pd.read_csv, {}),
    }

    message_prefix = "Step 1/? complete."

    dfs = []
    # Iterate through all files in the specified directory
    for file in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file)
        file_extension = os.path.splitext(file)[1]

        # Check if the file extension is in the list of types to read
        if file_extension in file_types:
            read_func, params = read_funcs.get(file_extension, (None, None))
            if read_func:
                df = read_func(file_path, **params)
                dfs.append(df)
            else:
                print(f"Skipping unsupported file type: {file_extension}")

    # Combine all DataFrames in the list into a single DataFrame
    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        print(f"{message_prefix} Combined {len(dfs)} files into one DataFrame.")
    else:
        df = pd.DataFrame()
        print("No files combined.")

    return df


def filter_andromeda_score(df, threshold=70):
    """
    Filters out rows in the DataFrame where the andromeda_score is less than 70.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: A DataFrame with rows where andromeda_score >= 70.
    """
    filtered_df = df[df["andromeda_score"] >= threshold]
    return filtered_df


def filter_dataframe_columns(
    df, columns_to_keep=["modified_sequence", "precursor_charge", "precursor_intensity"]
):
    """
    Filters a DataFrame to retain only the specified columns.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    columns_to_keep (list): The names of the columns to keep in the DataFrame.

    Returns:
    pd.Data
    """
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
    df = df[df[column].notna()]
    return df


def keep_desired_charges(df, charge_list=[1, 2, 3, 4, 5, 6], min_count=None):
    """
    Filters a DataFrame to keep only rows with charge states specified in the charge_list and,
    optionally, where the count of each charge state is at least min_count.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    charge_list (list): List of charge states to retain in the DataFrame.
    min_count (int, optional): Minimum count of charge states to be retained. If None, no minimum count is enforced.

    Returns:
    pd.DataFrame: A DataFrame containing only the rows with desired charge states and meeting the minimum count condition.
    """
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
    df = df.groupby("modified_sequence", as_index=False)[
        ["precursor_charge", "precursor_intensity"]
    ].agg(list)
    return df


def remove_rare_sequence_lengths(df, representation_threshold=100):
    """
    Removes sequences from the DataFrame that have lengths represented fewer than the specified threshold.

    Parameters:
    df (pd.DataFrame): The DataFrame containing a "modified_sequence" column where each entry is a sequence.
    representation_threshold (int): The minimum number of occurrences a sequence length must have to be retained.

    Returns:
    tuple (pd.DataFrame, int): A tuple where the first element is a DataFrame containing only sequences whose lengths
    meet or exceed the representation threshold, and the second element is the length of the longest sequence retained.
    """
    before_len = len(df)
    # Calculate sequence lengths directly within the groupby and count operation
    sequence_lengths = df["modified_sequence"].str.len()
    # Identify sequence lengths that meet the representation threshold
    valid_lengths = sequence_lengths.value_counts()[
        lambda x: x >= representation_threshold
    ].index
    # Filter the DataFrame based on valid sequence lengths
    df_filtered = df[sequence_lengths.isin(valid_lengths)].copy()
    padding_length = sequence_lengths.max()
    after_len = len(df_filtered)

    print(
        f"Removed {before_len - after_len} of {before_len} sequences because their sequence length "
        f"is represented less than {representation_threshold} times."
    )
    return df_filtered, padding_length


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


def select_most_abundant_charge_by_intensity(df, aggregation="max"):
    """
    Selects the most abundant precursor charge based on intensity from lists of charges and intensities in a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame containing lists of 'precursor_charge' and 'precursor_intensity'.
    aggregation (str): The method used to determine abundance ('max' for maximum intensity, 'avg' for average intensity).

    Returns:
    pd.DataFrame: The DataFrame updated with new columns for the most abundant charge and the corresponding intensity
    based on the specified aggregation method.
    """
    charge_col = f"charge_by_{aggregation}_intensity"
    intensity_col = f"{aggregation}_intensity"
    df[charge_col] = None
    df[intensity_col] = None

    for index, row in df.iterrows():
        charges = row["precursor_charge"]
        intensities = row["precursor_intensity"]

        # Aggregate intensities for each unique charge
        charge_intensity_dict = {}
        for charge, intensity in zip(charges, intensities):
            if charge in charge_intensity_dict:
                charge_intensity_dict[charge].append(intensity)
            else:
                charge_intensity_dict[charge] = [intensity]

        # Calculate the average or maximum intensity for each charge
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

        # Calculate the average or maximum intensity for each charge
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
    pd.DataFrame: The DataFrame updated with two new columns: 'one_hot_most_abundant_charge' and 'charge_state_vector'.
    The first column is a one-hot encoded vector representing the most abundant charge, and the second column is a
    binary vector representing the presence of each possible charge state up to the maximum found in the data.
    """
    df["one_hot_most_abundant_charge"] = None
    df["charge_state_vector"] = None

    max_charge_state = max(max(charges) for charges in df["precursor_charge"])

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
            for charge in range(1, max_charge_state + 1)
        ]

        # Generate the charge state vector for all charges
        charge_state_vector = [
            1 if charge in charges else 0 for charge in range(1, max_charge_state + 1)
        ]

        df.at[index, "one_hot_most_abundant_charge"] = one_hot_vector
        df.at[index, "charge_state_vector"] = charge_state_vector

    return df


def compute_normalized_intensity_distribution(df):
    """
    Computes the normalized intensity distribution for each sequence in the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame containing 'precursor_charge' and 'precursor_intensity' lists for each sequence.
    Each 'precursor_charge' entry is a list of charge states, and 'precursor_intensity' is a corresponding list of
    intensities for these charges.

    Returns:
    pd.DataFrame: The DataFrame updated with a new column 'normalized_intensity_distribution', which contains a
    list of normalized intensities for each possible charge state up to the maximum found in the data.
    """
    max_charge_state = max(max(charges) for charges in df["precursor_charge"])

    normalized_intensity_distribution = []
    for charges, intensities in zip(df["precursor_charge"], df["precursor_intensity"]):
        total_intensity = sum(intensities)
        charge_intensity_dict = {charge: 0 for charge in range(1, max_charge_state + 1)}
        for charge, intensity in zip(charges, intensities):
            charge_intensity_dict[charge] += intensity

        distribution = [
            charge_intensity_dict[i] / total_intensity
            for i in range(1, max_charge_state + 1)
        ]
        normalized_intensity_distribution.append(distribution)

    df["normalized_intensity_distribution"] = normalized_intensity_distribution
    return df
