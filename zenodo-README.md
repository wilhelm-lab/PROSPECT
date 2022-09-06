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

- `raw_file`: Raw file name.
- `scan_number`: Scan number of the MS/MS spectrum.
- `modified_sequence`: Sequence representation with the post-translational modifications.
- `precursor_charge`: The charge of the precursor ion.
- `precursor_intensity`: The intensity of the precursor ion.
- `mz [da]`: The theoritical mass over charge of the peptide sequence.
- `precursor_mz [da]`: The mass over charge of the precursor ion.
- `fragmentation`: The type of fragmentation method used (HCD, CID).
- `mass_analyzer`: The type of mass analyzer used to record the spectra (ITMS: Ion Trap, FTMS: Orbi Trap)
- `retention_time [min.]`: The uncalibrated retention time in minutes where the MS/MS spectrum has been acquired.
- `indexed_retention_time`: Indexed retention time calculated based on the Retention Time.
- `andromeda_score`: Andromeda score for the associated spectrum.
- `peptide_length`: Length of the peptide sequence without modifications.
- `orig_collision_energy`: Collison energy used to acquire the spectra.
- `aligned_collision_energy`: Calibrated collision energy.


Each annotation parquet file contains the following columns:

- `ion_type`: Type of the fragment ion (y, b).
- `no`: No of the fragment ion (1,n-1: n is the peptide length).
- `charge`: Charge of the fragment ion
- `experimental_mass [da]`: Mass of the experimental peak annotated.
- `theoretical_mass [da]`: Theoritical mass of the fragment ion.
- `intensity`: Normalized intensity of the peak.
- `neutral_loss`: Molecules lost from fragment ion (Empty string if there is no neutral loss).
- `fragment_score`: Score of the fragment ion to solve collisions.
- `peptide_sequence`: Sequence representation with the post-translational modifications.
- `scan_number`: Scan number of the MS/MS spectrum.
- `raw_file`: Raw file name.


Units:
Da: The dalton or unified atomic mass unit (symbols: da)






