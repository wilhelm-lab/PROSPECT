import os
from .config import ZENODO_BASE, ZENODO_RECORD
import zipfile

def get_all_urls(record=ZENODO_RECORD):
    import requests
    from bs4 import BeautifulSoup

    reqs = requests.get(ZENODO_RECORD)
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


def download_files(task='retention-time', save_directory = "", select_pool=None):
    import urllib.request
    from urllib.parse import urlparse
    meta_data_files_only = False
    
    if task == 'retention-time':
        meta_data_files_only = True
  
    urls = get_all_urls()
    urls = unique_urls(filter_relevant_urls(urls))
  
    if meta_data_files_only:
        urls = [u for u in urls if "meta_data" in u]
    
    if select_pool:
        urls = [u for u in urls if select_pool in u]
  
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

def download_dataset(task='retention-time', save_directory = "", select_pool=None):
    os.makedirs(save_directory, exist_ok=True)
    
    files = download_files(task, save_directory, select_pool)
    
    if task != "retention_time":
        zip_files = unzip_annotation_files(files, save_directory)
    return files + zip_files
