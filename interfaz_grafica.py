import io
import contextlib
import pyodbc
import tkinter as tk
from tkinter import scrolledtext
import main

# ===== CONFIGURACIÓN DE CONEXIÓN =====
SERVER   = "localhost"
DATABASE = "StreamUCV"
DRIVER   = "ODBC Driver 17 for SQL Server"
USERNAME = "sa"
PASSWORD = ""
USAR_AUTENTICACION_WINDOWS = True


def conectar():
    if USAR_AUTENTICACION_WINDOWS:
        partes = [
            f"DRIVER={{{DRIVER}}}",
            f"SERVER={SERVER}",
            f"DATABASE={DATABASE}",
            "Trusted_Connection=yes",
        ]
    else:
        partes = [
            f"DRIVER={{{DRIVER}}}",
            f"SERVER={SERVER}",
            f"DATABASE={DATABASE}",
            f"UID={USERNAME}",
            f"PWD={PASSWORD}",
        ]

    if "18" in DRIVER:
        partes.append("Encrypt=yes")
        partes.append("TrustServerCertificate=yes")

    cadena = ";".join(partes) + ";"
    return pyodbc.connect(cadena)


def capturar_salida(funcion, *args):
    """Ejecuta una función que usa print() y devuelve su salida como texto."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        funcion(*args)
    return buffer.getvalue()


class Aplicacion:
    def __init__(self, ventana, conn):
        self.conn = conn
        self.ventana = ventana
        self.ventana.title("StreamUCV - Diccionario de Datos")
        self.ventana.geometry("950x600")

        # ----- Panel izquierdo: botones -----
        panel_botones = tk.Frame(ventana, padx=10, pady=10)
        panel_botones.pack(side="left", fill="y")

        tk.Label(panel_botones, text="Reportes",
                 font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))

        reportes = [
            ("1. Tablas e índices", self.req1),
            ("2. Conteo de índices", self.req2),
            ("3. Restricciones", self.req3),
            ("4. Detalle de índices", self.req4),
            ("5. Triggers", self.req5),
            ("6. Tamaño de tablas", self.req6),
            ("7. Tamaño de registros", self.req7),
            ("8. Tamaño de columnas", self.req8),
            ("9. Factor de bloqueo", self.req9),
        ]
        for texto, comando in reportes:
            tk.Button(panel_botones, text=texto, width=24, anchor="w",
                      command=comando).pack(pady=2)

        # ----- Requerimiento 10 (necesita tabla y columna) -----
        tk.Label(panel_botones, text="10. Búsqueda con índice",
                 font=("Segoe UI", 9, "bold")).pack(pady=(12, 2))

        tk.Label(panel_botones, text="Tabla:").pack(anchor="w")
        self.entrada_tabla = tk.Entry(panel_botones, width=24)
        self.entrada_tabla.insert(0, "serie")
        self.entrada_tabla.pack(pady=2)

        tk.Label(panel_botones, text="Columna:").pack(anchor="w")
        self.entrada_columna = tk.Entry(panel_botones, width=24)
        self.entrada_columna.insert(0, "nombre_serie")
        self.entrada_columna.pack(pady=2)

        tk.Button(panel_botones, text="Ejecutar búsqueda", width=24,
                  command=self.req10).pack(pady=4)

        # ----- Panel derecho: resultados -----
        panel_resultado = tk.Frame(ventana, padx=10, pady=10)
        panel_resultado.pack(side="right", fill="both", expand=True)

        self.area_texto = scrolledtext.ScrolledText(
            panel_resultado, wrap="word", font=("Consolas", 10))
        self.area_texto.pack(fill="both", expand=True)

        # ----- Barra de estado -----
        self.barra_estado = tk.Label(ventana, text="Conexión exitosa a StreamUCV",
                                     bd=1, relief="sunken", anchor="w")
        self.barra_estado.pack(side="bottom", fill="x")

    def mostrar(self, texto):
        self.area_texto.delete("1.0", tk.END)
        self.area_texto.insert(tk.END, texto)

    def ejecutar(self, funcion, *args):
        try:
            salida = capturar_salida(funcion, *args)
            self.mostrar(salida)
            self.barra_estado.config(text="Reporte ejecutado correctamente")
        except Exception as e:
            self.mostrar(f"Error al ejecutar el reporte:\n{e}")
            self.barra_estado.config(text="Error al ejecutar el reporte")

    # ----- Requerimientos implementados -----
    def req1(self):
        self.ejecutar(main.requisito1, self.conn)

    def req2(self):
        self.ejecutar(main.requisito2, self.conn)

    def req3(self):
       self.ejecutar(main.requisito3, self.conn)  
  
    def req4(self):
        self.ejecutar(main.requisito4, self.conn)

    def req5(self):
        self.ejecutar(main.requisito5, self.conn)

    def req6(self):
        self.ejecutar(main.requisito6, self.conn)     

    def req7(self):
        self.ejecutar(main.requisito7, self.conn)

    def req8(self):
        self.ejecutar(main.requisito8, self.conn)

    def req9(self):
        self.ejecutar(main.requisito9, self.conn)  
   

    def req10(self):
        tabla = self.entrada_tabla.get()
        columna = self.entrada_columna.get()
        self.ejecutar(main.requisito10, self.conn, tabla, columna)

def main_grafica():
    try:
        conn = conectar()
    except Exception as e:
        ventana = tk.Tk()
        ventana.title("Error de conexión")
        tk.Label(ventana, text=f"No se pudo conectar a la base de datos:\n{e}",
                 padx=20, pady=20).pack()
        ventana.mainloop()
        return

    ventana = tk.Tk()
    Aplicacion(ventana, conn)
    ventana.mainloop()
    conn.close()


if __name__ == "__main__":
    main_grafica()
