# -*- coding: utf-8 -*-
from pathlib import Path
import sqlite3
import os
import traceback
import shutil
import pprint
import random
from PIL import Image


def make_dirs(class_name):
    # 各種フォルダの作成
    train_dir = Path('./train', class_name)
    train_dir.mkdir(exist_ok=True, parents=True)
    val_dir = Path('./val', class_name)
    val_dir.mkdir(exist_ok=True, parents=True)


def append_img_path(conn, files_dic, num):
    # データを取得して各クラスごとに用意されたリストに画像パス格納
    query = 'SELECT noninvasive, invasive, path FROM Avocados'

    for row in conn.execute(query):
        noninvasive = row[0]
        invasive = row[1]
        img_path = row[2]
        #print(noninvasive, invasive, img_path)
        correct_label = None
        # ラベルなしデータはスキップ
        if invasive == 'NULL' and noninvasive == 'NULL':
            continue
        # ラベルありデータに対する処理
        if invasive != 'NULL':
            correct_label = invasive
        else:
            correct_label = noninvasive
        #print(correct_label)
        if correct_label == 'ripe_to_overripe' or correct_label == 'unripe_to_ripe':
            continue

        # label名をkeyに持つ辞書にパスが格納されていく
        files_dic[correct_label].append(img_path)
    
    for k, v in files_dic.items():
        # 全ての画像パスが格納されているところからランダムにnum個選び直す (重複なし)
        # 画像数が指定数を下回るクラスはなにもしない (全ての画像が使用される)
        if  len(files_dic[k]) < num:
            pass
        else:
            files_dic[k] = random.sample(v, num)


def split_images(files_dic, ratio=0.8):
    
    for k, files in files_dic.items():
        img_num = len(files)
        print(img_num)

        try:
            for i, file_path in enumerate(files):
                if i < img_num * ratio:
                    shutil.copy2('./images/' + file_path, 'train/' + k + '/' + file_path)
                    #print('./images/' + file_path, 'train/' + k + '/' + file_path)
                else:
                    shutil.copy2('./images/' + file_path, 'val/' + k + '/' + file_path)
                    #print('./images' + file_path, 'val/' + k + '/' + file_path)
        except Exception:
            traceback.print_exc()





# 対象のクラス
CLASS_NAMES = ('unripe', 'ripe', 'overripe')
files_dic = {}
# 1クラスにおける最大画像
MAX_NUM = 300

# 画像格納先ディレクトリ作成
for cn in CLASS_NAMES:
    make_dirs(cn)
    # 空のリストを各クラス名ごとに作成
    files_dic[cn] = []


# データベースファイル読み込み
db_path = 'test4.db'
conn = sqlite3.connect(db_path)

append_img_path(conn, files_dic, MAX_NUM)
split_images(files_dic, 0.8)

