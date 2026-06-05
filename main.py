import argparse
import sys

def main() -> None:
    if len(sys.argv) <= 5:
        print("StreamUCV D/D")
        print('Uso: python main.py <server> <bd> <usuario> <password> <driver>')
        print('Ejemplo: python main.py localhost StreamUCV sa tu_password "ODBC Driver 17 for SQL Server"')
        return
    parser = argparse.ArgumentParser(description="StreamUCV D/D")
    parser.add_argument("server", type=str, help="Servidor o instancia de SQL Server")
    parser.add_argument("bd", type=str, help="Base de Datos")
    parser.add_argument("user", type=str, help="Usuario")
    parser.add_argument("pw", type=str, help="Contraseña")
    parser.add_argument("driver", type=str, help="Driver de conexion")
    args = parser.parse_args()
    
    print(args.server)
    print(args.bd)
    print(args.user)
    print(args.pw)
    print(args.driver)

if __name__ == "__main__":
    main()