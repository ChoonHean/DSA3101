import warnings

# Import the library necessary for the ControlNet Model
import cv2
import torch
import numpy as np
from PIL import Image
from transformers import pipeline
from diffusers.utils import load_image, make_image_grid
from diffusers import StableDiffusionControlNetPipeline, StableDiffusionControlNetImg2ImgPipeline, StableDiffusionControlNetInpaintPipeline, ControlNetModel, UniPCMultistepScheduler, AutoPipelineForInpainting, AutoPipelineForImage2Image



# Use to suppress the warning: Future Warning that exists when using the ControlNetModel
warnings.simplefilter(action = "ignore", category=FutureWarning)

# Customized the image using its canny image
def canny_customization(image, prompt, low_threshold = 100, high_threshold = 200, verbose = False):
    """
    :param np_image: Pillow Image object
    :param prompt: The change to made to the image
    :return: A Pillow Image object with changes according to prompt
    """

    # Check if GPU is available in the current computer
    gpu = torch.cuda.is_available()

    np_image = np.array(image)
    # Transform the image into a canny image with edge detection threshold
    np_image = cv2.Canny(np_image, low_threshold, high_threshold)
    np_image = np_image[:, :, None]
    np_image = np.concatenate([np_image, np_image, np_image], axis=2)
    canny_image = Image.fromarray(np_image)

    weight_dtype = torch.float16
    ## If there's no GPU available
    if not gpu:
        weight_dtype = torch.float32

    # Input the model and pipeline from the online pretrained model
    if "controlnet_canny" not in globals():
        global controlnet_depth
        controlnet_depth = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-canny", torch_dtype=weight_dtype,
                                                           use_safetensors=True)
        global pipe_depth
        pipe_depth = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
            "stable-diffusion-v1-5/stable-diffusion-v1-5", controlnet=controlnet_depth, torch_dtype=weight_dtype,
            use_safetensors=True
        )
        pipe_depth.scheduler = UniPCMultistepScheduler.from_config(pipe_depth.scheduler.config)
    if gpu:
        pipe_depth.enable_model_cpu_offload()
    else:
        pipe_depth = pipe_depth.to("cpu")

    output = pipe_depth(
        prompt, image = canny_image
    ).images[0]

    if verbose:
        return make_image_grid([np_image, canny_image, output], rows = 1, cols = 3)

    return output



# Using Depth Map as input to the customization model

# Extract out the depth map of an image
def get_depth_map(image, depth_estimator):
    image = depth_estimator(image)["depth"]
    image = np.array(image)
    image = image[:, :, None]
    image = np.concatenate([image, image, image], axis=2)
    detected_map = torch.from_numpy(image).float() / 255.0
    depth_map = detected_map.permute(2, 0, 1)
    return depth_map

# Utizlize depth map to customize the image
def depth_customization(image, prompt, verbose = False):
    """
    :param image: Pillow Image object
    :param prompt: The change to made to the image
    :param verbose: Binary, Default to be False. Return the original image and the customized image if True, return only the original image if false
    :return: A Pillow Image object with changes according to prompt
    """
    # Check if GPU is available in the current computer
    gpu = torch.cuda.is_available()
    weight_dtype = torch.float16

    depth_estimator = pipeline("depth-estimation")

    # Obtain the depth_map of the relevant image
    depth_map = get_depth_map(image, depth_estimator).unsqueeze(0)

    # CPU natively support float32 type, using float16 will cause CPU running model having numerical instability issues and also decreased efficiency
    if not gpu:
        weight_dtype = torch.float32


    if "controlnet_depth" not in globals():
        global controlnet_depth
        controlnet_depth = ControlNetModel.from_pretrained("lllyasviel/control_v11f1p_sd15_depth", torch_dtype=weight_dtype,
            use_safetensors=True)
        global pipe_depth
        pipe_depth = StableDiffusionControlNetPipeline.from_pretrained(
            "stable-diffusion-v1-5/stable-diffusion-v1-5", controlnet=controlnet_depth, torch_dtype=weight_dtype,
            use_safetensors=True
        )
        pipe_depth.scheduler = UniPCMultistepScheduler.from_config(pipe_depth.scheduler.config)

    if gpu:
        depth_map = depth_map.half().to("cuda")
        pipe_depth.enable_model_cpu_offload()
    if not gpu:
        pipe_depth = pipe_depth.to("cpu")

    output = pipe_depth(
        prompt, image=image, control_image=depth_map,
    ).images[0]

    if verbose:
        return make_image_grid([image, output], rows=1, cols=2)

    return output



