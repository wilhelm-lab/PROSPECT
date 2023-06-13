# PROSPECT & PROSPECT PTM: A Collection of Proteomics Datasets for Machine Learning and Deep Learning

[PROSPECT](https://doi.org/10.5281/zenodo.6602020) and PROSPECT PTM (https://doi.org/10.5281/zenodo.7998644) (PROteometools SPECTrum compendium) are large annotated datasets, leveraging the raw data from ProteomeTools [1], [2].

## Datasets

Dataset | Packages | Pools | Unique Peptides | Precursors | Sepctra | Annotated Peaks | Raw Peaks
--- | --- | --- | --- |--- |--- |--- |---
PROSPECT Unmodified dataset | 12 | 983 | 838 K | 1.24 M | 61.7 M | 5.7 B | 24 B 
PROSPECT PTM TMT dataset | 11 | 1000 | 714 K | 820 K | 28.2 M | 1.8 B | 11.2 B 
PROSPECT PTM Multi-PTM dataset | 15 | 400 | 307 K | 413 K | 19.6 M | 2 B | 6 B 
PROSPECT PTM TMT-PTM dataset | 10 | 327 | 159 K | 189 K | 7.8 M | 511 M | 3 B 
PROSPECT PTM Test-PTM dataset |  25 | 56 | 10 K | 15.6 K | 3 M | 193 M | 732 M 

## Features

* Access to a large annotated Mass Spectrometry dataset.
* Utilities for downloading and splitting data.

## Installation

Install with:

```
pip install git+https://github.com/wilhelm-lab/PROSPECT
```
    
## Usage

### Downloading a Dataset

#### Using `prospectdataset`:

- Install and import the package

```
import prospectdataset as prospect 
```

- To download a specficic dataset, pass the respective record name:
```
prospect.download_dataset(record = 'prospect', save_directory = SAVE_PATH)
```

- Available record names and URLs can be displayed as follows:
```
print(prospect.AVAILABLE_DATASET_URLS)

{'prospect': 'https://zenodo.org/record/6602020',
 'prospectptm_multi_ptm': 'https://zenodo.org/record/7998644',
 'prospectptm_tmt': 'https://zenodo.org/record/8003138',
 'prospectptm_tmt_ptm': 'https://zenodo.org/record/8003152',
 'prospectptm_test_ptm': 'https://zenodo.org/record/8003156'}
```

- To download data for retention time prediction only:
```
prospect.download_dataset(task = 'retention-time', SAVE_PATH)
```

- To download data for MS/MS spectrum prediction (includes both metadata and spectra):
```
prospect.download_dataset(task = 'all', SAVE_PATH)
```

- To download only one of the 12 packages (for a faster download and a smaller dataset to experiment with), enter a substring from the package name, package names are in [Zenodo](https://doi.org/10.5281/zenodo.6602020). For example to download the package TUM_missing_first, the following would download the meta data file for the specfic package:
```
prospect.download_dataset('retention-time', SAVE_PATH, 'missing') 
```

- All downloaded files are in the parquet format. They can be easily read using panda's `pd.read_parquet()`. For faster loading, we recommend using `fastparquet` as an engine, in case it fails for some reason, `pyarrow` can also be used.

```
df = pd.read_parquet(PARQUET_FILEPATH, engine='fastparquet')
```

#### From Zenodo:

Download and unzip from the respective zenodo record, available records are:
- [PROSPECT](https://zenodo.org/record/6602020)
- [PROSPECT PTM TMT](https://zenodo.org/record/8003138)
- [PROSPECT PTM MULTI-PTM](https://zenodo.org/record/7998644)
- [PROSPECT PTM TMT-PTM](https://zenodo.org/record/8003152)
- [PROSPECT PTM TEST-PTM](https://zenodo.org/record/8003156)

### Splitting and Filtering Scripts

The three following bash scripts can be used to perform data splitting, merge files, and to filter the retention time data (iRT). Once the package is installed, they are accessbile as bash commands on the system level. Use the option ```-h``` to see the arguments of each script. 

- ```shuffle-split-data```: Shuffle and split data

- ```merge-files```: merge multiple files into one

- ```filter-irt```: filter iRT data to prepare for training.

## License

The project is licensed under the [MIT license](https://github.com/wilhelm-lab/PROSPECT/blob/main/LICENSE).

## Dataset Hosting

The dataset is hosted on Zenodo [PROSPECT DOI](https://doi.org/10.5281/zenodo.6602020) and is licensed under Creative Commons Attribution 4.0 International.

## Citation

If you use PROSPECT, please cite our paper [PROSPECT: Labeled Tandem Mass Spectrometry Dataset for Machine Learning in Proteomics](https://openreview.net/pdf?id=4nAe0PS7D-l):

```
@inproceedings{prospect,
  title={PROSPECT: Labeled Tandem Mass Spectrometry Dataset for Machine Learning in Proteomics},
  author={Shouman, Omar and Gabriel, Wassim and Giurcoiu, Victor-George and Sternlicht, Vitor and Wilhelm, Mathias},
  booktitle={Thirty-sixth Conference on Neural Information Processing Systems Datasets and Benchmarks Track}
}
```

## References

[1] Daniel P Zolg, Mathias Wilhelm, Karsten Schnatbaum, Johannes Zerweck, Tobias Knaute, Bernard Delanghe, Derek J Bailey, Siegfried Gessulat, Hans-Christian Ehrlich, Maximilian Weininger, et al. Building proteometools based on a complete synthetic human proteome. Nature methods, 14(3):259–262, 2017.

[2] Zolg, D. P., Wilhelm, M., Schmidt, T., Médard, G., Zerweck, J., Knaute, T., ... & Kuster, B. (2018). ProteomeTools: Systematic characterization of 21 post-translational protein modifications by liquid chromatography tandem mass spectrometry (LC-MS/MS) using synthetic peptides. Molecular & Cellular Proteomics, 17(9), 1850-1863.
