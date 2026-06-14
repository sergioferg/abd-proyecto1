import pyodbc
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


def mostrar_menu():
    print("")
    print("======================================")
    print("   StreamUCV - Diccionario de Datos")
    print("======================================")
    print("  1. Listar tablas e índices")
    print("  2. Total de tablas e índices por tabla")
    print("  3. Restricciones (pendiente)")
    print("  4. Detalle de índices")
    print("  5. Triggers")
    print("  6. Tamaño de tablas (pendiente)")
    print("  7. Tamaño de registros")
    print("  8. Tamaño de columnas")
    print("  9. Factor de bloqueo (pendiente)")
    print(" 10. Búsqueda con índice")
    print("  0. Salir")


def ejecutar_opcion(opcion, conn):
    if opcion == "1":
        main.requisito1(conn)
    elif opcion == "2":
        main.requisito2(conn)
    elif opcion == "3":
        print("Requerimiento pendiente")  
    elif opcion == "4":
        main.requisito4(conn)
    elif opcion == "5":
        main.requisito5(conn)
    elif opcion == "6":
        print("Requerimiento pendiente")   
    elif opcion == "7":
        main.requisito7(conn)
    elif opcion == "8":
        main.requisito8(conn)
    elif opcion == "9":
        print("Requerimiento pendiente")   
    elif opcion == "10":
        tabla = input("Nombre de la tabla: ")
        columna = input("Nombre de la columna: ")
        main.requisito10(conn, tabla, columna)
    else:
        print("Opción no válida.")


def main_consola():
    try:
        conn = conectar()
        print("Conexión exitosa!")
    except Exception as e:
        print(f"Error de conexión: {e}")
        return

    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ")

        if opcion == "0":
            print("Saliendo...")
            break

        print("")
        ejecutar_opcion(opcion, conn)
        input("\nPresiona Enter para continuar...")

    conn.close()


if __name__ == "__main__":
    main_consola()
