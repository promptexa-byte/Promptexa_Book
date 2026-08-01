# -*- coding: utf-8 -*-
"""
اسکریپت ساخت فایل EXE از کتاب امن
با استفاده از PyInstaller

⚠️ نکته حیاتی: این اسکریپت را باید روی خود سیستم ویندوزی که می‌خواهید
exe برایش بسازید اجرا کنید. PyInstaller یک کامپایلر Cross-Platform
نیست؛ اجرای آن روی لینوکس/مک، فایل اجرایی همان سیستم‌عامل را می‌سازد
نه exe ویندوز.

نویسنده: وحید خلج
"""

import os
import sys
import subprocess
import shutil
import platform

def build_exe():
    print("=" * 70)
    print("🚀  ساخت فایل EXE کتاب امن اندروید WebView")
    print("📚  نویسنده: وحید خلج - www.promptexa.ir")
    print("=" * 70)

    if platform.system() != "Windows":
        print("\n⚠️  هشدار: شما در حال اجرای این اسکریپت روی",
              platform.system(), "هستید، نه ویندوز.")
        print("    خروجی این اجرا یک فایل اجرایی مخصوص همین سیستم‌عامل")
        print("    خواهد بود (نه exe ویندوز). برای exe واقعی، این اسکریپت")
        print("    را روی یک سیستم ویندوزی واقعی اجرا کنید.\n")

    for folder in ["build", "dist", "__pycache__"]:
        if os.path.exists(folder):
            print(f"🗑️  حذف پوشه {folder}...")
            shutil.rmtree(folder, ignore_errors=True)

    print("\n📦  نصب وابستگی‌های مورد نیاز...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install",
                                "PyQt5", "pyinstaller"])
        print("✅  وابستگی‌ها نصب شدند.")
    except Exception as e:
        print(f"❌  خطا در نصب وابستگی‌ها: {e}")
        return

    print("\n🔧  ساخت فایل اجرایی...")

    data_sep = ";" if platform.system() == "Windows" else ":"
    app_out_name = "کتاب_امن_اندروید_WebView"

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        f"--name={app_out_name}",
        f"--add-data=style.qss{data_sep}.",
        "book_reader.py",
    ]

    if os.path.exists("icon.ico") and platform.system() == "Windows":
        cmd.insert(3, "--icon=icon.ico")

    try:
        subprocess.check_call(cmd)

        exe_name = app_out_name + (".exe" if platform.system() == "Windows" else "")
        exe_path = os.path.join("dist", exe_name)
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            # کپی فایل کتاب کنار exe، فقط برای راحتی تست فوری —
            # ویوور خودش عمومی است و با هر فایل .ptxbook دیگری هم کار می‌کند
            if os.path.exists("book.ptxbook"):
                shutil.copy("book.ptxbook", os.path.join("dist", "book.ptxbook"))
            print("\n" + "=" * 70)
            print("✅  ساخت فایل اجرایی با موفقیت انجام شد!")
            print(f"📁  مسیر: {exe_path}")
            print(f"📏  حجم: {size_mb:.2f} MB")
            print("=" * 70)
            print("\n🎉  نرم‌افزار آماده اجراست — یک ویوور عمومی است.")
            print("    برای باز کردن کتاب: اجرا کن، بعد از دکمه «باز کردن فایل کتاب»")
            print("    فایل book.ptxbook کنارش را انتخاب کن (یا بکِش و رهایش کن).")
            print("📖  کتاب امن اندروید WebView - وحید خلج")
            print("🌐  www.promptexa.ir | www.ptxplus.ir")
        else:
            print("❌  فایل اجرایی ساخته نشد؛ خروجی بالا را برای خطا بررسی کنید.")

    except Exception as e:
        print(f"❌  خطا در ساخت فایل اجرایی: {e}")


if __name__ == "__main__":
    build_exe()
