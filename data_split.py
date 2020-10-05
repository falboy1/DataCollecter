from pathlib import Path
import sqlite3
import os
import shutil
import pprint


def make_dirs(class_name):
    # 各種フォルダの作成
    train_dir = Path('./train' / class_name)
    train_dir.mkdir(exist_ok=True, parents=True)
    val_dir = Path('./val' / class_name)
    val_dir.mkdir(exist_ok=True, parents=True)


def append_img_path(conn, files_dic):
    # データを取得して各クラスごとに用意されたリストに画像パス格納
    query = 'SELECT noninvasive, invasive, path FROM Avocados'

    for row in conn.execute(query):
        noninvasive = row[2]
        invasive = row[3]
        img_path = row[5]

        correct_label = None
        if invasive != 'NULL':
            correct_label = invasive
        else:
            correct_label = noninvasive

        files_dic[correct_label].append(img_path)


def split_images(files_dic, ratio=0.8):
    
    for k, files in files_dic.items():
        img_num = len(files)

        for i, file_path in enumerate(files):
            if i <= img_num * ratio:
                shutil.copy2(file_path, 'train/' + k + '/' + file_path)
                print(file_path, 'train/' + k + '/' + file_path)
            else:
                shutil.copy2(file_path, 'val/' + k + '/' + file_path)
                print(file_path, 'val/' + k + '/' + file_path)





# ディレクトリ読み込み
cwd = Path('.')
cwd.glob()

# 対象のクラス
CLASS_NAMES = ('unripe', 'ripe', 'overripe')
files_dic = {}

# 画像格納先ディレクトリ作成
for cn in CLASS_NAMES:
    make_dirs(cn)
    # 空のリストを各クラス名ごとに作成
    files_dic{cn: list()}
    

# データベースファイル読み込み
db_path = 'test4.db'
conn = sqlite3.connect(db_path)

append_img_path(conn, files_dic)
split_images(files_dic, 0.8)



split_files('unripe')
split_files('ripe')
split_files('overripe')

