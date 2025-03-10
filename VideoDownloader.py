import tkinter
from tkinter import messagebox
import customtkinter
import yt_dlp
from customtkinter import *
import os
import threading
from pathlib import Path
import pyktok as pyk

app = CTk()
app.title("Multi-Downloader")
app.geometry('600x600')

set_default_color_theme('green')

# Variables globales
download_dir = str(Path.home() / "Downloads")
stop_download_flag = False
current_title = ""

tabview = CTkTabview(master=app)
tabview.pack(fill='both', expand=1)

tabview.add("Youtube Downloader")
tabview.add("TikTok Downloader")
tabview.add("X Downloader")
tabview.add('Configuración')
tabview.add('Información')

# Frame principal para Youtube
main_frame = customtkinter.CTkFrame(master=tabview.tab('Youtube Downloader'), fg_color="transparent")
main_frame.pack(expand=True, fill="both", padx=20, pady=20)

label_Youtube = CTkLabel(master=main_frame, text="Youtube Video and Audio Downloader", font=("Arial", 16, "bold"))
label_Youtube.pack(padx=5, pady=15, anchor="center")

# Elementos de la interfaz
entry = customtkinter.CTkEntry(master=main_frame,
                               placeholder_text="Ingrese el URL del video a descargar",
                               width=400)
entry.pack(padx=5, pady=15, anchor="center")

# Radio buttons
frame_btn = customtkinter.CTkFrame(master=main_frame, fg_color="transparent")
radio_var = tkinter.IntVar(value=0)

Radiobtn1 = customtkinter.CTkRadioButton(master=frame_btn, text='Video + Audio',
                                         command=lambda: radiobtn_event(),
                                         variable=radio_var, value=1)
Radiobtn2 = customtkinter.CTkRadioButton(master=frame_btn, text='Audio',
                                         command=lambda: radiobtn_event(),
                                         variable=radio_var, value=2)
Radiobtn1.pack(side='left', padx=10)
Radiobtn2.pack(side='left', padx=10)
frame_btn.pack(pady=10, anchor="center")

# ComboBox formato audio
ComboBoxFormato = customtkinter.CTkComboBox(master=main_frame,
                                            values=['mp3', 'aac', 'wav', 'opus', 'm4a'],
                                            width=200,
                                            command=lambda choice: combobox_eventFormat(choice))
ComboBoxFormato.pack(pady=10)
ComboBoxFormato.configure(state='disabled')

# Botones de acción
button_frame = customtkinter.CTkFrame(master=main_frame, fg_color="transparent")
button_frame.pack(pady=15, anchor="center")

btn_DescargarYt = customtkinter.CTkButton(button_frame, text="Descargar",
                                          corner_radius=20,
                                          width=200)
btn_Detener = customtkinter.CTkButton(button_frame, text="Detener",
                                      corner_radius=20,
                                      width=100,
                                      state='disabled')


btn_DescargarYt.pack(side='left', padx=5)
btn_Detener.pack(side='left', padx=5)

# Barra de progreso y estado
progress_bar = CTkProgressBar(master=main_frame, width=400)
progress_bar.set(0)
status_label = CTkLabel(master=main_frame, text="", font=("Arial", 12))

progress_bar.pack(pady=5)
status_label.pack()


def select_directory():
    global download_dir
    if not os.path.isdir(download_dir):
        download_dir = str(Path.home())  # Usar el home directamente
        print(f"Advertencia: Carpeta Downloads no encontrada, usando {download_dir}")
    new_dir = filedialog.askdirectory(initialdir=download_dir)
    if new_dir:
        download_dir = new_dir
        messagebox.showinfo("Directorio seleccionado",
                            f"Descargas se guardarán en:\n{download_dir}")

def progress_hook_wrapper():
    def hook(d):
        global current_title
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            try:
                progress = float(percent.strip('%')) / 100
            except:
                progress = 0

            app.after(0, lambda: progress_bar.set(progress))
            app.after(0, lambda: status_label.configure(
                text=f"Descargando: {current_title} - {percent}"
            ))

        elif d['status'] == 'finished':
            app.after(0, lambda: status_label.configure(
                text=f"Procesando: {current_title}"
            ))

    return hook

