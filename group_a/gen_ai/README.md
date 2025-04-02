# GenAI model usage

## Download Dataset
1. Download the meta dataset for the Fashion Category: Run ```AmazonProduct.py```. You should see ```fashion_meta.gzip``` under ```dataset``` after the script finished running 
2. Download images from the first 3 product of Fashion dataset: Run ```DataPreprocess.py```. Check for images in ```dataset\fashion```


## There're in total 3 functions offering different customization of the variables
1. ```canny_customization``` It uses the canny image of an image to generate customized image
2. ```depth_customization``` It uses the depth map of an image to generate customized image
3. ```inpainting_customization``` It uses a mask image to tell the model the exact position of the original image to customized


## How to run
1. Navigate to ```AI Model/ControlNet.py``` 
2. Under the line ```if __name__ == "__main__":```, cuztomized the code to suits your requirement
3. You may add image under the ```dataset/fashion``` directory to test out different images
4. Change the prompts to see the different effects of it
5. Run the ControlNet.py file and observe the results

