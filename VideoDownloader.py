import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Canvas
import yt_dlp
import os
import pyktok as pyk


class VideoDownloader:
    def __init__(self, root):
        self.root = root
        root.title("Downloader Video Pro")
        root.geometry("650x450")
        root.resizable(False, False)

        self.yt_format = tk.StringVar(value='video')
        self.audio_codec = tk.StringVar(value='mp3')
        self.audio_quality = tk.StringVar(value='320')

        self.yt_format.trace_add('write', self.alternar_audio_opts)

        self.configure_styles()
        self.download_dir = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(self.download_dir, exist_ok=True)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)

        self.create_youtube_tab()
        self.create_tiktok_tab()
        self.create_settings_tab()
        self.create_info_tab()

    def create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        canvas.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, start=90, extent=90, **kwargs)
        canvas.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, start=0, extent=90, **kwargs)
        canvas.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, start=270, extent=90, **kwargs)
        canvas.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, start=180, extent=90, **kwargs)
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
        canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)

    def rounded_button(self, parent, text, command, radius=25, **kwargs):
        bg = kwargs.get('bg', '#3498db')
        fg = kwargs.get('fg', 'white')
        font = kwargs.get('font', ('Arial', 12, 'bold'))
        hover_bg = kwargs.get('hover_bg', '#2980b9')
        width = kwargs.get('width', 200)
        height = 40

        btn_canvas = Canvas(parent, width=width, height=height,
                            highlightthickness=0, bg='#f0f0f0')

        self.create_rounded_rectangle(btn_canvas, -2, 0, width, height,
                                      radius=radius, fill=bg,outline=bg)

        text_id = btn_canvas.create_text(width // 2, height//2,
                                         text=text,fill=fg, font=font)

        def on_enter(e):
            btn_canvas.itemconfig(1, fill=hover_bg)
            btn_canvas.config(cursor="hand2")

        def on_leave(e):
            btn_canvas.itemconfig(1, fill=bg)
            btn_canvas.config(cursor="")

        btn_canvas.bind('<Enter>', lambda e: btn_canvas.config(cursor='hand2'))
        btn_canvas.bind('<Leave>', on_leave)
        btn_canvas.bind('<Button-1>', lambda e: command())

        return btn_canvas

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TEntry', padding=5, font=('Arial', 10))
        style.configure('TRadiobutton', background='#f0f0f0', font=('Arial', 10))
        style.configure('TCombobox', padding=5)

    def create_youtube_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='YouTube')

        content_frame = ttk.Frame(tab, padding=20)
        content_frame.pack(fill='both', expand=True)

        ttk.Label(content_frame, text="Formato de descarga:").pack(anchor='w',pady=5)
        format_frame = ttk.Frame(content_frame)
        format_frame.pack(anchor='w',pady=10)

        ttk.Radiobutton(format_frame, text="Video + Audio",
                        variable=self.yt_format, value='video').pack(side='left', padx=15)
        ttk.Radiobutton(format_frame, text="Solo Audio",
                        variable=self.yt_format, value='audio').pack(side='left', padx=15)

        self.audio_options_frame = ttk.Frame(content_frame)

        ttk.Label(self.audio_options_frame, text="Formato:").pack(side='left', padx=5)
        codec_combo = ttk.Combobox(self.audio_options_frame,
                                   textvariable=self.audio_codec,
                                   values=['mp3', 'aac', 'wav', 'opus', 'm4a'],
                                   state='readonly',
                                   width=8)
        codec_combo.pack(side='left', padx=5)

        ttk.Label(self.audio_options_frame, text="Calidad:").pack(side='left', padx=5)
        quality_combo = ttk.Combobox(self.audio_options_frame,
                                     textvariable=self.audio_quality,
                                     values=['128', '192', '256','320'],
                                     state='readonly',
                                     width=5)
        quality_combo.pack(side='left', padx=5)

        self.url_label = ttk.Label(content_frame, text="URL del video:")
        self.url_label.pack(pady=(20, 5))

        self.yt_url = ttk.Entry(content_frame, width=60)
        self.yt_url.pack(pady=5)

        self.rounded_button(content_frame, "Descargar de YouTube",
                            self.download_youtube,
                            bg='#3498db', hover_bg='#2980b9',
                            width=200).pack(pady=20)
        self.alternar_audio_opts()

    def create_tiktok_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='TikTok')

        content_frame = ttk.Frame(tab)
        content_frame.pack(pady=20, padx=20, fill='both', expand=True)

        ttk.Label(content_frame, text="URL del video:").pack(pady=10)
        self.tt_url = ttk.Entry(content_frame, width=50)
        self.tt_url.pack(pady=5)

        self.rounded_button(content_frame, "Descargar de TikTok",
                            self.download_tiktok,
                            bg='#e74c3c', hover_bg='#c0392b',
                            width=200).pack(pady=20)

    def create_settings_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Configuración')

        content_frame = ttk.Frame(tab)
        content_frame.pack(pady=20, padx=20, fill='both', expand=True)

        ttk.Label(content_frame, text="Carpeta de descargas:").pack(pady=10)

        path_frame = ttk.Frame(content_frame)
        path_frame.pack(fill='x', pady=5)

        self.path_entry = ttk.Entry(path_frame)
        self.path_entry.insert(0, self.download_dir)
        self.path_entry.pack(side='left', fill='x', expand=True, padx=5)

        self.rounded_button(path_frame, "Cambiar",
                            self.select_directory,
                            bg='#95a5a6', hover_bg='#7f8c8d',
                            width=100).pack(side='left')

    def create_info_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Información')

        info_text = (
            "Downloader Video Pro v2.3\n\n"
            "Desarrollado por Carlos Gandara\n\n"
            "Características principales:\n"
            "✔ Descarga videos de YouTube en HD\n"
            "✔ Extrae audio en calidad MP3\n"
            "✔ Descarga videos de TikTok\n"
            "✔ Interfaz moderna y fácil de usar\n"
            "✔ Configuración personalizable\n"
            "✔ Mas formatos de audio y calidad"
        )

        ttk.Label(tab, text=info_text, justify='left',
                  font=('Arial', 10), wraplength=400).pack(pady=30, padx=20)

    def download_youtube(self):
        url = self.yt_url.get()
        if not url:
            messagebox.showerror("Error", "Por favor ingresa una URL válida de YouTube")
            return

        try:
            opts = {
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook]
            }

            if self.yt_format.get() == 'video':
                opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
                opts['merge_output_format'] = 'mp4'
            else:
                opts['format'] = 'bestaudio/best'
                opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.audio_codec.get(),
                    'preferredquality': self.audio_quality.get(),
                }]
                if self.audio_codec.get() == 'opus':
                    opts['postprocessors'][0]['preferredquality'] = '192'
                elif self.audio_codec.get() == 'wav':
                    opts['postprocessors'][0]['preferredquality'] = '0'

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            messagebox.showinfo("Éxito", "Descarga de YouTube completada correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error en YouTube: {str(e)}")

    def download_tiktok(self):
        url = self.tt_url.get()
        if not url:
            messagebox.showerror("Error", "Por favor ingresa una URL válida de TikTok")
            return

        try:
            pyk.specify_browser('edge')
            pyk.save_tiktok(
                url,
                True
            )
            messagebox.showinfo("Éxito", "Video de TikTok descargado con éxito")

        except Exception as e:
            messagebox.showerror("Error", f"Error en TikTok: {str(e)}")

    def select_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.download_dir = path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            os.makedirs(path, exist_ok=True)
            messagebox.showinfo("Info", f"Directorio actualizado:\n{path}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            print(f"Progreso: {d.get('_percent_str', 'N/A')}")

    def alternar_audio_opts(self, *args):
        if self.yt_format.get() == 'audio':
            self.audio_options_frame.pack(anchor='w', pady=10, before=self.url_label)
        else:
            self.audio_options_frame.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloader(root)
    root.mainloop()