def descargar_youtube():
    global stop_download_flag, current_title
    stop_download_flag = False
    url = entry.get()

    if not url.startswith(('https://www.youtube.com', 'https://youtu.be')):
        app.after(0, lambda: messagebox.showerror("Error", "URL de YouTube inválida"))
        return

    if not download_dir:
        app.after(0, lambda: messagebox.showerror("Error", "Selecciona un directorio de descarga primero"))
        return

    try:
        # Obtener información del video
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl_info:
            info = ydl_info.extract_info(url, download=False)
            current_title = info.get('title', 'Video sin título')

        app.after(0, lambda: status_label.configure(
            text=f"Iniciando descarga: {current_title}"
        ))

        opts = {
            'outtmpl': os.path.join(download_dir, f'{current_title}.%(ext)s'),
            'progress_hooks': [progress_hook_wrapper()],
            'noplaylist': True,
            'restrictfilenames': True,
            'merge_output_format': 'mp4'
        }

        if radio_var.get() == 1:  # Video + Audio
            opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        else:  # Solo Audio
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': ComboBoxFormato.get(),
                'preferredquality': '320' if ComboBoxFormato.get() != 'wav' else '0',
            }]

        # Descarga real
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        app.after(0, lambda: status_label.configure(
            text=f"Descarga completada: {current_title}"
        ))
        app.after(0, lambda: progress_bar.set(0))

    except Exception as e:
        app.after(0, lambda: messagebox.showerror("Error", f"Error: {str(e)}"))
    finally:
        app.after(0, lambda: btn_DescargarYt.configure(state='normal'))
        app.after(0, lambda: btn_Detener.configure(state='disabled'))

def start_download_thread():
    btn_DescargarYt.configure(state='disabled')
    btn_Detener.configure(state='normal')
    threading.Thread(target=descargar_youtube, daemon=True).start()

def stop_download():
    global stop_download_flag
    stop_download_flag = True
    messagebox.showinfo("Detener", "La descarga se cancelará al finalizar el fragmento actual")
    btn_Detener.configure(state='disabled')

def radiobtn_event():
    if radio_var.get() == 2:
        ComboBoxFormato.configure(state='normal')
    else:
        ComboBoxFormato.configure(state='disabled')

def combobox_eventFormat(choice):
    print(f"Formato de audio seleccionado: {choice}")

# Comandos de los botones
btn_DescargarYt.configure(command=start_download_thread)
btn_Detener.configure(command=stop_download)

#<-- Metodos de TikTok -->

