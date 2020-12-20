from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
import cv2
import numpy as np
import sqlite3
import time
import datetime
import copy

# 画面サイズ設定
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '500')

# カメラサイズ設定
CAPTURE_WIDTH = 600
CAPTURE_HEIGHT = 600

# 撮影ボタン
class ImageButton(ButtonBehavior, Image):
    preview = ObjectProperty(None)

    def buttonCaptureClicked(self):
        pass

# 撮影した画像を入れるレイアウト
class CapturedImages(BoxLayout):
    pass

# 撮影された画像
class CapturedImage(ButtonBehavior, Image):
    main = ObjectProperty(None)
    index = NumericProperty(None)
    # クリック時
    def on_press(self):
        self.index = (len(self.parent.children) - 1) - self.parent.children.index(self)
        print(main.values(self.index))

# カメラプレビュー
class CameraPreview(Image):
    texture = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(CameraPreview, self).__init__(**kwargs)
        # 0番目のカメラに接続
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
        # 描画のインターバルを設定
        Clock.schedule_interval(self.update, 1.0 / 10)

    # インターバルで実行する描画メソッド
    def update(self, dt):
        # フレームを読み込み
        ret, self.frame = self.capture.read()
        # Kivy Textureに変換
        buf1 = cv2.flip(self.frame, 0)
        buf = buf1.tostring()
        texture = Texture.create(size=(self.frame.shape[1], self.frame.shape[0]), colorfmt='bgr') 
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # インスタンスのtextureを変更
        self.texture = texture


