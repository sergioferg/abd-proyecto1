import argparse
import sys
import pyodbc

def main() -> None:
    parser = argparse.ArgumentParser(description="StreamUCV D/D")
    parser.add_argument("server", type=str, help="Servidor o instancia de SQL Server")
    parser.add_argument("db", type=str, help="Base de Datos")
    parser.add_argument("user", type=str, help="Usuario")
    parser.add_argument("pw", type=str, help="Contraseña")
    parser.add_argument("driver", type=str, help="Driver de conexion")
    args = parser.parse_args()

    connection = []
    
    #SQL_CONNECTION_STRING="Driver={<driver>};Server=<server_name>;Database=<database_name>;UId=<username>;Pwd=<password>"

    connection = [
        f"Driver={{{args.driver}}}",
        f"Server={args.server}",
        f"Database={args.db}",
        f"UId={args.user}",
        f"Pwd={args.pw}",
    ]
    
    connection_string = ";".join(connection) + ";"
    

    try: 
        conn = pyodbc.connect(connection_string)
        print("Conexión exitosa!")
        print(connection_string)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

    

if __name__ == "__main__":
    main()