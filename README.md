# PROSPECT: Proteomics Dataset for Machine Learning

[PROSPECT](https://doi.org/10.5281/zenodo.6602020) enables machine learning on proteomics tasks.

## Features

* Access to a large annotated Mass Spectrometry dataset.
* Utilities for reading, filtering, and splitting data.

## Installation

Install with:

```
pip install prospect-dataset
```
    
## Usage


### Downloading a dataset

From python:
```
import prospect_dataset as prods 
prods.download_dataset('retention-time', SAVE_PATH, sample=True) # Download dataset for retention time prediction.
```

Or, download and unzip from the [Zenodo](https://doi.org/10.5281/zenodo.6602020).

## Contribute

Contributions are welcome. If you have additional datasets, methods, or functionality, please contribute.
See the [Contributing]() section for details.

## License

The project is licensed under the [MIT license](https://github.com/wilhelm-lab/PROSPECT/blob/main/LICENSE).

## Dataset Hosting

The data is hosted on Zenodo [PROSPECT DOI](https://doi.org/10.5281/zenodo.6602020).

## Reference

If you use PROSPECT, please cite our paper:

paper citation here