def download_tiktok():
    try:
        download_path = os.path.normpath(download_dir)

        os.makedirs(download_path, exist_ok=True)
        if not os.access(download_path, os.W_OK):
            raise PermissionError(f'No hay permisos de escritura en: {download_path}')
        url = entry_TikTok.get().strip()
        if not url.startswith(('https://www.tiktok.com', 'https://tiktok.com')):
            messagebox.showerror("Error", "URL de TikTok inválida")
            return

        opts = {
             'outtmpl': os.path.join(download_path, '%(uploader)s..%(track)s.%(title)s.%(id)s.%(ext)s'),
            'restrictfilenames': True,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4'
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = info['uploader']

            messagebox.showinfo("Exito", f"Video descargado en:\n{filename}")
    except Exception as e:
        messagebox.showerror("Error de Permisos", f"Ejecuta como Administrador o cambia permisos:\n{e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al descargar: {str(e)}")


#<-- TikTok -->
tiktok_frame = customtkinter.CTkFrame(master=tabview.tab('TikTok Downloader'), fg_color="transparent")
tiktok_frame.pack(expand=True, fill="both", padx=20, pady=20)
label_TikTok = CTkLabel(master=tiktok_frame, text="TikTok Video Downloader", font=("Arial", 16, "bold"))
label_TikTok.pack(padx=5, pady=15, anchor="center")

entry_TikTok = customtkinter.CTkEntry(master=tiktok_frame,placeholder_text='Ingrese el URL del video a descargar',
                                      width=400)
entry_TikTok.pack(padx=5, pady=15, anchor="center")
btn_DescargarTikTok = customtkinter.CTkButton(master=tiktok_frame, text="Descargar",
                                              corner_radius=20,
                                              width=200)
btn_DescargarTikTok.pack(padx=5, pady=15)
btn_DescargarTikTok.configure(command=download_tiktok)

#<-- Twitter -->
# <- Metodos ->
def download_twitter():

    download_path = os.path.normpath(download_dir)
    os.makedirs(download_path, exist_ok=True)

    if not os.access(download_path, os.W_OK):
        raise PermissionError(f'No hay permisos de escritura en: {download_path}')

    url = entry_Twitter.get()
    if not url.startswith(('https://www.x.com', 'https://x.com')):
        messagebox.showerror("Error", "URL de TikTok inválida")
        return
    if not url:
        messagebox.showerror("Error", 'Porfavor ingrese una URL valida de Twitter(X)')
        return
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'outtmpl': os.path.join(download_path,'%(title)s.%(uploader)s.%(ext)s'),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        messagebox.showinfo("Éxito", "Descarga completada correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"Error en Twitter: {str(e)}")


# Twitter/X
twitter_frame = customtkinter.CTkFrame(master=tabview.tab('X Downloader'), fg_color="transparent")
twitter_frame.pack(expand=True, fill="both", padx=20, pady=20)
label_Twitter = CTkLabel(master=twitter_frame, text="Twitter Video Downloader", font=("Arial", 16, "bold"))
label_Twitter.pack(padx=5, pady=15, anchor="center")

entry_Twitter = customtkinter.CTkEntry(master=twitter_frame,placeholder_text='Ingrese el URL del video a descargar',
                                       width=400)
entry_Twitter.pack(padx=5, pady=15, anchor="center")

btn_DescargarTwitter = customtkinter.CTkButton(master=twitter_frame, text="Descargar",
                                               corner_radius=20,
                                               width=200)
btn_DescargarTwitter.pack(padx=5, pady=15)
btn_DescargarTwitter.configure(command=download_twitter)

# Configuración
config_frame = customtkinter.CTkFrame(master=tabview.tab('Configuración'), fg_color="transparent")
config_frame.pack(expand=True, fill="both", padx=20, pady=20)
label_Config = CTkLabel(master=config_frame, text="Configuración", font=("Arial", 16, "bold"))
label_Config.pack(padx=5, pady=15, anchor="center")

# Botón para seleccionar directorio de descarga
btn_select_dir = customtkinter.CTkButton(master=config_frame, text="Seleccionar directorio de descarga",
                                         corner_radius=10,
                                         command=select_directory,
                                         width=250)
btn_select_dir.pack(padx=5, pady=15, anchor="center")
# Información
info_frame = customtkinter.CTkFrame(master=tabview.tab('Información'), fg_color="transparent")
info_frame.pack(expand=True, fill="both", padx=20, pady=20)
label_Info = CTkLabel(master=info_frame, text="Información", font=("Arial", 16, "bold"))
label_Info.pack(padx=5, pady=15, anchor="center")

info_text = """
Multi-Downloader v3.6
Desarrollado para descargar contenido multimedia de distintas plataformas.
Desarrolado por Carlos Gan

Plataformas soportadas:
- YouTube (videos y audio)
- TikTok (videos)
- Twitter/X (videos)

Características principales:
✔ Descarga videos de YouTube en HD
✔ Extrae audio en calidad MP3
✔ Descarga videos de TikTok
✔ Interfaz moderna y fácil de usar
✔ Configuración personalizable
✔ Mas formatos de audio y calidad

© 2025 - Todos los derechos reservados
"""
info_label = CTkLabel(master=info_frame, text=info_text, font=("Arial", 12))
info_label.pack(padx=20, pady=10)

app.mainloop()
