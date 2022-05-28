# PROSPECT: Proteomics Dataset for Machine Learning

[PROSPECT](https://www.proteometools.org/) enables machine learning on proteomics tasks.

## Features

* Access to a large annotated Mass Spectrometry dataset.
* Utilities for reading, filtering, and splitting data.

## Installation

Install with:

```
pip install prospect
```
    
## Usage


### Downloading a dataset

From python:
```
import prospect
prospect.download_dataset('retention-time', SAVE_PATH, sample=True) # Download dataset for retention time prediction.
```

Or, download and unzip from the [website](https://www.proteometools.org/).

## Contribute

Contributions are welcome. If you have additional datasets, methods, or functionality, please contribute.
See the [Contributing]() section for details.

## License

The project is licensed under the [MIT license](https://github.com/wilhelm-lab/PROSPECT/blob/main/LICENSE).

## Reference

If you use PROSPECT, please cite our paper:

paper citation here
