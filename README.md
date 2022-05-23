# ProteomDS: Proteomics Dataset for Machine Learning

[ProteomDS](https://www.proteometools.org/) enables machine learning on proteomics tasks.

## Features

* Access to a large annotated Mass Spectrometry dataset.
* Utilities for reading, filtering, and splitting data.

## Installation

Install with:

```
pip install proteomds
```
    
## Usage


### Downloading a dataset

From python:
```
import proteomds
proteomds.download_dataset('retention-time', SAVE_PATH, sample=True) # Download dataset for retention time prediction.
```

Or, download and unzip from the [website](https://www.proteometools.org/).

## Contribute

Contributions are welcome. If you have additional datasets, methods, or functionality, please contribute.
See the [Contributing]() section for details.

## License

The project is licensed under the [MIT license](https://github.com/wilhelm-lab/proteomDS/blob/main/LICENSE).

## Reference

If you use ProteomDS, please cite our paper:

paper citation here
