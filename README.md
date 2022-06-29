# PROSPECT: Proteomics Dataset for Machine Learning

[PROSPECT](https://doi.org/10.5281/zenodo.6602020) (PROteometools SPECTrum compendium) is a large annotated dataset leveraging the raw data from ProteomeTools [1].

## Features

* Access to a large annotated Mass Spectrometry dataset.
* Utilities for downloading and splitting data.

## Installation

Install with:

```
pip install git+https://github.com/wilhelm-lab/PROSPECT
```
    
## Usage


### Downloading the Dataset

#### Using `prospectdataset`:

- Install and import the package

```
import prospectdataset as prods 
```

- To download data for retention time prediction only:
```
prods.download_dataset('retention-time', SAVE_PATH)
```

- To download data for MS/MS spectrum prediction:
```
prods.download_dataset('all', SAVE_PATH)
```

- To download only one of the 12 packages (for a faster download and a smaller dataset to experiment with), enter a substring from the package name, package names are in [Zenodo](https://doi.org/10.5281/zenodo.6602020). For example to download the package TUM_missing_first, the following would download the meta data file and the annotations zip files, then extract all annotation files.
```
prods.download_dataset('retention-time', SAVE_PATH, 'missing') 
```

#### From Zenodo:

Download and unzip from [Zenodo](https://doi.org/10.5281/zenodo.6602020).

### Splitting and Filtering Scripts

The three following bash scripts can be used to perform data splitting, merge files, and to filter the retention time data (iRT). Once the package is installed, they arae accessbile as bash commands on the system level. Use the option ```-h``` to see the arguments of each script. 

- ```shuffle-split-data```: Shuffle and split data

- ```merge-files```: merge multiple files into one

- ```filter-irt```: filter iRT data to prepare for training.

## License

The project is licensed under the [MIT license](https://github.com/wilhelm-lab/PROSPECT/blob/main/LICENSE).

## Dataset Hosting

The data is hosted on Zenodo [PROSPECT DOI](https://doi.org/10.5281/zenodo.6602020) and is licensed under Creative Commons Attribution 4.0 International.

## Citation

If you use PROSPECT, please cite our paper:

paper citation here

## References

[1] Daniel P Zolg, Mathias Wilhelm, Karsten Schnatbaum, Johannes Zerweck, Tobias Knaute, Bernard Delanghe, Derek J Bailey, Siegfried Gessulat, Hans-Christian Ehrlich, Maximilian Weininger, et al. Building proteometools based on a complete synthetic human proteome. Nature methods, 14(3):259–262, 2017.
