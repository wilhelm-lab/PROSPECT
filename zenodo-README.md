## PROSPECT: Labeled Tandem Mass Spectrometry Dataset for Machine Learning in Proteomics

PROSPECT (PROteometools SPECTrum compendium) is a large annotated dataset leveraging the raw data from ProteomeTools.

The dataset consists of 12 packages and has two main parquet file formats; meta-data and annotation files. There is one meta-data file for each package, while the annotations file is split into multiple files per package to facilitate reading the data. 

Annotation files are sub-organized by pools, where a pool is a set of ~1k peptides measured in one analysis to keep the complexity low and the identification rate high. The annotation files are also zipped together into archives. 

In all files, a unique identifier to trace back any example to its original raw data file in ProteomeTools is provided. This identifier is the combination of the raw file ID and the scan number. 

The original ProteomeTools dataset is available on PRIDE: [Part1](https://www.ebi.ac.uk/pride/archive/projects/PXD004732), [Part2](https://www.ebi.ac.uk/pride/archive/projects/PXD010595), [Part3](https://www.ebi.ac.uk/pride/archive/projects/PXD021013).


## Usage

Please refer to the dataset [GitHub repository.](https://github.com/wilhelm-lab/PROSPECT)

## File Format and Data Structure

The meta-data parquet file contains the following columns:

- `raw_file`:
- `scan_number`:
- `modified_sequence`:
- `precursor_charge`:
- `precursor_intensity`: 
- `mz`:
- `precursor_mz`:
- `fragmentation`:
- `mass_analyzer`:
- `retention_time`:
- `indexed_retention_time`:
- `andromeda_score`:
- `peptide_length`:
- `orig_collision_energy`:
- `aligned_collision_energy`:


Each annotation parquet file contains the following columns:

- `ion_type`: 
- `no`: 
- `charge`: 
- `experimental_mass`: 
- `theoretical_mass`: 
- `intensity`: 
- `neutral_loss`: 
- `fragment_score`: 
- `peptide_sequence`: 
- `scan_number`: 
- `raw_file`: 










