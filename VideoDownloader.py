from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
import yt_dlp
import os
import threading
from pathlib import Path

Window.size = (400, 600)

class MainScreen(TabbedPanel):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.download_dir = str(Path.home() / "Downloads")
        self.stop_download_flag = False
        self.current_title = ""
        
        self.create_youtube_tab()
        self.create_tiktok_tab()
        self.create_twitter_tab()
        self.create_config_tab()
        self.create_info_tab()

    def create_youtube_tab(self):
        tab = TabbedPanelItem(text='YouTube')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Widgets de YouTube
        self.yt_url = TextInput(hint_text='URL de YouTube', size_hint=(1, None), height=40)
        self.yt_progress = ProgressBar(max=100, size_hint=(1, None), height=20)
        self.yt_status = Label(text='Listo', size_hint=(1, None), height=30)
        
        # Botones de acción
        btn_layout = BoxLayout(size_hint=(1, None), height=40)
        self.yt_download_btn = Button(text='Descargar', on_press=self.start_youtube_download)
        self.yt_stop_btn = Button(text='Detener', disabled=True)
        
        layout.add_widget(Label(text='Descargador de YouTube', bold=True))
        layout.add_widget(self.yt_url)
        layout.add_widget(self.yt_progress)
        layout.add_widget(self.yt_status)
        layout.add_widget(btn_layout)
        
        tab.add_widget(layout)
        self.add_widget(tab)

    def create_tiktok_tab(self):
        tab = TabbedPanelItem(text='TikTok')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Widgets de TikTok
        self.tt_url = TextInput(hint_text='URL de TikTok', size_hint=(1, None), height=40)
        self.tt_progress = ProgressBar(max=100, size_hint=(1, None), height=20)
        self.tt_status = Label(text='Listo', size_hint=(1, None), height=30)
        self.tt_download_btn = Button(text='Descargar', on_press=self.start_tiktok_download)
        
        layout.add_widget(Label(text='Descargador de TikTok', bold=True))
        layout.add_widget(self.tt_url)
        layout.add_widget(self.tt_progress)
        layout.add_widget(self.tt_status)
        layout.add_widget(self.tt_download_btn)
        
        tab.add_widget(layout)
        self.add_widget(tab)
    
    def create_twitter_tab(self):
        tab = TabbedPanelItem(text='Twitter/X')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Widgets de Twitter
        self.tw_url = TextInput(hint_text='URL de Twitter/X', size_hint=(1, None), height=40)
        self.tw_progress = ProgressBar(max=100, size_hint=(1, None), height=20)
        self.tw_status = Label(text='Listo', size_hint=(1, None), height=30)
        self.tw_download_btn = Button(text='Descargar', on_press=self.start_twitter_download)
        
        layout.add_widget(Label(text='Descargador de Twitter/X', bold=True))
        layout.add_widget(self.tw_url)
        layout.add_widget(self.tw_progress)
        layout.add_widget(self.tw_status)
        layout.add_widget(self.tw_download_btn)
        
        tab.add_widget(layout)
        self.add_widget(tab)

    def create_config_tab(self):
        tab = TabbedPanelItem(text='Configuración')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Configuración de descargas'))
        tab.add_widget(layout)
        self.add_widget(tab)
        
    def create_info_tab(self):
        tab = TabbedPanelItem(text='Información')
        layout = BoxLayout(orientation='vertical', padding=10)
        info_text = """Multi-Downloader v3.5
            Desarrollado por Carlos Gan"""
        layout.add_widget(Label(text=info_text))
        tab.add_widget(layout)
        self.add_widget(tab)

    def update_progress(self, progress, status, platform):
        if platform == 'youtube':
            Clock.schedule_once(lambda dt: setattr(self.yt_progress, 'value', progress))
            Clock.schedule_once(lambda dt: setattr(self.yt_status, 'text', status))
        elif platform == 'tiktok':
            Clock.schedule_once(lambda dt: setattr(self.tt_progress, 'value', progress))
            Clock.schedule_once(lambda dt: setattr(self.tt_status, 'text', status))
        elif platform == 'twitter':
            Clock.schedule_once(lambda dt: setattr(self.tw_progress, 'value', progress))
            Clock.schedule_once(lambda dt: setattr(self.tw_status, 'text', status))

    def youtube_progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            try:
                progress = float(percent.strip('%'))
            except:
                progress = 0
            self.update_progress(progress, f"Descargando: {self.current_title} - {percent}", 'youtube')
        elif d['status'] == 'finished':
            self.update_progress(100, "Procesando video...", 'youtube')

    def start_youtube_download(self, instance):
        url = self.yt_url.text
        if not url:
            self.show_popup('Error', 'Ingresa una URL válida')
            return
        
        self.yt_download_btn.disabled = True
        self.yt_stop_btn.disabled = False
        threading.Thread(target=self.youtube_download_thread, args=(url,), daemon=True).start()

    def youtube_download_thread(self, url):
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl_info:
                info = ydl_info.extract_info(url, download=False)
                self.current_title = info.get('title', 'Video sin título')

            ydl_opts = {
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self.youtube_progress_hook],
                'noplaylist': True,
                'restrictfilenames': True,
                'merge_output_format': 'mp4'
            }
            
            if self.yt_format.state == 'down':
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
            else:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.audio_spinner.text,
                    'preferredquality': '320'
                }]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            self.show_popup('Éxito', 'Descarga de YouTube completada')
            
        except Exception as e:
            self.show_popup('Error', f"Error YouTube: {str(e)}")
        finally:
            Clock.schedule_once(lambda dt: setattr(self.yt_download_btn, 'disabled', False))
            Clock.schedule_once(lambda dt: setattr(self.yt_stop_btn, 'disabled', True))

    def start_tiktok_download(self, instance):
        url = self.tt_url.text
        if not url:
            self.show_popup('Error', 'Ingresa una URL válida de TikTok')
            return
        
        self.tt_download_btn.disabled = True
        threading.Thread(target=self.tiktok_download_thread, args=(url,), daemon=True).start()

    def tiktok_progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            try:
                progress = float(percent.strip('%'))
            except:
                progress = 0
            self.update_progress(progress, f"Descargando TikTok - {percent}", 'tiktok')

    def tiktok_download_thread(self, url):
        try:
            opts = {
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self.tiktok_progress_hook],
                'restrictfilenames': True,
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4'
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
                
            self.show_popup('Éxito', 'Descarga de TikTok completada')
            
        except Exception as e:
            self.show_popup('Error', f"Error TikTok: {str(e)}")
        finally:
            Clock.schedule_once(lambda dt: setattr(self.tt_download_btn, 'disabled', False))

    def start_twitter_download(self, instance):
        url = self.tw_url.text
        if not url:
            self.show_popup('Error', 'Ingresa una URL válida de Twitter/X')
            return
        
        self.tw_download_btn.disabled = True
        threading.Thread(target=self.twitter_download_thread, args=(url,), daemon=True).start()

    def twitter_download_thread(self, url):
        try:
            opts = {
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'restrictfilenames': True,
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4'
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
                
            self.show_popup('Éxito', 'Descarga de Twitter/X completada')
            
        except Exception as e:
            self.show_popup('Error', f"Error Twitter/X: {str(e)}")
        finally:
            Clock.schedule_once(lambda dt: setattr(self.tw_download_btn, 'disabled', False))

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        close_btn = Button(text='Cerrar', size_hint=(1, None), height=40)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

class DownloaderApp(App):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    DownloaderApp().run()
