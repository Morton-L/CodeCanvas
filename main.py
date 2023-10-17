import csv
import datetime
import hashlib
import gvcode
import os
import random
import shutil
from io import BytesIO

from captcha.image import ImageCaptcha
from tqdm import tqdm


class CodeCanvas:
    def __init__(self):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_dir = './captchas_output'
        self.project_dir = f'{output_dir}/{current_time}'
        self.csv_path = f'{self.project_dir}/dataframe.csv'
        self.image_dir = f'{self.project_dir}/images'

        self.characters = ''
        self.include_digits = True
        self.include_uppercase_letters = False
        self.include_lowercase_letters = False
        self.include_specials = False

        self.num_captchas = 1

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_captcha(
        self,
        lib: str = 'captcha',
        captcha_length: int = 4,
        min_captcha_length: int = None,
        max_captcha_length: int = None,
    ):
        """
        生成验证码
        :param lib: 使用的验证码库
        :param captcha_length: 验证码长度（当配置了min_captcha_length和max_captcha_length时无效）
        :param min_captcha_length: 动态验证码长度的最小长度
        :param max_captcha_length: 动态验证码长度的最大长度
        """
        if self.include_digits:
            self.characters += '0123456789'
        if self.include_uppercase_letters:
            self.characters += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if self.include_lowercase_letters:
            self.characters += 'abcdefghijklmnopqrstuvwxyz'
        if self.include_specials:
            self.characters += '!@#$%^&*()-_=+'
        lib_map = {
            'captcha': self.generate_with_captcha,
            'pillow': self.generate_with_pillow,
            'gvcode': self.generate_with_gvcode,
        }
        func = lib_map.get(lib)
        if not func:
            raise ValueError(f"Unsupported library: {lib}")

        if os.path.exists(self.project_dir):
            # 删除整个目录
            shutil.rmtree(self.project_dir)
            # 无论目录是否已存在，都重新创建它
        os.makedirs(self.project_dir)
        os.makedirs(self.image_dir)
        # 创建或追加写入CSV文件的头
        with open(self.csv_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['file', 'label'])

        if min_captcha_length is not None and max_captcha_length is not None:
            captcha_length = random.randint(min_captcha_length, max_captcha_length)

        for i in tqdm(range(self.num_captchas), desc="生成验证码", unit="个"):
            if min_captcha_length is not None and max_captcha_length is not None:
                captcha_length = random.randint(min_captcha_length, max_captcha_length)
            func(captcha_length=captcha_length)

        print(f"生成 {self.num_captchas} 个验证码 -> Done")

    def generate_with_captcha(self, captcha_length: int):
        captcha_text = ''.join(random.choice(self.characters) for _ in range(captcha_length))
        image_captcha = ImageCaptcha()
        image = image_captcha.generate_image(captcha_text)

        self.save_image(captcha_image=image, captcha_text=captcha_text)

    def generate_with_gvcode(self, captcha_length: int):
        image, captcha_text = gvcode.generate(
            length=captcha_length,
            chars=self.characters
        )
        self.save_image(captcha_image=image, captcha_text=captcha_text)

    def generate_with_pillow(self, captcha_length: int):
        # TODO: 使用pillow生成验证码
        pass

    def save_image(self, captcha_image, captcha_text):
        # 计算图片的SHA1值
        with BytesIO() as buffer:
            captcha_image.save(buffer, format="PNG")
            img_data = buffer.getvalue()
            sha1 = hashlib.sha1(img_data).hexdigest()

        image_path = os.path.join(self.image_dir, f"{captcha_text}_{sha1}.png")
        captcha_image.save(image_path)

        # 将图像路径和标签写入CSV文件
        with open(self.csv_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([f"{captcha_text}_{sha1}.png", captcha_text])


if __name__ == '__main__':
    CodeCanvas = CodeCanvas()

    CodeCanvas.include_digits = True  # 数字
    CodeCanvas.include_uppercase_letters = True  # 大写字母
    CodeCanvas.include_lowercase_letters = True  # 小写字母
    CodeCanvas.include_specials = False  # 特殊符号

    CodeCanvas.num_captchas = 200
    CodeCanvas.generate_captcha(lib='captcha', captcha_length=4, min_captcha_length=3, max_captcha_length=8)
