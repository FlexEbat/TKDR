import customtkinter
from tkinter import filedialog
import yt_dlp
import threading
import os

# Настройки внешнего вида
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- СИСТЕМА ЛОКАЛИЗАЦИИ ---
        self.translations = {
            'ru': {
                "title": "Tiktok Downloader",
                "tab_download": "Скачать видео",
                "tab_settings": "Настройки",
                "url_placeholder": "Вставьте ссылку на видео TikTok",
                "download_button": "Скачать",
                "settings_path_label": "Путь для сохранения видео:",
                "browse_button": "Выбрать...",
                "settings_lang_label": "Язык интерфейса:",
                "log_download_start": "Начинаю скачивание: {url}",
                "log_download_success": "✅ Скачивание успешно завершено!",
                "log_download_error": "❌ Ошибка при скачивании: {error}",
                "log_url_empty": "Пожалуйста, вставьте ссылку на видео."
            },
            'en': {
                "title": "TikTok Downloader",
                "tab_download": "Download Video",
                "tab_settings": "Settings",
                "url_placeholder": "Paste TikTok video link here",
                "download_button": "Download",
                "settings_path_label": "Path to save videos:",
                "browse_button": "Browse...",
                "settings_lang_label": "Interface Language:",
                "log_download_start": "Starting download: {url}",
                "log_download_success": "✅ Download completed successfully!",
                "log_download_error": "❌ Error during download: {error}",
                "log_url_empty": "Please paste a video link."
            },
            'zh': {
                "title": "TikTok 下载器",
                "tab_download": "下载视频",
                "tab_settings": "设置",
                "url_placeholder": "在此处粘贴 TikTok 视频链接",
                "download_button": "下载",
                "settings_path_label": "视频保存路径:",
                "browse_button": "浏览...",
                "settings_lang_label": "界面语言:",
                "log_download_start": "开始下载: {url}",
                "log_download_success": "✅ 下载成功完成!",
                "log_download_error": "❌ 下载时出错: {error}",
                "log_url_empty": "请输入视频链接。"
            }
        }
        self.lang_map = {"Русский": "ru", "English": "en", "中文": "zh"}
        self.current_lang = "ru" # Язык по умолчанию

        # --- Конфигурация окна ---
        self.geometry("700x450")
        self.minsize(600, 400)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Создание вкладок ---
        self.tab_view = customtkinter.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.download_tab = self.tab_view.add(self.translations[self.current_lang]["tab_download"])
        self.settings_tab = self.tab_view.add(self.translations[self.current_lang]["tab_settings"])

        # =====================================================================
        # --- ВКЛАДКА "СКАЧАТЬ ВИДЕО" ---
        # =====================================================================
        self.download_tab.grid_columnconfigure(0, weight=1)
        self.download_tab.grid_rowconfigure(2, weight=1)

        self.input_frame = customtkinter.CTkFrame(self.download_tab)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = customtkinter.CTkEntry(self.input_frame)
        self.url_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.download_button = customtkinter.CTkButton(self.input_frame, command=self.start_download)
        self.download_button.grid(row=0, column=1, padx=10, pady=10)

        self.progress_bar = customtkinter.CTkProgressBar(self.download_tab)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.output_textbox = customtkinter.CTkTextbox(self.download_tab, state="disabled")
        self.output_textbox.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # =====================================================================
        # --- ВКЛАДКА "НАСТРОЙКИ" ---
        # =====================================================================
        self.settings_tab.grid_columnconfigure(0, weight=1)

        self.path_frame = customtkinter.CTkFrame(self.settings_tab)
        self.path_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.path_frame.grid_columnconfigure(0, weight=1)

        self.save_path_label = customtkinter.CTkLabel(self.path_frame)
        self.save_path_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w")

        self.save_path_entry = customtkinter.CTkEntry(self.path_frame)
        self.save_path_entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.save_path_entry.insert(0, "downloads")

        self.browse_button = customtkinter.CTkButton(self.path_frame, command=self.browse_directory, width=120)
        self.browse_button.grid(row=1, column=1, padx=(0, 10), pady=10)
        
        self.lang_frame = customtkinter.CTkFrame(self.settings_tab)
        self.lang_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.lang_label = customtkinter.CTkLabel(self.lang_frame)
        self.lang_label.pack(side="left", padx=10, pady=10)
        
        self.lang_menu = customtkinter.CTkOptionMenu(self.lang_frame, values=list(self.lang_map.keys()), command=self.switch_language)
        self.lang_menu.pack(side="left", padx=(0, 10), pady=10)
        
        # --- ПЕРВИЧНОЕ ОБНОВЛЕНИЕ ИНТЕРФЕЙСА ---
        self.update_ui_language()

    def update_ui_language(self):
        """Обновляет весь текст в GUI в соответствии с выбранным языком."""
        lang_dict = self.translations[self.current_lang]
        self.title(lang_dict["title"])
        # Примечание: название вкладок нельзя легко изменить после создания,
        # поэтому мы их создаем сразу с правильным названием.
        # Для изменения пришлось бы пересоздавать TabView.
        self.url_entry.configure(placeholder_text=lang_dict["url_placeholder"])
        self.download_button.configure(text=lang_dict["download_button"])
        self.save_path_label.configure(text=lang_dict["settings_path_label"])
        self.browse_button.configure(text=lang_dict["browse_button"])
        self.lang_label.configure(text=lang_dict["settings_lang_label"])

    def switch_language(self, choice):
        """Вызывается при смене языка в меню."""
        self.current_lang = self.lang_map[choice]
        self.update_ui_language()

    def log(self, message):
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert("end", message + "\n")
        self.output_textbox.see("end")
        self.output_textbox.configure(state="disabled")

    def browse_directory(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.save_path_entry.delete(0, "end")
            self.save_path_entry.insert(0, folder_selected)

    def download_video_thread(self, url):
        try:
            save_path = self.save_path_entry.get()
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            # --- ИСПРАВЛЕННЫЕ ОПЦИИ YDL ---
            ydl_opts = {
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'nocheckcertificate': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.log(self.translations[self.current_lang]["log_download_start"].format(url=url))
                ydl.download([url])
                self.log(self.translations[self.current_lang]["log_download_success"])
                self.url_entry.delete(0, "end")
        except Exception as e:
            self.log(self.translations[self.current_lang]["log_download_error"].format(error=e))
        finally:
            self.progress_bar.set(0)
            self.download_button.configure(state="normal")

    def start_download(self):
        url = self.url_entry.get()
        if url:
            self.download_button.configure(state="disabled")
            self.progress_bar.set(0)
            
            download_thread = threading.Thread(target=self.download_video_thread, args=(url,), daemon=True)
            download_thread.start()
        else:
            self.log(self.translations[self.current_lang]["log_url_empty"])

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes')
            if total_bytes and downloaded_bytes:
                progress = downloaded_bytes / total_bytes
                self.progress_bar.set(progress)
        if d['status'] == 'finished':
            self.progress_bar.set(1)

if __name__ == "__main__":
    app = App()
    app.mainloop()