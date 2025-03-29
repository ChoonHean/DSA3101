from synthcity.utils.serialization import save_to_file, load_from_file
from synthcity.plugins.core.dataloader import ImageDataLoader
from synthcity.plugins import Plugins
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
import torch
import os

class CustomImageDataset(Dataset):
    def __init__(self, image_folder, transform=None):
        self.image_folder = image_folder
        self.image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg')][:2]
        self.transform = transform

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_path = os.path.join(self.image_folder, self.image_files[idx])
        image = Image.open(img_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        label = torch.tensor([idx % 10], dtype=torch.long)  # Ensure label is a tensor with shape [1]
        return image, label

# Define any transformations (e.g., resizing, normalization) if needed
transform = transforms.Compose([
    transforms.Resize((32, 32)),  # Resize images to 32x32 pixels
    transforms.ToTensor(),       # Convert images to PyTorch tensors
    # Add more transformations as needed
])

# Initialize the custom dataset
dataset = CustomImageDataset(image_folder='dataset/images', transform=transform)

# Step 3: Initialize ImageDataLoader
loader = ImageDataLoader(data=dataset, height=32, width=32)


Plugins(categories = ["images"]).list()
syn_model = Plugins().get("image_cgan")
syn_model.patience_metric = None
syn_model.fit(loader)

save_to_file("models/synthcity_cgan.pkl", syn_model)
reloaded = load_from_file("models/synthcity_cgan.pkl")

syn_img, syn_labels = syn_model.generate(count=10).unpack().numpy()


