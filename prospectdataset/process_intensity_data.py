import glob
import warnings
from os.path import dirname, join, splitext

from .download import download_dataset

COLUMNS_TO_DROP = ["precursor_intensity", "precursor_mz", "retention_time", "orig_collision_energy",
                   "indexed_retention_time", 'mz']


def download_process_pool(annotations_data_dir=None, metadata_path=None, pool_name=None, save_filepath=None, sequence_filtering_criteria=None):

    import pandas as pd
    from spectrum_fundamentals.constants import FRAGMENTATION_ENCODING

    #if (not annotations_data_dir and not metadata_path) or (not pool_name and not save_path):
    #    raise ValueError("You should either provide path to metadata and annotations or a pool name to download.")
    # if a pool name is provided, trigger download
    if pool_name:
        save_dir = dirname(save_filepath)
        downloaded_files = download_dataset("all", save_dir, pool_name)
        for f in downloaded_files:
            if f.endswith(".parquet"):
                metadata_path = f
            if f.endswith(".zip"):
                annotations_data_dir = splitext(f)[0]

    # read meta data file
    metadata_df = pd.read_parquet(metadata_path, engine='fastparquet')
    columns_to_drop = list(set(metadata_df.columns).intersection(set(COLUMNS_TO_DROP)))
    metadata_df.drop(columns_to_drop, axis=1, inplace=True)

    # filter meta data
    if sequence_filtering_criteria:
        metadata_df = filter_metadata(metadata_df, sequence_filtering_criteria)

    # read annotation files
    annotation_files = glob.glob(join(annotations_data_dir, "*.parquet"), recursive=True)
    annotation_df = read_process_annotation_files(annotation_files)

    # rename comlumns for fundamentals # ToDo
    if "experimental_mass" in list(annotation_df.columns):
        annotation_df.rename(columns={'experimental_mass':'exp_mass'}, inplace=True)

    annotation_matrix_df = build_annotation_df(annotation_df, metadata_df)
    del annotation_df

    meta_data_merge = metadata_df.merge(annotation_matrix_df, on=['raw_file','scan_number'], how='inner')
    del metadata_df

    # scale CE
    if "aligned_collision_energy" in list(meta_data_merge.columns):
        meta_data_merge['collision_energy_aligned_normed'] = meta_data_merge['aligned_collision_energy'].apply(lambda x: x/100.0)

    # encoding fragmentation methods
    if "fragmentation" in list(meta_data_merge.columns):
        meta_data_merge['method_nbr'] = meta_data_merge['fragmentation'].map(FRAGMENTATION_ENCODING)

    # one-hot encoding  of precursor charge
    if "precursor_charge" in list(meta_data_merge.columns):
        meta_data_merge['precursor_charge_onehot'] = meta_data_merge['precursor_charge'].apply(precursor_int_to_onehot)

    if not save_filepath:
        # return dataframe in-memory
        return meta_data_merge
    
    # save to disk as parquet file and return file path
    meta_data_merge.to_parquet(save_filepath, index=False)
    
    return save_filepath

def filter_metadata(df, sequence_filtering_criteria):

    # example
    # criteria should be MODE_COLUMNNAME
    # mode = {min, max}
    # columnname = {metadata dataframe columns}

    # sequence_filtering_criteria = {
    #    "min_andromeda_score": 0.1,
    #    "max_peptide_length": 20,
    #    "max_precursor_charge": 6,
    # }

    for criteria, threshold in sequence_filtering_criteria.items():
        mode, attribute = criteria.split("_", maxsplit=1)
        print("mode: ", mode)
        print("attribute: ", attribute)
        if attribute not in df.columns:
            warnings.warn(RuntimeWarning("Skipping attribute {attribute} since it is not in metadata columns {list(df.columns)}."))
            continue
        filter_query = f" {attribute} "
        filter_query += " >= " if mode == "min" else " <= "
        filter_query += str(threshold)
        df = df.query(filter_query)
    return df

def read_process_annotation_files(annotation_files):
    import pandas as pd
    a_dfs = []

    for file in annotation_files:
        df = pd.read_parquet(file, engine='fastparquet')
        
        # filtering
        mask = ((df.neutral_loss) == "") & (df.ion_type != 'precursor')
        df = df[mask]

        if "neutral_loss" in list(df.columns):
            df.drop("neutral_loss", axis=1, inplace=True)
        
        # drop duplicates
        
        # pick the annotation fragement ion with the highest fragment_score 
        if "fragment_score" in list(df.columns):
            df.sort_values(by='fragment_score', ascending=False, inplace=True)
        df.drop_duplicates(subset=['raw_file','scan_number', 'experimental_mass'], keep="first", inplace=True)
        
        # select peak with highest intensity
        df.sort_values(by='intensity', ascending=False, inplace=True)
        df.drop_duplicates(subset=['raw_file', 'scan_number', 'ion_type', 'no', 'charge'], keep="first", inplace=True)

        a_dfs.append(df)
        del df
    
    return pd.concat(a_dfs)

def precursor_int_to_onehot(charge):
    import numpy as np
    
    precursor_charge = np.full((6), 0)
    precursor_charge[charge-1] = 1
    return precursor_charge

def build_annotation_df(annotation_df, metadata_df):
    import numpy as np
    import pandas as pd
    from spectrum_fundamentals.annotation.annotation import generate_annotation_matrix
    from spectrum_fundamentals.mod_string import internal_without_mods

    annotation_scans = annotation_df.groupby(['raw_file','scan_number'])
    
    charge_seq = metadata_df.groupby(['raw_file','scan_number']).agg({
    "precursor_charge" : lambda x: np.unique(x)[0],
    "modified_sequence": lambda x: np.unique(x)[0]
    })
    
    #Create annotation matrix
    intensities_raw = []
    masses_raw = []
    scans = []
    raw_files = []
    for scan, spectrum in annotation_scans:
        # select the two columns from meta data
        raw_file, scan_number = scan
        charge_modseq = charge_seq.loc[raw_file, scan_number]
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
    annotation_matrix_df['scan_number'] = scans
    annotation_matrix_df['raw_file'] = raw_files
    annotation_matrix_df['intensities_raw'] = intensities_raw
    annotation_matrix_df['masses_raw'] = masses_raw
    return annotation_matrix_df

