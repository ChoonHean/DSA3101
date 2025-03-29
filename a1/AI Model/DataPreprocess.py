import pandas as pd
import numpy as np
import os
import requests
from PIL import Image
from io import BytesIO


images = pd.read_parquet("dataset/fashion_meta.gzip")["images"]

def amazon_url(images):
    """
    This function ensures that all the item has all image variants while maximizing the resolution of all the photos
    :param images: list of amazon item dictionary (Series object)
    :return: list of "url array" for all the images
    """
    def get_url(image):
        hi_res = image["hi_res"]
        large = image["large"]
        thumb = image["thumb"]
        res = np.where(hi_res == None, large, hi_res)
        res = np.where(res == None, thumb, res)
        return res

    return list(map(get_url, images))

image_urls = amazon_url(images)
# The following line ensures that there's no None element inside any of the urls
print(sum(map(lambda x: None in x, image_urls)))

# Define a function to download images
def download_images(url_list, save_dir="dataset/images"):
    os.makedirs(save_dir, exist_ok=True)
    image_paths = []

    for idx, url in enumerate(url_list):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img_path = os.path.join(save_dir, f"image_{idx}.jpg")
            img.save(img_path)
            image_paths.append(img_path)
        except Exception as e:
            print(f"Failed to download {url}: {e}")

    return image_paths

# Download images and get file paths
image_paths = download_images(image_urls)

