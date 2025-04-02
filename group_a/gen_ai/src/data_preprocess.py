import pandas as pd
import numpy as np
import os
import requests
from PIL import Image
from io import BytesIO


images = pd.read_parquet("../dataset/fashion_meta.gzip")["images"]


def amazon_url(images):
    """
    This function ensures that all the item has all image variants while maximizing the resolution of all the photos
    :param images: A series object containing dictionary of amazon item (hi_res, large and thumb) urls (Series object)
    :return: list of "url array" for all the fashion
    """
    def get_url(image):
        """
        This will return the image that has the greatest resolution of the relevant image
        :param image: A dictionary containing URLs for the list of amazon items in the form {"hi_res":[url1, url2, ...], "large":[url1, url2, ...], "thumb":[url1, url2, ...]}
        :return: A list containing URLs of greatest resolution 1 product if available
        """
        hi_res = image["hi_res"]
        large = image["large"]
        thumb = image["thumb"]
        res = np.where(hi_res == None, large, hi_res)
        res = np.where(res == None, thumb, res)
        return res

    return list(map(get_url, images))

# This will result in a list of arrays. Where each array contain different preview of a product (URL)
image_urls = amazon_url(images)

# The following line ensures that there's no None element inside any of the urls
print(sum(map(lambda x: None in x, image_urls)))

def download_images(url_list, save_dir="../dataset/fashion"):
    """
    Download the list of url from url_list into save_dir
    :param url_list: A list that contains URL
    :param save_dir: The directory to which the resulting images will be saved to
    :return: A list of the image_path which the image that has been downloaded
    """
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

# Download fashion product image and get file paths
if __name__ == "main":
    n = 3
    first_n_images = image_urls[:n]
    url_list = [url for product in first_n_images for url in product]
    image_paths = download_images(url_list)
    print(image_paths)

