# ==================== IMPORTS ====================
import asyncio
from random import randint
import requests
from time import sleep
import os
from PIL import Image
from dotenv import get_key

# ==================== DELETE PREVIOUS IMAGES ====================
def delete_previous_images(prompt: str):
    folder_path = "Data"
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
                print(f"Deleted: {image_path}")
            except Exception as e:
                print(f"Failed to delete {image_path}: {e}")

# ==================== IMAGE OPEN FUNCTION ====================
def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")  # Normalize prompt to match filename pattern
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
       
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
                # Use 'start' to open in default Photos app (Windows only)
            img.show()
            sleep(1)
        except IOError:
                print(f"Unable to open {image_path}")
        else:
            print(f"Image not found: {image_path}")
# ==================== API SETUP ====================
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# ==================== API QUERY FUNCTION ====================
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

# ==================== IMAGE GENERATION FUNCTION ====================
async def generate_images(prompt: str):
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality-4K, sharpness-maximum, Ultra High details, high resolution, seed {randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        with open(fr"Data\{prompt.replace(' ', '_')}{i + 1}.jpg", "wb") as f:
            f.write(image_bytes)

# ==================== WRAPPER FUNCTION ====================
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# ==================== MAIN MONITORING LOOP ====================
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()
            Prompt, Status = Data.split(",")

        if Status == "True":
            print("Generating Images ...")
            ImageStatus = GenerateImages(prompt=Prompt)

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
                break
        else:
            sleep(1)
    except:
        pass
