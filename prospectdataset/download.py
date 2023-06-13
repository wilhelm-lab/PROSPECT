import os
import zipfile

from .config import AVAILABLE_DATASET_URLS, ZENODO_BASE


def get_all_urls(record_url):
    import requests
    from bs4 import BeautifulSoup

    reqs = requests.get(record_url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    urls = []
    for link in soup.find_all('a'):
        urls.append(link.get('href'))

    return urls

def filter_relevant_urls(urls_unfiltered):
    # non-null download links only
    filtered_urls = [u for u in urls_unfiltered if u is not None and u.endswith("download=1")]
    return filtered_urls

def unique_urls(urls):
    unique_urls = list(dict.fromkeys(urls))
    return unique_urls


def download_files(record, task='retention-time', save_directory = "", select_package=None):
    import urllib.request
    from urllib.parse import urlparse
    meta_data_files_only = False
    
    if task == 'retention-time':
        meta_data_files_only = True
    
    print("Downloading dataset from Zenodo record", record)
    print("Corresponding Zenodo URL is", AVAILABLE_DATASET_URLS[record])

    urls = get_all_urls(AVAILABLE_DATASET_URLS[record])
    urls = unique_urls(filter_relevant_urls(urls))
  
    if meta_data_files_only:
        urls = [u for u in urls if "meta_data" in u]
    
    if select_package:
        urls = [u for u in urls if select_package in u]
  
    print("Collected URLs: ", urls)
    downloaded_files = []
  
    for u in urls:
        filename = os.path.basename(urlparse(u).path)
        save_full_path = os.path.join(save_directory, filename)
        
        print('Downloading URL: ', u)
        urllib.request.urlretrieve(ZENODO_BASE + u, save_full_path)
        
        print('Saved file: ', save_full_path)
        downloaded_files.append(save_full_path)
    
    return downloaded_files
                        
def unzip_annotation_files(files, extract_to_dir=""):
    # ensure list contains only zip files
    zip_files = [f for f in files if ".zip" in f]

    for zf in zip_files:
        print("Unzipping file", zf)
        with zipfile.ZipFile(zf) as zfile:
            zfile.extractall(extract_to_dir)

    return zip_files

def download_dataset(record = "prospect", task="retention-time", save_directory = "", select_package=None):
    os.makedirs(save_directory, exist_ok=True)
    all_files = []
    
    if record not in AVAILABLE_DATASET_URLS.keys():
        raise ValueError("Record {} not available. Available records are {}".format(record, AVAILABLE_DATASET_URLS.keys()))
    if not isinstance(record, (str, list)):
        raise ValueError("Record must be a string or list of strings.")
    
    # if record is a string, convert to list
    if isinstance(record, str):
        record = [record]
    for rec in record:
        files = download_files(rec, task, save_directory, select_package)
        all_files.append(files)

        if task != "retention_time":
            unzip_annotation_files(files, save_directory)

    return all_files

