import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
import threading
import re


class WebmToMP4Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("WebM to MP4 Converter")
        self.root.geometry("1000x700")
        
        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.files_data = []
        self.converting = False
        self.log_visible = tk.BooleanVar(value=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame superior para selección de carpetas
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N))
        
        # Carpeta origen
        ttk.Label(top_frame, text="Carpeta origen:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(top_frame, textvariable=self.source_folder, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(top_frame, text="Explorar...", command=self.browse_source).grid(row=0, column=2)
        
        # Carpeta destino
        ttk.Label(top_frame, text="Carpeta destino:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(top_frame, textvariable=self.dest_folder, width=60).grid(row=1, column=1, padx=5)
        ttk.Button(top_frame, text="Explorar...", command=self.browse_dest).grid(row=1, column=2)
        
        # Botón para cargar archivos
        ttk.Button(top_frame, text="Cargar archivos WebM", command=self.load_files).grid(row=2, column=1, pady=10)
        
        # Frame para la tabla de archivos
        table_frame = ttk.Frame(self.root, padding="10")
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar pesos para redimensionamiento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview para mostrar archivos
        columns = ("nombre", "extension", "tamano", "fecha")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="tree headings", selectmode="extended")
        
        self.tree.heading("#0", text="✓")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("extension", text="Extensión")
        self.tree.heading("tamano", text="Tamaño")
        self.tree.heading("fecha", text="Fecha")
        
        self.tree.column("#0", width=30, stretch=False)
        self.tree.column("nombre", width=400)
        self.tree.column("extension", width=80)
        self.tree.column("tamano", width=100)
        self.tree.column("fecha", width=150)
        
        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind para selección con click
        self.tree.bind("<Button-1>", self.on_tree_click)
        
        # Frame para botones de control
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="Seleccionar todos", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Deseleccionar todos", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        self.convert_button = ttk.Button(control_frame, text="Convertir seleccionados", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=5)
        
        # Frame para progreso
        progress_frame = ttk.Frame(self.root, padding="10")
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        self.progress_label = ttk.Label(progress_frame, text="Listo")
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate", length=400)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Frame para log (colapsable)
        log_container = ttk.Frame(self.root, padding="10")
        log_container.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.rowconfigure(4, weight=1)
        
        log_header = ttk.Frame(log_container)
        log_header.pack(fill=tk.X)
        
        self.toggle_log_button = ttk.Button(log_header, text="▼ Mostrar/Ocultar Log", command=self.toggle_log)
        self.toggle_log_button.pack(side=tk.LEFT)
        
        self.log_frame = ttk.Frame(log_container)
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(self.log_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def toggle_log(self):
        """Alternar visibilidad del log"""
        if self.log_visible.get():
            self.log_frame.pack_forget()
            self.log_visible.set(False)
            self.toggle_log_button.config(text="▶ Mostrar/Ocultar Log")
        else:
            self.log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            self.log_visible.set(True)
            self.toggle_log_button.config(text="▼ Mostrar/Ocultar Log")
    
    def log(self, message):
        """Añadir mensaje al log"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
    def browse_source(self):
        """Seleccionar carpeta origen"""
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder.set(folder)
            
    def browse_dest(self):
        """Seleccionar carpeta destino"""
        folder = filedialog.askdirectory()
        if folder:
            self.dest_folder.set(folder)
            
    def format_size(self, size_bytes):
        """Formatear tamaño en bytes a formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def load_files(self):
        """Cargar archivos WebM de la carpeta origen"""
        source = self.source_folder.get()
        
        if not source or not os.path.exists(source):
            messagebox.showerror("Error", "Por favor, selecciona una carpeta origen válida")
            return
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.files_data = []
        
        # Buscar archivos .webm
        webm_files = list(Path(source).glob("*.webm"))
        
        if not webm_files:
            messagebox.showinfo("Información", "No se encontraron archivos WebM en la carpeta")
            return
        
        for file_path in webm_files:
            stat = file_path.stat()
            file_info = {
                'path': file_path,
                'name': file_path.name,
                'extension': file_path.suffix,
                'size': stat.st_size,
                'date': datetime.fromtimestamp(stat.st_mtime),
                'selected': True
            }
            self.files_data.append(file_info)
            
            # Añadir a la tabla
            self.tree.insert("", tk.END, text="☑", values=(
                file_info['name'],
                file_info['extension'],
                self.format_size(file_info['size']),
                file_info['date'].strftime("%Y-%m-%d %H:%M:%S")
            ))
        
        self.log(f"Cargados {len(webm_files)} archivos WebM")
        
    def on_tree_click(self, event):
        """Manejar click en la tabla para seleccionar/deseleccionar"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "tree":
            item = self.tree.identify_row(event.y)
            if item:
                index = self.tree.index(item)
                if index < len(self.files_data):
                    self.files_data[index]['selected'] = not self.files_data[index]['selected']
                    checkbox = "☑" if self.files_data[index]['selected'] else "☐"
                    self.tree.item(item, text=checkbox)
                    
    def select_all(self):
        """Seleccionar todos los archivos"""
        for i, item in enumerate(self.tree.get_children()):
            self.files_data[i]['selected'] = True
            self.tree.item(item, text="☑")
            
    def deselect_all(self):
        """Deseleccionar todos los archivos"""
        for i, item in enumerate(self.tree.get_children()):
            self.files_data[i]['selected'] = False
            self.tree.item(item, text="☐")
    
    def get_video_dimensions(self, video_path):
        """Obtener dimensiones del video usando ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-of', 'json',
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace', check=True)
            data = json.loads(result.stdout)
            
            if 'streams' in data and len(data['streams']) > 0:
                stream = data['streams'][0]
                return stream.get('width'), stream.get('height')
        except Exception as e:
            self.log(f"Error obteniendo dimensiones de {video_path.name}: {str(e)}")
        
        return None, None
    
    def adjust_dimensions(self, width, height):
        """Ajustar dimensiones para que sean pares"""
        new_width = width if width % 2 == 0 else width - 1
        new_height = height if height % 2 == 0 else height - 1
        
        adjusted = new_width != width or new_height != height
        return new_width, new_height, adjusted
    
    def convert_file(self, file_info, dest_folder, index, total):
        """Convertir un archivo WebM a MP4"""
        input_path = file_info['path']
        output_name = input_path.stem + '.mp4'
        output_path = Path(dest_folder) / output_name
        
        self.log(f"\n[{index}/{total}] Procesando: {input_path.name}")
        
        # Obtener dimensiones
        width, height = self.get_video_dimensions(input_path)
        
        if width is None or height is None:
            self.log(f"  ⚠ No se pudieron obtener dimensiones, usando valores por defecto")
            filter_complex = None
        else:
            new_width, new_height, adjusted = self.adjust_dimensions(width, height)
            
            if adjusted:
                self.log(f"  ⚠ Dimensiones ajustadas: {width}x{height} → {new_width}x{new_height}")
                filter_complex = f"scale={new_width}:{new_height}"
            else:
                self.log(f"  ✓ Dimensiones correctas: {width}x{height}")
                filter_complex = None
        
        # Preparar comando ffmpeg
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-y',  # Sobrescribir sin preguntar
        ]
        
        if filter_complex:
            cmd.extend(['-vf', filter_complex])
        
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            str(output_path)
        ])
        
        self.log(f"  Comando: {' '.join(cmd)}")
        
        try:
            # Ejecutar ffmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Capturar salida
            duration = None
            for line in process.stderr:
                self.log(f"  {line.strip()}")
                
                # Intentar capturar duración
                if "Duration:" in line and duration is None:
                    match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2})", line)
                    if match:
                        h, m, s = map(int, match.groups())
                        duration = h * 3600 + m * 60 + s
                
                # Actualizar progreso si tenemos duración
                if duration and "time=" in line:
                    match = re.search(r"time=(\d{2}):(\d{2}):(\d{2})", line)
                    if match:
                        h, m, s = map(int, match.groups())
                        current_time = h * 3600 + m * 60 + s
                        file_progress = (current_time / duration) * 100 if duration > 0 else 0
                        overall_progress = ((index - 1) / total) * 100 + (file_progress / total)
                        self.root.after(0, lambda p=overall_progress: self.progress_bar.configure(value=p))
            
            process.wait()
            
            if process.returncode == 0:
                self.log(f"  ✓ Conversión completada: {output_name}")
                return True
            else:
                self.log(f"  ✗ Error en la conversión (código {process.returncode})")
                return False
                
        except Exception as e:
            self.log(f"  ✗ Error: {str(e)}")
            return False
    
    def start_conversion(self):
        """Iniciar proceso de conversión"""
        if self.converting:
            messagebox.showwarning("Advertencia", "Ya hay una conversión en progreso")
            return
        
        dest = self.dest_folder.get()
        if not dest or not os.path.exists(dest):
            messagebox.showerror("Error", "Por favor, selecciona una carpeta destino válida")
            return
        
        # Obtener archivos seleccionados
        selected_files = [f for f in self.files_data if f['selected']]
        
        if not selected_files:
            messagebox.showwarning("Advertencia", "No hay archivos seleccionados")
            return
        
        # Verificar que ffmpeg está disponible
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except:
            messagebox.showerror("Error", "FFmpeg no está disponible en el PATH. Por favor, instálalo primero.")
            return
        
        # Iniciar conversión en thread separado
        self.converting = True
        self.convert_button.config(state=tk.DISABLED)
        self.progress_bar.configure(value=0)
        
        thread = threading.Thread(target=self.conversion_thread, args=(selected_files, dest))
        thread.daemon = True
        thread.start()
    
    def conversion_thread(self, selected_files, dest_folder):
        """Thread para ejecutar conversiones"""
        total = len(selected_files)
        successful = 0
        
        self.root.after(0, lambda: self.progress_label.configure(text=f"Convirtiendo 0/{total}..."))
        self.log(f"\n{'='*60}")
        self.log(f"Iniciando conversión de {total} archivo(s)")
        self.log(f"{'='*60}")
        
        for i, file_info in enumerate(selected_files, 1):
            self.root.after(0, lambda idx=i: self.progress_label.configure(text=f"Convirtiendo {idx}/{total}..."))
            
            if self.convert_file(file_info, dest_folder, i, total):
                successful += 1
        
        # Finalizar
        self.root.after(0, lambda: self.progress_bar.configure(value=100))
        self.root.after(0, lambda: self.progress_label.configure(text=f"Completado: {successful}/{total} conversiones exitosas"))
        self.log(f"\n{'='*60}")
        self.log(f"Proceso completado: {successful}/{total} conversiones exitosas")
        self.log(f"{'='*60}\n")
        
        self.converting = False
        self.root.after(0, lambda: self.convert_button.config(state=tk.NORMAL))
        
        # Mostrar mensaje final
        if successful == total:
            self.root.after(0, lambda: messagebox.showinfo("Éxito", f"Todas las conversiones se completaron exitosamente"))
        else:
            self.root.after(0, lambda: messagebox.showwarning("Completado con errores", 
                f"Se completaron {successful}/{total} conversiones. Revisa el log para más detalles."))


def main():
    root = tk.Tk()
    app = WebmToMP4Converter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
