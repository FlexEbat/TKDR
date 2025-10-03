import flet as ft
import yt_dlp
import threading
import os
import time

translations = {
    'ru': {
        "title": "Загрузчик TikTok",
        "tab_download": "Скачать",
        "tab_settings": "Настройки",
        "url_placeholder": "Вставьте ссылку на видео...",
        "download_button": "Скачать",
        "settings_path_label": "Путь для сохранения:",
        "browse_button": "Выбрать",
        "settings_lang_label": "Язык:",
        "log_download_start": "Начинаю скачивание...",
        "log_download_success": "✅ Видео успешно сохранено!",
        "log_download_error": "❌ Ошибка: {error}",
        "log_url_empty": "Пожалуйста, вставьте ссылку.",
        "log_header": "Лог:"
    },
    'en': {
        "title": "TikTok Downloader",
        "tab_download": "Download",
        "tab_settings": "Settings",
        "url_placeholder": "Paste video link here...",
        "download_button": "Download",
        "settings_path_label": "Save path:",
        "browse_button": "Browse",
        "settings_lang_label": "Language:",
        "log_download_start": "Starting download...",
        "log_download_success": "✅ Video saved successfully!",
        "log_download_error": "❌ Error: {error}",
        "log_url_empty": "Please paste a link.",
        "log_header": "Log:"
    },
    'zh': {
        "title": "TikTok 下载器",
        "tab_download": "下载",
        "tab_settings": "设置",
        "url_placeholder": "在此处粘贴视频链接...",
        "download_button": "下载",
        "settings_path_label": "保存路径:",
        "browse_button": "浏览",
        "settings_lang_label": "语言:",
        "log_download_start": "开始下载...",
        "log_download_success": "✅ 视频保存成功!",
        "log_download_error": "❌ 错误: {error}",
        "log_url_empty": "请输入链接。",
        "log_header": "日志:"
    }
}
lang_map = {"Русский": "ru", "English": "en", "中文": "zh"}


def main(page: ft.Page):
    current_lang = 'zh' 
    
    page.title = translations[current_lang]['title']
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 600
    page.window_height = 550
    page.window_min_width = 500
    page.window_min_height = 500
    page.padding = ft.padding.all(15)

    def log(message: str):
        log_view.controls.append(ft.Text(message))
        page.update()

    def progress_hook(d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                progress = downloaded_bytes / total_bytes
                progress_bar.value = progress
        elif d['status'] == 'finished':
            progress_bar.value = 1
        time.sleep(0.01)
        page.update()
        
    def download_video_thread(url: str, save_path: str):
        try:
            if not os.path.exists(save_path): os.makedirs(save_path)
            ydl_opts = {'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'), 'progress_hooks': [progress_hook], 'nocheckcertificate': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                log(translations[current_lang]["log_download_start"])
                ydl.download([url])
                log(translations[current_lang]["log_download_success"])
                url_entry.value = ""
        except Exception as e:
            log(translations[current_lang]["log_download_error"].format(error=str(e)))
        finally:
            progress_bar.visible = False
            download_button.disabled = False
            page.update()

    def start_download(e):
        video_url, save_path = url_entry.value, save_path_entry.value
        if not video_url:
            log(translations[current_lang]["log_url_empty"]); return
        download_button.disabled = True
        progress_bar.value = 0
        progress_bar.visible = True
        page.update()
        threading.Thread(target=download_video_thread, args=(video_url, save_path), daemon=True).start()
        
    def pick_directory_result(e: ft.FilePickerResultEvent):
        if e.path: save_path_entry.value = e.path; page.update()

    def switch_language(e):
        nonlocal current_lang
        current_lang = lang_map[e.control.value]
        lang_dict = translations[current_lang]
        page.title = lang_dict['title']
        tab_download.text, tab_settings.text = lang_dict['tab_download'], lang_dict['tab_settings']
        url_entry.hint_text = lang_dict['url_placeholder']
        download_button.text, browse_button.text = lang_dict['download_button'], lang_dict['browse_button']
        settings_path_label.value, settings_lang_label.value = lang_dict['settings_path_label'], lang_dict['settings_lang_label']
        log_header.value = lang_dict['log_header']
        page.update()
        
    primary_button_style = ft.ButtonStyle(
        bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE,
        shape=ft.RoundedRectangleBorder(radius=8), padding=15
    )
    textfield_style = {
        "border_radius": 8, "expand": True, "bgcolor": ft.Colors.WHITE10,
        "border_color": "transparent", "focused_border_color": ft.Colors.BLUE_400
    }

    dir_picker = ft.FilePicker(on_result=pick_directory_result); page.overlay.append(dir_picker)

    url_entry = ft.TextField(hint_text=translations[current_lang]['url_placeholder'], **textfield_style)
    download_button = ft.ElevatedButton(text=translations[current_lang]['download_button'], on_click=start_download, icon=ft.Icons.DOWNLOAD, style=primary_button_style)
    progress_bar = ft.ProgressBar(value=0, visible=False, border_radius=10)
    log_header = ft.Text(translations[current_lang]['log_header'], weight=ft.FontWeight.BOLD)
    log_view = ft.ListView(spacing=5, auto_scroll=True, expand=True)
    log_container = ft.Container(
        content=ft.Column(controls=[log_header, log_view], spacing=10),
        border=ft.border.all(1, ft.Colors.WHITE10), border_radius=8, padding=15, expand=True
    )
    download_view = ft.Column(controls=[
        ft.Row(controls=[url_entry, download_button]),
        progress_bar, ft.Divider(height=10, color="transparent"), log_container
    ], spacing=10, expand=True)
    
    settings_path_label = ft.Text(translations[current_lang]['settings_path_label'])
    save_path_entry = ft.TextField(value="downloads", read_only=True, **textfield_style)
    browse_button = ft.ElevatedButton(text=translations[current_lang]['browse_button'], icon=ft.Icons.FOLDER_OPEN, on_click=lambda _: dir_picker.get_directory_path(), style=primary_button_style)
    settings_lang_label = ft.Text(translations[current_lang]['settings_lang_label'])
    
    initial_lang_key = next(key for key, value in lang_map.items() if value == current_lang)
    
    lang_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(lang) for lang in lang_map.keys()],
        value=initial_lang_key,  # Используем найденный ключ
        on_change=switch_language, border_radius=8,
    )

    settings_view = ft.Column(controls=[
        settings_path_label, ft.Row(controls=[save_path_entry, browse_button]),
        ft.Divider(), settings_lang_label, lang_dropdown
    ], spacing=15)
    
    tab_download = ft.Tab(text=translations[current_lang]['tab_download'], icon=ft.Icons.VIDEO_LIBRARY, content=ft.Container(download_view, padding=ft.padding.only(top=10)))
    tab_settings = ft.Tab(text=translations[current_lang]['tab_settings'], icon=ft.Icons.SETTINGS, content=ft.Container(settings_view, padding=ft.padding.only(top=10)))
    tabs = ft.Tabs(selected_index=0, animation_duration=300, tabs=[tab_download, tab_settings], expand=True)
    page.add(tabs)

if __name__ == "__main__":
    ft.app(target=main)