# メインのレイアウト
class MainScreen(Widget):
    # ウィジェット系
    preview = ObjectProperty(None)
    captured_images = ObjectProperty(None)
    captured_image = ObjectProperty(None)
    textbox = ObjectProperty(None)
    # [0]->my_label, [1]->truth_label, [2]->stem_label
    label_list = ListProperty([0, 0, 0])
    # テキスト系
    button1_label = StringProperty()
    button2_label = StringProperty()
    button3_label = StringProperty()
    # ボタンカラー系
    button1_color = ListProperty()
    button2_color = ListProperty()
    # データベース系
    values = ListProperty()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        # キーボード設定
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # ボタンテキスト設定
        self.button_text_change()

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    # キープレス
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()

        # ショートカットキー
        if len(modifiers) == 1:
            if text == 'c' and modifiers[0] == 'meta':
                self.buttonCaptureClicked()
            elif text == 'a' and modifiers[0] == 'meta':
                self.button1Clicked()
            elif text == 's' and modifiers[0] == 'meta':
                self.button2Clicked()
            elif text == 'd' and modifiers[0] == 'meta':
                self.button3Clicked()
            elif text == 'f' and modifiers[0] == 'meta':
                print('f!')

        return True

    # ショートカット時の動作
    # キャプチャ command + c
    def capture(self):
        # ファイル名をシステム時刻から決定
        now = time.time()
        image_name = str(now).replace('.', '') + '.jpg'
        # 画像保存
        cv2.imwrite(image_name, self.preview.frame)
        # 画像一覧に追加
        self.captured_images.add_widget(CapturedImage(source=image_name, size_hint_y=None))
        # 保存した画像パスを返却
        return image_name

    # 登録する値のスタック
    def append_values(self, id, my_label, truth_label, stem_label, path):
        # 値を全て保管
        self.values.append([id, my_label, truth_label, stem_label, path])
        
    # 破壊検査ラベルを反映
    def apply_truth_label(self):
        # truth_labelを変更
        for value in self.values:
            value[2] = self.button2_label



    # StringPropertyを変更
    def button_text_change(self):
        unripe_color = [0, 80/256 , 0, 1]
        unripe_ripe_color = [0, 40/256, 0, 1]
        ripe_color = [53/256, 50/256, 52/256, 1]
        ripe_overripe_color = [25/256, 25/256, 25/256, 1]
        overripe_color = [0, 0, 0, 1]
        null_color = [88/256, 88/256, 88/256, 1]

        # 主観ラベル
        if self.label_list[0] % 6 == 0:
            self.button1_label = 'NULL'
            self.button1_color = null_color
        elif self.label_list[0] % 6 == 1:
            self.button1_label = 'unripe'
            self.button1_color = unripe_color
        elif self.label_list[0] % 6 == 2:
            self.button1_label = 'unripe_to_ripe'
            self.button1_color = unripe_ripe_color
        elif self.label_list[0] % 6 == 3:
            self.button1_label = 'ripe'
            self.button1_color = ripe_color
        elif self.label_list[0] % 6 == 4:
            self.button1_label = 'ripe_to_overripe'
            self.button1_color = ripe_overripe_color
        elif self.label_list[0] % 6 == 5:
            self.button1_label = 'overripe'
            self.button1_color = overripe_color

        # truthラベル
        if self.label_list[1] % 6 == 0:
            self.button2_label = 'NULL'
            self.button2_color = null_color
        elif self.label_list[1] % 6 == 1:
            self.button2_label = 'unripe'
            self.button2_color = unripe_color
        elif self.label_list[1] % 6 == 2:
            self.button2_label = 'unripe_to_ripe'
            self.button2_color = unripe_ripe_color
        elif self.label_list[1] % 6 == 3:
            self.button2_label = 'ripe'
            self.button2_color = ripe_color
        elif self.label_list[1] % 6 == 4:
            self.button2_label = 'ripe_to_overripe'
            self.button2_color = ripe_overripe_color
        elif self.label_list[1] % 6 == 5:
            self.button2_label = 'overripe'
            self.button2_color = overripe_color
        
        # stemラベル
        if self.label_list[2] % 2 == 0:
            self.button3_label = 'stem'
        elif self.label_list[2] % 2 == 1:
            self.button3_label = 'nonstem'
    

    # 撮影ボタンクリック時の動作
    def buttonCaptureClicked(self):
        # 撮影
        image_name = self.capture()
        # データ保管 id, my_label, truth_label, stem_label, path
        id = image_name.replace('.jpg', '')
        self.append_values(id, self.button1_label, self.button2_label, self.button3_label, image_name)
        print(self.values[-1])

    # 主観ラベルボタンクリック時の動作
    def button1Clicked(self):
        self.label_list[0] += 1
        self.button_text_change()
        print(self.label_list)

    # 破壊検査ラベルボタンクリック時の動作
    def button2Clicked(self):
        self.label_list[1] += 1
        self.button_text_change()
        print(self.label_list)

    # ヘタラベルボタンクリック時の動作
    def button3Clicked(self):
        self.label_list[2] += 1
        self.button_text_change()
        print(self.label_list)

    # データ挿入ボタンクリック時の動作
    def buttonInsertClicked(self):
        # テキストボックスの中身をチェック
        if self.textbox.text == '':
            print('Fill out the textbox.')
            return False

        # 破壊ラベルを全てに適用
        self.apply_truth_label()

        conn = sqlite3.connect('test4.db')
        cur = conn.cursor()

        now = datetime.datetime.now()
        capture_day = now.strftime('%Y-%m-%d %H:%M:%S')

        query = '''
            INSERT INTO Avocados(id, avo_id, noninvasive, invasive, stem, path, capture_day) VALUES(?, ?, ?, ?, ?, ?, ?);
        '''

        for v in self.values:
            v.insert(1, self.textbox.text)
            v.append(capture_day)
            cur.execute(query, v)
        conn.commit()
        cur.close()
        conn.close()
        # 各項目クリア
        self.values.clear()
        self.captured_images.clear_widgets()
        self.textbox.text = ''
        print('INSERTED!')
        return True


class CameraApp(App):
    def __init__(self, **kwargs):
        super(CameraApp, self).__init__(**kwargs)
        self.title = 'MyCameraApp'

    def on_start(self):
        print('App start.')

    def on_stop(self):
        print('App end.')

    def build(self):
        # 主要画面のインスタンスを作成
        ms = MainScreen()
        return ms


if __name__ == '__main__':
    CameraApp().run()
    cv2.destroyAllWindows()