def make_inpaint_condition(image, image_mask):
    image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
    image_mask = np.array(image_mask.convert("L")).astype(np.float32) / 255.0

    assert image.shape[0:1] == image_mask.shape[0:1]
    image[image_mask > 0.5] = -1.0  # set as masked pixel
    image = np.expand_dims(image, 0).transpose(0, 3, 1, 2)
    image = torch.from_numpy(image)
    return image

# Use inpainting feature to customize the image:
def inpainting_customization(image, mask_image, prompt, image_inpainting = None, verbose = False):
    """
    :param image: Pillow Image object
    :param mask_image: Pillow Image object, contains the white colour as the area to be inpaint using black background
    :param prompt: The change to made to the image
    :param image_inpainting: Pillow Image to be inpaint in the mask_image area.
    :param verbose: Binary, Default to be False. Return the original image, mask_image and the customized image if True, return only the original image if false
    :return: A Pillow Image object with changes according to prompt
    """
    gpu = torch.cuda.is_available()
    weight_dtype = torch.float16

    if not gpu:
        weight_dtype = torch.float32
    if "controlnet_inpainting" not in globals():
        global controlnet_inpainting
        controlnet_inpainting = ControlNetModel.from_pretrained("lllyasviel/control_v11p_sd15_inpaint",
            torch_dtype=weight_dtype, use_safetensors=True)
        global pipe_inpainting
        pipe_inpainting = StableDiffusionControlNetInpaintPipeline.from_pretrained(
            "stable-diffusion-v1-5/stable-diffusion-v1-5", controlnet=controlnet_inpainting, torch_dtype=weight_dtype,
            use_safetensors=True
        )
        pipe_inpainting.scheduler = UniPCMultistepScheduler.from_config(pipe_inpainting.scheduler.config)

    control_image = make_inpaint_condition(image, mask_image)
    output = pipe_inpainting(
        prompt,
        ## Increase the inference_steps to more denoising procedure
        num_inference_steps=10,
        # Corresponds to eta in the DDIM scheduler
        eta=1.0,
        image=image,
        mask_image=mask_image,
        control_image=control_image,
    ).images[0]

    if verbose:
        return make_image_grid([image, mask_image, output], rows=1, cols=3)
    return output


# Using image as an inpainting
# def image_inpainting(image, mask_image, image_inpainting, prompt, verbose = False):
#     pipeline = AutoPipelineForInpainting.from_pretrained(
#         "stabilityai/stable-diffusion-xl-refiner-1.0", torch_dtype=torch.float32
#     )
#     image = pipeline(prompt=prompt, image=image_inpainting, mask_image=mask_image, output_type="latent").images[0]
#
#     # Second layer of pipeline
#     pipeline = AutoPipelineForImage2Image.from_pipe(pipeline)
#     image = pipeline(prompt=prompt, image=image).images[0]
#
#
#     return
#
# pipeline = AutoPipelineForInpainting.from_pretrained(
#     "stabilityai/stable-diffusion-xl-refiner-1.0", torch_dtype=torch.float32
# )
# pipeline.enable_xformers_memory_efficient_attention()
# image = pipeline(prompt = prompt, image = image_inpainting, mask_image = mask_image, output_type = "latent").images[0]


if __name__ == "__main__":
    sock = Image.open("../dataset/fashion/image_6.jpg")
    sock_mask = Image.open("../dataset/sock_mask.jpg")
    sock = sock.resize((400,400))
    sock_mask = sock_mask.resize((400,400))
    orange_sock_canny = canny_customization(sock, "Orange Sock", verbose = True)
    orange_sock_depth = depth_customization(sock, "Orange sock", verbose = True)
    orange_sock_inpaint = inpainting_customization(sock, sock_mask, "Yellow Stripes", verbose=True)

