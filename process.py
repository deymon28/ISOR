'''
Файл тайлової обробки зображень для програми
'''


import torch
from ultralytics import YOLO
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from collections import Counter
import os
import sys
import json

def load_yolo_model(yolo_model_path):
    try:
        model = YOLO(yolo_model_path)
        return model
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        return None

def process_image(model, image_path, output_path, tile_size=4096, overlap_ratio=0.2, detection_threshold=0.5, model_imgsz=2048):
    try:
        Image.MAX_IMAGE_PIXELS = None  # DecompressionBombError
        img = Image.open(image_path)
        img = img.convert("RGB")
    except Exception as e:
        print(f"Error loading image: {e}")
        return None, None

    img_width, img_height = img.size
    overlap = int(tile_size * overlap_ratio)
    stride = tile_size - overlap

    final_image = img.copy()
    draw_final = ImageDraw.Draw(final_image)
    font = ImageFont.load_default()

    seen_objects = []
    object_count = 0
    class_counter = Counter()

    for top in range(0, img_height, stride):
        for left in range(0, img_width, stride):
            right = min(left + tile_size, img_width)
            bottom = min(top + tile_size, img_height)
            tile = img.crop((left, top, right, bottom))

            results = model.predict(source=tile, imgsz=model_imgsz, conf=detection_threshold)

            if results and results[0].obb is not None:
                obb_boxes = results[0].obb.xyxyxyxy.cpu().numpy()
                confs = results[0].obb.conf.cpu().numpy()
                classes = results[0].obb.cls.cpu().numpy()
                names = results[0].names

                for i, obb_box in enumerate(obb_boxes):
                    coords = obb_box.flatten()
                    conf = confs[i]
                    class_idx = int(classes[i])
                    label = f"{names[class_idx]} {conf:.2f}"

                    adjusted_coords = [(coords[j] + left if j % 2 == 0 else coords[j] + top) for j in range(len(coords))]
                    seen_objects.append({'coords': adjusted_coords, 'conf': conf, 'class_idx': class_idx})
                    object_count += 1
                    class_counter[class_idx] += 1

                    draw_final.polygon(adjusted_coords, outline="red", width=1)
                    min_x, min_y = np.min(adjusted_coords[::2]), np.min(adjusted_coords[1::2])
                    text_offset = 6
                    draw_final.rectangle([min_x, min_y - text_offset - 10, min_x + len(label) * 6, min_y - text_offset], fill="black")
                    draw_final.text((min_x, min_y - text_offset - 10), label, fill="white", font=font)

    final_image.save(output_path, format="PNG")

    info_output_path = os.path.splitext(output_path)[0] + "_info.txt"
    with open(info_output_path, 'w') as info_file:
        if class_counter:
            for class_idx, count in class_counter.items():
                class_name = names[class_idx] if names else str(class_idx)
                info_file.write(f"{class_name}: {count}\n")
            info_file.write(f"Total detected objects: {object_count}\n")
        else:
            info_file.write("No detections made.")

    return final_image, class_counter


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process.py <config.json>")
        sys.exit(1)

    config_path = sys.argv[1]
    with open(config_path, 'r') as f:
        config = json.load(f)

    yolo_model_path = config.get("yolo_model_path")
    image_path = config.get("image_path")
    output_path = config.get("output_path")
    detection_threshold = config.get("detection_threshold", 0.5)
    tile_size = config.get("tile_size", 4096)
    model_imgsz = config.get("model_imgsz", 2048)

    model = load_yolo_model(yolo_model_path)
    if model:
        final_image, class_counter = process_image(model, image_path, output_path, tile_size, 0.2, detection_threshold, model_imgsz)
        if final_image is not None:
            # final_image.show()
            # for class_idx, count in class_counter.items():
            #     print(f"{class_idx}: {count}")
            for class_idx, count in class_counter.items():
                class_name = model.names[class_idx] if hasattr(model, 'names') else str(class_idx)
                print(f"{class_name}: {count}")
            print(f"Total detected objects: {sum(class_counter.values())}")
