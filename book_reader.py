# -*- coding: utf-8 -*-
"""
کتاب امن اندروید WebView
نرم‌افزار خواننده کتاب الکترونیک با امنیت بالا
نسخه 1.0.0
نویسنده: وحید خلج
وب‌سایت: www.promptexa.ir | www.ptxplus.ir

نحوه اجرا (روی ویندوز، مک یا لینوکس - با پایتون نصب‌شده):
    pip install -r requirements.txt
    python book_reader.py

ساخت فایل exe واقعی (فقط باید روی خود ویندوز اجرا شود؛ PyInstaller
یک کامپایلر Cross-Platform نیست و exe واقعی فقط وقتی تولید می‌شود
که این اسکریپت را روی یک سیستم ویندوزی واقعی اجرا کنید):
    python build_exe.py
"""

import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QFrame, QTextEdit, QPushButton,
    QMessageBox, QScrollArea, QSizePolicy, QLineEdit, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QTextCursor
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

APP_NAME = "کتاب امن اندروید WebView"
APP_VERSION = "1.0.0"
AUTHOR = "وحید خلج"
WEBSITE1 = "www.promptexa.ir"
WEBSITE2 = "www.ptxplus.ir"
WATERMARK = f"{AUTHOR}  —  {WEBSITE1}"

# باید عیناً همان کلید استفاده‌شده در encrypt_book.py و در ویوور اندروید باشد
SHARED_KEY_HEX = "8f3a1c9d2e7b4560af13c9e2d4b6f8a01c3e5f7091b3d5f7a9c1e3f5071b3d59"
_PTXB_MAGIC = b"PTXB"


def decrypt_ptxbook(path):
    """رمزگشایی فایل اختصاصی .ptxbook (AES-256-GCM) و بازگرداندن دیکشنری کتاب."""
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:4] != _PTXB_MAGIC:
        raise ValueError("فایل .ptxbook نامعتبر است یا خراب شده.")
    nonce = raw[5:17]
    ciphertext = raw[17:]
    key = bytes.fromhex(SHARED_KEY_HEX)
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode("utf-8"))


