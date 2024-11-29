'''
Скрипт виправлення анотацій власного міні датасету. Виправлення до відповідності дота датасету
'''

import os
import yaml

new_annotations_path = r"C:\Users\dimag\Desktop\samll-dataset\train\labels"  
yaml_old_path = r"D:\DYPLOMA\dota1.5_yolo.yaml"  
yaml_new_path = r"C:\Users\dimag\Desktop\samll-dataset\data.yaml" 

with open(yaml_old_path, 'r') as f:
    old_classes = yaml.safe_load(f)['names']

with open(yaml_new_path, 'r') as f:
    new_classes = yaml.safe_load(f)['names']

new_to_old_mapping = {}
for new_index, new_name in new_classes.items():
    for old_index, old_name in old_classes.items():
        if new_name.replace('-', ' ') == old_name:
            new_to_old_mapping[new_index] = old_index
            break

for annotation_file in os.listdir(new_annotations_path):
    if annotation_file.endswith(".txt"):
        annotation_path = os.path.join(new_annotations_path, annotation_file)
        with open(annotation_path, 'r') as f:
            lines = f.readlines()
        
        updated_lines = []
        for line in lines:
            parts = line.strip().split()
            class_id = int(parts[0])
            if class_id in new_to_old_mapping:
                parts[0] = str(new_to_old_mapping[class_id])
                updated_lines.append(" ".join(parts))
            else:
                print(f"Warning: Class ID {class_id} in file {annotation_file} not found in mapping.")
                updated_lines.append(line.strip()) 
 
        with open(annotation_path, 'w') as f:
            f.write("\n".join(updated_lines))

print("+")
