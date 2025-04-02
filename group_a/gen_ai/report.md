# AI Image Synthesis Techniques

## 1. VAEs Architecture

![image](https://github.com/user-attachments/assets/fb0779c9-d89d-4d2c-b26b-f91c785c8663)
*<p style="text-align:centre;">Figure 1 Model Architecture of VAEs</p>*

Image Source: https://miro.medium.com/v2/resize:fit:828/format:webp/0*g9DdElJzN1iCwUOt

As an extension of the autoencoders, VAEs are capable of generating **variants of the original images** instead of just
reconstructing the images.

**Model Architecture**

* It does so through mapping the distribution of the input (x) instead of representing it using a single fixed latent
  vector
* Latent vectors (z) which are fed to the decoder are sampled from the distribution, indicating the source of
  variation (In autoencoder, the same data will generate the same latent vector using the same model)
* Usage of distribution allows the features of the data to be learnt while allowing variations. The learning of
  distribution is manifested in the parameters φ
* In the decoder stage, it tries to reconstruct the encoder distribution (of parameters φ) in the decoder distribution (
  of parameters θ) using the latent vector z.
* The output x' is sampled from the decoder distribution

**Model Loss Function**

![image](https://github.com/user-attachments/assets/4e29823b-ae9a-4704-8c23-85692b2839d3)
*<p style="text-align:centre;">Figure 2 VAE Loss function</p>*

* The first term (_Reconstruction Loss_) is the negative log-likelihood for the decoder. It sums up the expected
  probabilities of obtaining the input vector given the latent vector z
* The second terms (_Regularization Term_) is Kullback-Leibler (KL) Divergence. This term would encourage the model to
  generate the latent vector z that follows the prior distribution p(z). In this case p(z) ~ N(0,1). The regularization
  term helps to ensure the model do not simply replicate the original picture while ensuring the model correctly
  classifies the data according to its label in the latent space(Original picture).

References:

1. https://medium.com/@judyyes10/generate-images-using-variational-autoencoder-vae-4d429d9bdb5
2. https://mbernste.github.io/posts/vae/

## 2. Stable Diffusion Model

Stable diffusion model is a generative artificial intelligence model that produces unique high-quality images from text
and image prompts. The model is based on diffusion technology and uses latent space. Diffusion models transform random
noise into structured images by reversing the diffusion process. This allows for the model to be run on desktops or
laptops equipped with GPUs as it has less processing requirements.

**Process of the Stable Diffusion Model**

<img width="457" alt="Screenshot 2025-03-21 at 11 36 06 PM" src="https://github.com/user-attachments/assets/1bcdb4aa-7612-43b8-b548-d7f494fa9da2" />

*<p style="text-align:centre;">Figure 3 Stable Diffusion Inference Process</p>*

**Latent Seed :** The process begins with Gaussian noise, which is the initial "seed" used to be transformed into an
image and this seed is a random noise pattern which is then used to generate meaningful images

**User Prompt :** A text prompt is then processed by a CLIP text encoder, which is then converted into a vector
representation

**Text-Conditioned Latent U-Net :** This model takes both the noisy latent and the text embeddings, iteratively refining
the image by predicting and removing noise in the latent space

**Scheduler :** The scheduler controls the noise addition and removal process, determining how many steps the diffusion
process should run through

**Variational Autoencoder (VAE) Decoder :** After processing the latent space, the VAE decoder converts the conditioned
latent space into a visible, high-resolution image

The above stable diffusion model can also be applied to image to image generation by passing a text prompt and an
initial image to condition the generation of new images. The *StableDiffusionImg2ImgPipleine* can be used for this. The
*StableDiffusionImg2ImgPipeline* will process the initial image in the latent space and adjust it based on the features
described in the prompt. It will modify parts of the image while trying to maintain the structural integrity and main
features of the original image. This makes stable diffusion suitable for product customization as businesses can use
this to modify product images according to each customers' preferences.

**Advantages :**

* Able to generate images that are high in resolution and highly detailed even from low quality inputs
* Able to capture the detailed textures, lighting and other realistic aspects of the input image
* Saves time as companies do not have to do the customisation of the images themselves
* Can be used to enhance specific features in an image, such as colours, textures and more making it very useful for
  customer customisation of products

**Limitations :**

* Computationally intensive and time-consuming, especially when the input images are large
* Not suitable for some image editing tasks like removing an unwanted element from the image, resulting in a
  customisation limitation
* May not be suitable for all types of images, such as low-contrast or noisy images
* Might struggle with understanding very ambiguous or high abstract prompts resulting in incorrect images being
  generated

References :

1. https://medium.com/@onkarmishra/stable-diffusion-explained-1f101284484d
2. https://huggingface.co/docs/diffusers/en/api/pipelines/stable_diffusion/img2img



## 3. GANs (Generative Adversarial Networks)
**Architecture of GANs**
* Inspired by the two-person zero-sum game in game theory.
* Consists of two different neural networks: a Generator and a Discriminator. 

![Image](https://github.com/user-attachments/assets/cda3fb26-2251-4cf5-b9f7-caf2de20dfc1)

Image Source: https://ieeexplore-ieee-org.libproxy1.nus.edu.sg/document/9514052

Generator, G
* Goal: Captures the potential distribution of real data samples and generate new data samples (fake data).
* Input: Random noise.
* Output: Fake data.

Discriminator, D
* Goal: To distinguish whether the input data is real or fake (is a classifier).
* Input: From generator and real data.
* Output: Probability that the input is real data.

Training Process (Adversarial Learning) 
* The Generator and Discriminator are trained simultaneously but in competition.
* The Discriminator is trained on real images from a dataset and fake images from the Generator.
* The Generator is trained to improve at fooling the Discriminator.
* Over time, the Generator learns to produce highly realistic images.

Optimization
* Min-max loss function 
<img width="294" alt="image" src="https://github.com/user-attachments/assets/2dc0ed84-afbe-438f-a3f4-fb018513e4c9" />

* A discriminator D: wants to maximize the classification between the distribution from real data and the one from fake data.
  * Hope D(x) increases = discriminator can identify real data more accurately.
  * At the same time, hope D(G(z)) decreases = identify the fake data more accurately.
  * Therefore, we minimize G.
* A generator G: To maximize the loss function for generator.
  * hope D(G(z)) increases = fake data looks like real data afther the optimizations.
  <img width="163" alt="image" src="https://github.com/user-attachments/assets/3f08ad12-cb20-4246-9c10-ae2830220578" />


| Advantages       |Disadvantages       | 
| ------------- |:-------------:| 
| Synthesize realistic images      | Difficulty in evaluation performance| 
| Can be trained on a variety of data types      | Training instability     |  
| Unsupervised learning | Limited control over the features      |   

References:

http://ieeexplore-ieee-org.libproxy1.nus.edu.sg/document/9514052 

https://www.researchgate.net/publication/381416905_Image_Processing_and_Optimization_Using_Deep_Learning-Based_Generative_Adversarial_Networks_GANs 




# Model Choice

1. Diffusion model are capable of taking in input and the condition to which we could imposed on the original product,
   making customization feasible
2. GANs and VAEs are good at generating variants of the picture but hard to be conditioned on.
3. Diffusion model don't fully regenerate the product (by using depth map, line-art, canny image etc) allowing for
   efficient generation of the model.

# Prototype Model

Two prototype model has been implemented:

1. ControlNet (```src\control_net.py```)
2. Diffusion Model (```src\img2imggen_evaluation.py```)

## ControlNet

![image](https://github.com/user-attachments/assets/e946dedc-ff56-436b-96d0-4a8fbc8edd80)
*<p style="text-align:centre;">Figure 4 Basic ControlNet Unit</p>*
ControlNet is a derivative of the diffusion model. It enhances the diffusion model feature by allowing extra conditions
to be imposed while generating images. Figure 4 shows the additional architecture ControlNet added on to the original
diffusion model. It has the following features:

* The neural network block is referred to as the full diffusion model. The model weights will remain constant (locked)
  to preserve the original model function throughout the inference process.
* The neural network block is then replicated and added to the base model as a trainable copy. It's the change of
  weights in this block that allows the ControlNet to shape the diffusion model.
* Zero Convolution here refers to the 1*1 convolution with both weight and bias initialized as 0, which is an
  element-wise transformation to the matrix.
* The zero convolution will be tuned as the model denoising process progress to adjust the effect of trainable weights

![image](https://github.com/user-attachments/assets/f9a487d1-9316-4509-8e21-871d887d15f1)
*<p style="text-align:centre;">Figure 5 Full ControlNet Architecture</p>*

References:

1. https://huggingface.co/docs/diffusers/en/using-diffusers/controlnet
2. https://github.com/lllyasviel/ControlNet



