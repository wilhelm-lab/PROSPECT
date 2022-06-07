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


### Downloading a dataset

From python:
```
import prospect_dataset as prods 
prods.download_dataset('retention-time', SAVE_PATH) # Download dataset for retention time prediction.
```

Or, download and unzip from [Zenodo](https://doi.org/10.5281/zenodo.6602020).

## Contribute

Contributions are welcome. If you have additional datasets, methods, or functionality, please contribute.
See the [Contributing]() section for details.

## License

The project is licensed under the [MIT license](https://github.com/wilhelm-lab/PROSPECT/blob/main/LICENSE).

## Dataset Hosting

The data is hosted on Zenodo [PROSPECT DOI](https://doi.org/10.5281/zenodo.6602020).

## Citation

If you use PROSPECT, please cite our paper:

paper citation here

## References


[1] Daniel P Zolg, Mathias Wilhelm, Karsten Schnatbaum, Johannes Zerweck, Tobias Knaute, Bernard Delanghe, Derek J Bailey, Siegfried Gessulat, Hans-Christian Ehrlich, Maximilian Weininger, et al. Building proteometools based on a complete synthetic human proteome. Nature methods, 14(3):259–262, 2017.