def resource_path(filename):
    """Works both when run as a normal script and when bundled by PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


class BookReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME + " — بدون فایل باز")
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(1360, 860)
        self.setAcceptDrops(True)

        self.book_data = {"title": "", "author": "", "chapters": []}
        self.current_id = None
        self.current_file_path = None

        self.setup_ui()
        self.apply_styles()
        self.show_welcome_screen()

        # اگر با دابل‌کلیک روی یک فایل .ptxbook یا از خط فرمان اجرا شده باشد
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            self.open_book_file(sys.argv[1])

    # ------------------------------------------------------------------
    def open_book_file(self, path):
        """باز کردن هر فایل .ptxbook دلخواه — این متد قلب رفتار «ویوور عمومی» است."""
        try:
            self.book_data = decrypt_ptxbook(path)
            self.current_file_path = path
        except Exception as e:
            QMessageBox.critical(self, "خطا در بازکردن فایل",
                                  f"این فایل یک کتاب معتبر Promptexa (.ptxbook) نیست یا خراب شده است.\n\n{e}")
            return

        self.populate_chapter_list()
        self.setWindowTitle(f"{APP_NAME} — {self.book_data.get('title', '')}")
        if self.book_data.get("chapters"):
            self.show_chapter(self.book_data["chapters"][0]["id"])

    def show_welcome_screen(self):
        """صفحه خوش‌آمد وقتی هنوز هیچ فایلی باز نشده — دقیقاً رفتار یک ای‌بوک‌ریدر عمومی."""
        welcome_html = f"""
        <div style="text-align:center; padding-top:60px;">
            <p style="font-size:26px; font-weight:bold; color:#6c5ce7;">📖 {APP_NAME}</p>
            <p style="font-size:15px; color:#888;">نسخه {APP_VERSION} — یک ویوور عمومی برای فایل‌های .ptxbook</p>
            <p style="font-size:15px; margin-top:30px;">
                برای شروع، از دکمه «باز کردن فایل کتاب» بالای صفحه استفاده کنید،<br/>
                یا فایل <b>.ptxbook</b> را مستقیماً به داخل این پنجره بکشید و رها کنید.
            </p>
            <p style="font-size:12px; color:#aaa; margin-top:50px;">
                © {AUTHOR} — {WEBSITE1} — {WEBSITE2}
            </p>
        </div>
        """
        self.content_display.setHtml(welcome_html)
        self.chapter_title.setText("فایلی باز نشده است")
        self.copy_bar_scroll.setVisible(False)

    # ------------------------------------------------------------------
    def browse_and_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "باز کردن فایل کتاب", "", "کتاب Promptexa (*.ptxbook);;همه فایل‌ها (*)"
        )
        if path:
            self.open_book_file(path)

    # ------------------------------------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".ptxbook"):
                self.open_book_file(path)
                return
        QMessageBox.warning(self, "فرمت نامعتبر", "فقط فایل‌های .ptxbook پشتیبانی می‌شوند.")

    # ------------------------------------------------------------------
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # ---------------- Sidebar ----------------
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(340)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar.setLayout(sidebar_layout)

        title_label = QLabel("📖 فهرست مطالب")
        title_label.setObjectName("sidebar_title")
        sidebar_layout.addWidget(title_label)

        self.search_box = QLineEdit()
        self.search_box.setObjectName("search_box")
        self.search_box.setPlaceholderText("جست‌وجو در فهرست...")
        self.search_box.textChanged.connect(self.filter_chapters)
        sidebar_layout.addWidget(self.search_box)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #6c5ce7; height: 2px; border: none;")
        sidebar_layout.addWidget(line)

        self.chapter_list = QListWidget()
        self.chapter_list.setObjectName("chapter_list")
        self.chapter_list.itemClicked.connect(self.on_chapter_clicked)
        sidebar_layout.addWidget(self.chapter_list)

        brand_frame = QFrame()
        brand_frame.setObjectName("brand_frame")
        brand_layout = QVBoxLayout()
        brand_layout.setAlignment(Qt.AlignCenter)
        brand_frame.setLayout(brand_layout)
        for txt, obj in [
            (f"© {AUTHOR}", "brand_info"),
            (f"🌐 {WEBSITE1}", "brand_link"),
            (f"🌐 {WEBSITE2}", "brand_link"),
            (f"نسخه {APP_VERSION}", "version_label"),
        ]:
            lbl = QLabel(txt)
            lbl.setObjectName(obj)
            lbl.setAlignment(Qt.AlignCenter)
            brand_layout.addWidget(lbl)
        sidebar_layout.addWidget(brand_frame)

        # ---------------- Content panel ----------------
        content_panel = QWidget()
        content_panel.setObjectName("content_panel")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_panel.setLayout(content_layout)

        # Header
        header_widget = QWidget()
        header_widget.setObjectName("header")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(25, 15, 25, 15)
        header_widget.setLayout(header_layout)

        self.chapter_title = QLabel("عنوان فصل")
        self.chapter_title.setObjectName("chapter_title")
        self.chapter_title.setWordWrap(True)
        header_layout.addWidget(self.chapter_title)
        header_layout.addStretch()

        self.open_btn = QPushButton("📂 باز کردن فایل کتاب (.ptxbook)")
        self.open_btn.setObjectName("nav_btn")
        self.open_btn.clicked.connect(self.browse_and_open)
        header_layout.addWidget(self.open_btn)

        self.prev_btn = QPushButton("→ فصل قبل")
        self.prev_btn.setObjectName("nav_btn")
        self.prev_btn.clicked.connect(self.go_prev)
        header_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("فصل بعد ←")
        self.next_btn.setObjectName("nav_btn")
        self.next_btn.clicked.connect(self.go_next)
        header_layout.addWidget(self.next_btn)

        content_layout.addWidget(header_widget)

        # Row of copy buttons for this chapter's code/prompt blocks
        self.copy_bar_scroll = QScrollArea()
        self.copy_bar_scroll.setObjectName("copy_bar_scroll")
        self.copy_bar_scroll.setWidgetResizable(True)
        self.copy_bar_scroll.setFixedHeight(52)
        self.copy_bar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.copy_bar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.copy_bar_widget = QWidget()
        self.copy_bar_layout = QHBoxLayout()
        self.copy_bar_layout.setContentsMargins(12, 8, 12, 8)
        self.copy_bar_layout.setSpacing(8)
        self.copy_bar_widget.setLayout(self.copy_bar_layout)
        self.copy_bar_scroll.setWidget(self.copy_bar_widget)
        self.copy_bar_scroll.setObjectName("copy_bar_scroll")
        content_layout.addWidget(self.copy_bar_scroll)

        # Content display
        self.content_display = QTextEdit()
        self.content_display.setObjectName("content_display")
        self.content_display.setReadOnly(True)
        self.content_display.setContextMenuPolicy(Qt.NoContextMenu)
        content_layout.addWidget(self.content_display)

        # Footer
        footer = QLabel(f"© {AUTHOR} — {WEBSITE1} — {WEBSITE2} | تمام حقوق محفوظ است | نسخه {APP_VERSION}")
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(footer)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_panel)
        main_layout.setStretchFactor(sidebar, 0)
        main_layout.setStretchFactor(content_panel, 1)

        self.populate_chapter_list()

    # ------------------------------------------------------------------
    def populate_chapter_list(self):
        self.chapter_list.clear()
        for chapter in self.book_data.get("chapters", []):
            item = QListWidgetItem(chapter["title"])
            item.setData(Qt.UserRole, chapter["id"])
            self.chapter_list.addItem(item)

    def filter_chapters(self, text):
        text = text.strip().lower()
        for i in range(self.chapter_list.count()):
            item = self.chapter_list.item(i)
            item.setHidden(text not in item.text().lower())

    # ------------------------------------------------------------------
    def on_chapter_clicked(self, item):
        self.show_chapter(item.data(Qt.UserRole))

    def go_next(self):
        chapters = self.book_data.get("chapters", [])
        idx = next((i for i, c in enumerate(chapters) if c["id"] == self.current_id), 0)
        if idx + 1 < len(chapters):
            self.show_chapter(chapters[idx + 1]["id"])

    def go_prev(self):
        chapters = self.book_data.get("chapters", [])
        idx = next((i for i, c in enumerate(chapters) if c["id"] == self.current_id), 0)
        if idx - 1 >= 0:
            self.show_chapter(chapters[idx - 1]["id"])

    def show_chapter(self, chapter_id):
        chapter = next((c for c in self.book_data.get("chapters", []) if c["id"] == chapter_id), None)
        if not chapter:
            return
        self.current_id = chapter_id
        self.chapter_title.setText(chapter["title"])

        content = chapter.get("content", "")
        watermark_html = f"""
        <div style="position:relative;">
            <p style="text-align:center;color:#d9d9e8;font-size:34px;font-weight:bold;
                      opacity:0.5;">{WATERMARK}</p>
            {content}
        </div>
        """
        self.content_display.setHtml(watermark_html)
        self.content_display.moveCursor(QTextCursor.Start)

        # rebuild copy-button bar for this chapter's code blocks
        while self.copy_bar_layout.count():
            w = self.copy_bar_layout.takeAt(0).widget()
            if w:
                w.deleteLater()

        code_blocks = chapter.get("code_blocks", [])
        if code_blocks:
            label = QLabel("📋 کپی سریع کد/پرامپت:")
            label.setObjectName("copy_bar_label")
            self.copy_bar_layout.addWidget(label)
            for i, code in enumerate(code_blocks, start=1):
                btn = QPushButton(f"کد {i}")
                btn.setObjectName("copy_btn")
                btn.clicked.connect(lambda _, t=code, b=btn: self.copy_code(t, b))
                self.copy_bar_layout.addWidget(btn)
            self.copy_bar_layout.addStretch()
            self.copy_bar_scroll.setVisible(True)
        else:
            self.copy_bar_scroll.setVisible(False)

        # highlight active item in sidebar
        for i in range(self.chapter_list.count()):
            item = self.chapter_list.item(i)
            item.setSelected(item.data(Qt.UserRole) == chapter_id)

    def copy_code(self, text, btn):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        original = btn.text()
        btn.setText("کپی شد ✓")
        btn.setStyleSheet("background:#2e7d32;")
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1200, lambda: (btn.setText(original), btn.setStyleSheet("")))

    # ------------------------------------------------------------------
    def apply_styles(self):
        try:
            with open(resource_path("style.qss"), "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass

    def keyPressEvent(self, event):
        """جلوگیری از کپی/پرینت متن اصلی؛ کپی فقط از طریق دکمه‌های کد مجاز است."""
        if event.modifiers() == Qt.ControlModifier:
            if event.key() in (Qt.Key_C, Qt.Key_P, Qt.Key_S, Qt.Key_X):
                event.ignore()
                return
        super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    font = QFont("Vazirmatn", 10)
    app.setFont(font)

    window = BookReader()
    window.show()
    sys.exit(app.exec_())
