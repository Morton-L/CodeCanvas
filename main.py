import hashlib
import os
import random
import shutil
from io import BytesIO

from captcha.image import ImageCaptcha


class CodeCanvas:
    def __init__(self):
        self.characters = ''
        self.save_dir = './captchas_output'
        self.include_digits = True
        self.include_uppercase_letters = False
        self.include_lowercase_letters = False
        self.include_specials = False

        self.num_captchas = 1

    def generate_captcha(self, lib: str = 'captcha', captcha_length: int = 4):
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
            'pillow': self.generate_with_pillow
        }
        func = lib_map.get(lib)
        if not func:
            raise ValueError(f"Unsupported library: {lib}")

        if os.path.exists(self.save_dir):
            # 删除整个目录
            shutil.rmtree(self.save_dir)
            # 无论目录是否已存在，都重新创建它
        os.makedirs(self.save_dir)

        print_frequency = 200  # 例如每生成100个验证码打印一次
        for i in range(1, self.num_captchas + 1):
            func(captcha_length=captcha_length)
            if i % print_frequency == 0:
                print(f"已经生成 {i} 个验证码...")

        print(f"生成 {self.num_captchas} 个验证码 -> Done")

    def generate_with_captcha(self, captcha_length: int):
        captcha_text = ''.join(random.choice(self.characters) for _ in range(captcha_length))
        image_captcha = ImageCaptcha()
        image = image_captcha.generate_image(captcha_text)

        # 计算图片的SHA1值
        with BytesIO() as buffer:
            image.save(buffer, format="PNG")
            img_data = buffer.getvalue()
            sha1 = hashlib.sha1(img_data).hexdigest()

        image_path = os.path.join(self.save_dir, f"{captcha_text}_{sha1}.png")
        image.save(image_path)

    def generate_with_pillow(self, captcha_length: int):
        pass


if __name__ == '__main__':
    CodeCanvas = CodeCanvas()

    CodeCanvas.include_digits = True
    CodeCanvas.include_uppercase_letters = True
    CodeCanvas.include_lowercase_letters = True
    CodeCanvas.include_specials = False

    CodeCanvas.num_captchas = 2000
    CodeCanvas.generate_captcha(lib='captcha', captcha_length=4)
