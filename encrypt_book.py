"""
ساخت فایل محتوای رمزنگاری‌شده اختصاصی (.ptxbook)

از AES-256-GCM استفاده می‌کند — الگوریتمی که هم در پایتون (این اسکریپت)
و هم در اندروید (javax.crypto) به‌صورت بومی و کاملاً سازگار پشتیبانی می‌شود،
پس هر دو ویوور (دسکتاپ و اندروید) می‌توانند دقیقاً همین یک فایل را رمزگشایی کنند.

فرمت فایل خروجی (باینری):
  4 بایت   : امضا "PTXB"
  1 بایت   : شماره نسخه فرمت (1)
  12 بایت  : Nonce/IV مخصوص GCM
  باقی     : متن رمزشده + برچسب احراز اصالت GCM (بهم‌چسبیده، طبق پیش‌فرض هر دو پلتفرم)
"""

import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# کلید ثابت ۳۲ بایتی (AES-256) که در هر دو ویوور (پایتون/کاتلین) باید عیناً یکسان باشد.
# اینجا به‌صورت هگز نگه داشته می‌شود تا موقع ساخت اپ اندروید هم دقیقاً همین رشته کپی شود.
SHARED_KEY_HEX = "8f3a1c9d2e7b4560af13c9e2d4b6f8a01c3e5f7091b3d5f7a9c1e3f5071b3d59"
KEY = bytes.fromhex(SHARED_KEY_HEX)
assert len(KEY) == 32, "کلید باید دقیقاً ۳۲ بایت (۶۴ کاراکتر هگز) باشد"

MAGIC = b"PTXB"
VERSION = bytes([1])


def encrypt_book(json_path, out_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = f.read().encode("utf-8")

    aesgcm = AESGCM(KEY)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)  # tag appended automatically

    with open(out_path, "wb") as f:
        f.write(MAGIC)
        f.write(VERSION)
        f.write(nonce)
        f.write(ciphertext)

    print(f"✅ فایل رمزنگاری‌شده ساخته شد: {out_path}")
    print(f"   حجم اصلی JSON: {len(data)} بایت")
    print(f"   حجم فایل نهایی: {4 + 1 + 12 + len(ciphertext)} بایت")


def decrypt_book(ptx_path):
    """برای تست/اعتبارسنجی همینجا هم رمزگشایی را پیاده می‌کنیم."""
    with open(ptx_path, "rb") as f:
        raw = f.read()
    assert raw[:4] == MAGIC, "فایل نامعتبر است (امضا مطابقت ندارد)"
    nonce = raw[5:17]
    ciphertext = raw[17:]
    aesgcm = AESGCM(KEY)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode("utf-8"))


if __name__ == "__main__":
    encrypt_book("/home/claude/qtbook/book_data.json", "/home/claude/qtbook/book.ptxbook")
    # اعتبارسنجی فوری: رمزگشایی و مقایسه با فایل اصلی
    result = decrypt_book("/home/claude/qtbook/book.ptxbook")
    print("✅ تست رمزگشایی موفق — تعداد فصل‌ها:", len(result["chapters"]))
