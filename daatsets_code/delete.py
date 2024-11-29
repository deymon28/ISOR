'''
Xview видалення не обднакових зображень(640*640)
'''

import os
from pathlib import Path
from PIL import Image

image_dir = Path(r'D:\DYPLOMA\datasets\images\tiles\train') 
label_dir = Path(r'D:\DYPLOMA\datasets\labels\tiles\train') 

for img_path in image_dir.glob('*.tif'):
    img = Image.open(img_path)
    width, height = img.size
    
    if width != 640 or height != 640:
        print(f"Видалення зображення: {img_path.name} (Розмір: {width}x{height})")
        
        img.close()
        
        try:
            os.remove(img_path)
            
            lbl_path = label_dir / img_path.with_suffix('.txt').name
            if lbl_path.exists():
                os.remove(lbl_path)
                print(f"Видалено файл анотацій: {lbl_path.name}")
        except Exception as e:
            print(f"Помилка при видаленні {img_path.name}: {e}")
