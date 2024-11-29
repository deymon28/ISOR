import os
import cv2
import numpy as np
from glob import glob
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def apply_blur(image, strength):
    return image.filter(ImageFilter.GaussianBlur(strength))

def apply_darker(image, factor):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

def apply_lighter(image, factor):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

def apply_fog(image, intensity):
    fog = Image.new('RGB', image.size, (255, 255, 255))
    return Image.blend(image, fog, intensity)

def apply_noise(image, noise_level):
    np_image = np.array(image)
    noise = np.random.normal(0, noise_level, np_image.shape).astype(np.uint8)
    noisy_image = cv2.add(np_image, noise)
    return Image.fromarray(np.clip(noisy_image, 0, 255))

def apply_contrast(image, factor):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

def apply_sharpness(image, factor):
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(factor)

def apply_flip(image, annotation_data, img_width):
    flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)
    flipped_annotations = []
    for line in annotation_data:
        parts = line.strip().split()
        if len(parts) == 9:
            class_id = int(parts[0])
            x1, y1, x2, y2, x3, y3, x4, y4 = map(float, parts[1:])
            x1, x2, x3, x4 = 1.0 - x1, 1.0 - x2, 1.0 - x3, 1.0 - x4
            flipped_annotations.append(f"{class_id} {x1} {y1} {x2} {y2} {x3} {y3} {x4} {y4}\n")
    return flipped_image, flipped_annotations

def apply_solarize(image, threshold):
    return ImageOps.solarize(image, threshold)

def apply_color_jitter(image, factor):
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)

def process_images(input_folder, annotation_folder, output_image_folder, output_annotation_folder):
    if not os.path.exists(output_image_folder):
        os.makedirs(output_image_folder)
    if not os.path.exists(output_annotation_folder):
        os.makedirs(output_annotation_folder)
    
    image_paths = glob(os.path.join(input_folder, "*.jpg"))
    
    for image_path in image_paths:
        image_name = os.path.basename(image_path)
        annotation_name = os.path.splitext(image_name)[0] + '.txt'
        annotation_path = os.path.join(annotation_folder, annotation_name)
        
        image = Image.open(image_path)
        img_width, img_height = image.size
        
        if os.path.exists(annotation_path):
            with open(annotation_path, 'r') as ann_file:
                annotation_data = ann_file.readlines()
        else:
            annotation_data = []
        
        augmentations = {
            "blur_": lambda img, ann: (apply_blur(img, random.uniform(0.5, 3.0)), ann),
            "darker_": lambda img, ann: (apply_darker(img, random.uniform(0.3, 0.7)), ann),
            "lighter_": lambda img, ann: (apply_lighter(img, random.uniform(1.3, 1.7)), ann),
            "fog_": lambda img, ann: (apply_fog(img, random.uniform(0.1, 0.3)), ann),
            "noise_": lambda img, ann: (apply_noise(img, random.randint(5, 30)), ann),
            "contrast_": lambda img, ann: (apply_contrast(img, random.uniform(0.7, 1.5)), ann),
            "sharpness_": lambda img, ann: (apply_sharpness(img, random.uniform(0.5, 2.0)), ann),
            "flip_": lambda img, ann: apply_flip(img, ann, img_width),
            "solarize_": lambda img, ann: (apply_solarize(img, random.randint(100, 200)), ann),
            "color_jitter_": lambda img, ann: (apply_color_jitter(img, random.uniform(0.7, 1.3)), ann),
        }
        
        for prefix, augmentation in augmentations.items():
            augmented_image, augmented_annotations = augmentation(image, annotation_data)
            augmented_image_path = os.path.join(output_image_folder, prefix + image_name)
            augmented_image.save(augmented_image_path)
            
            augmented_annotation_path = os.path.join(output_annotation_folder, prefix + annotation_name)
            with open(augmented_annotation_path, 'w') as ann_out_file:
                ann_out_file.writelines(augmented_annotations)
    
    sample_images = glob(os.path.join(output_image_folder, "*.jpg"))[:5]
    for sample_image_path in sample_images:
        image = Image.open(sample_image_path)
        annotation_path = os.path.join(output_annotation_folder, os.path.splitext(os.path.basename(sample_image_path))[0] + '.txt')
        
        if os.path.exists(annotation_path):
            with open(annotation_path, 'r') as ann_file:
                annotation_data = ann_file.readlines()
        
        np_image = np.array(image)
        plt.imshow(np_image)
        
        for line in annotation_data:
            parts = line.strip().split()
            if len(parts) == 9:
                class_id = int(parts[0])
                x1, y1, x2, y2, x3, y3, x4, y4 = map(float, parts[1:])
                img_height, img_width, _ = np_image.shape
                
                x1_pixel, y1_pixel = x1 * img_width, y1 * img_height
                x2_pixel, y2_pixel = x2 * img_width, y2 * img_height
                x3_pixel, y3_pixel = x3 * img_width, y3 * img_height
                x4_pixel, y4_pixel = x4 * img_width, y4 * img_height
                
                polygon = Polygon([(x1_pixel, y1_pixel), (x2_pixel, y2_pixel), (x3_pixel, y3_pixel), (x4_pixel, y4_pixel)],
                                  linewidth=1, edgecolor='r', facecolor='none')
                plt.gca().add_patch(polygon)
                plt.text(x1_pixel, y1_pixel, f'Class {int(class_id)}', color='red', fontsize=6)
        
        plt.axis('off')
        plt.show()

if __name__ == "__main__":
    input_folder =r"C:\Users\dimag\Desktop\samll-dataset\images\train"
    annotation_folder = r"C:\Users\dimag\Desktop\samll-dataset\labels\train"
    output_image_folder = r"C:\Users\dimag\Desktop\samll-dataset\output\images"
    output_annotation_folder = r"C:\Users\dimag\Desktop\samll-dataset\output\annotations"
    process_images(input_folder, annotation_folder, output_image_folder, output_annotation_folder)
