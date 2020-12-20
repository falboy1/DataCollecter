# -*- coding: utf-8 -*-
from pathlib import Path
import sqlite3
import os
import traceback
import shutil
import pprint
import random
from PIL import Image

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def make_dirs(class_name):
    # 各種フォルダの作成
    train_dir = Path('./resized/train', class_name)
    train_dir.mkdir(exist_ok=True, parents=True)
    val_dir = Path('./resized/val', class_name)
    val_dir.mkdir(exist_ok=True, parents=True)

CLASS_NAMES = ('unripe', 'ripe', 'overripe')

train_dir = Path('./train')
val_dir = Path('./val')

for cn in CLASS_NAMES:
    make_dirs(cn)

for img_path in train_dir.glob('**/*.jpg'):
    img = Image.open(img_path)
    new_img = crop_center(img, 480, 480)
    new_img.save('resized/' + str(img_path), quality=95)

for img_path in val_dir.glob('**/*.jpg'):
    img = Image.open(img_path)
    new_img = crop_center(img, 480, 480)
    new_img.save('resized/' + str(img_path), quality=95)