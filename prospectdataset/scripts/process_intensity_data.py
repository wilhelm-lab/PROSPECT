import glob
from os.path import join, splitext

import numpy as np
import pandas as pd
from spectrum_fundamentals.annotation.annotation import generate_annotation_matrix
from spectrum_fundamentals.mod_string import internal_without_mods

from ..download import download_dataset

POOL_NAME = "third"
DATA_DIR = "./data"
SAVE_PATH = DATA_DIR

downloaded_files = download_dataset("all", DATA_DIR, POOL_NAME)
meta_data_file_path = None
annotations_files_folder_path = None

for f in downloaded_files:
    if f.endswith(".parquet"):
        meta_data_file_path = f
    if f.endswith(".zip"):
        annotations_files_folder_path = splitext(f)[0]


metadata_df = pd.read_parquet(meta_data_file_path, engine='fastparquet')
columns_to_drop = ["precursor_intensity", "precursor_mz", "retention_time", "orig_collision_energy",
                   "indexed_retention_time", 'mz']
metadata_df.drop(columns_to_drop, axis=1, inplace=True)



annotation_files = glob.glob(join(annotations_files_folder_path, "*.parquet"))


#

a_dfs = []
for file in annotation_files:
    df = pd.read_parquet(file, engine='fastparquet')
    
    # filtering
    mask = ((df.neutral_loss) == "") & (df.ion_type != 'precursor')
    df = df[mask]
    df.drop("neutral_loss", axis=1, inplace=True)
    
    # drop duplicates
    
    # pick the annotation fragement ion with the highest fragment_score 
    df.sort_values(by='fragment_score', ascending=False, inplace=True)
    df.drop_duplicates(subset=['raw_file','scan_number', 'experimental_mass'], keep="first", inplace=True)
    
    # select peak with highest intensity
    df.sort_values(by='intensity', ascending=False, inplace=True)
    df.drop_duplicates(subset=['raw_file', 'scan_number', 'ion_type', 'no', 'charge'], keep="first", inplace=True)

    
    a_dfs.append(df)
    del df

annotation_df = pd.concat(a_dfs)
del a_dfs

# for fundamentals
annotation_df.rename(columns={'experimental_mass':'exp_mass'}, inplace=True)

annotation_matrix_df = build_annotation_matrix_df(annotation_df, metadata_df)

meta_data_merge = metadata_df.merge(annotation_matrix_df, on=['raw_file','scan_number'], how='inner')

# scale CE
meta_data_merge['collision_energy_aligned_normed'] = meta_data_merge['aligned_collision_energy'].apply(lambda x: x/100.0)

# encoding fragmentation methods
meta_data_merge['method_nbr'] = meta_data_merge['fragmentation'].apply(lambda x: FRAGMENTATION_ENCODING[x])

# one-hot encoding  of precursor charge
meta_data_merge['precursor_charge_onehot'] = meta_data_merge['precursor_charge'].apply(precursor_int_to_onehot)

# save to disk as parquet file
meta_data_merge.to_parquet(join(SAVE_PATH, f"processed_data_{POOL_NAME}.parquet"), index=False)


def precursor_int_to_onehot(charge):
    precursor_charge = np.full((6), 0)
    precursor_charge[charge-1] = 1
    return precursor_charge

def build_annotation_matrix_df(annotation_df, metadata_df):
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
