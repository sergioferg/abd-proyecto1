import argparse
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

    if "18" in args.driver:
        connection.append("Encrypt=yes")
        connection.append("TrustServerCertificate=yes")
    
    connection_string = ";".join(connection) + ";"
    
    try: 
        conn = pyodbc.connect(connection_string)
        print("Conexión exitosa!")
        print(connection_string)
        requisito1(conn)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

# Ejemplo de consulta
def requisito1(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()
    query1 = """
        SELECT TABLE_NAME AS 'Nombre' 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'streaming' 
        AND TABLE_TYPE = 'BASE TABLE';
    """

    query2 = """
        WITH object_id_cte AS ( 
            SELECT OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME) AS 'id', TABLE_NAME AS 'Nombre' 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'streaming' 
            AND TABLE_TYPE = 'BASE TABLE' 
        ) 
        SELECT si.name 
        FROM sys.indexes si 
        JOIN object_id_cte oi ON (si.object_id = oi.id) 
    """

    cursor.execute(query1)

    rows = cursor.fetchall()

    print("Nombre de Tablas:")
    for row in rows:
        print(str(row).lstrip("('").rstrip("',)"))

    # Otra manera de hacerlo (no se entiende pero se puede)
    # print("Nombre de Tablas:")
    # print("\n".join(["\n".join([str(val) for val in row]) for row in rows]))

    print("")

    cursor.execute(query2)
    rows = cursor.fetchall()

    print("Nombre de Indices:")
    for row in rows:
        print(str(row).lstrip("('").rstrip("',)"))




    
    

if __name__ == "__main__":
    main()