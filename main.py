import argparse
import pyodbc

def main() -> None:
    parser = argparse.ArgumentParser(description="StreamUCV D/D")
    parser.add_argument("server", type=str, help="Servidor o instancia de SQL Server")
    parser.add_argument("database", type=str, help="Base de Datos")
    parser.add_argument("user", type=str, help="Usuario")
    parser.add_argument("password", type=str, help="Contraseña")
    parser.add_argument("driver", type=str, help="Driver de conexion")
    args = parser.parse_args()

    connection = []
    
    #SQL_CONNECTION_STRING="Driver={<driver>};Server=<server_name>;Database=<database_name>;UId=<username>;Pwd=<password>"

    connection = [
        f"Driver={{{args.driver}}}",
        f"Server={args.server}",
        f"Database={args.database}",
        f"UId={args.user}",
        f"Pwd={args.password}",
    ]

    if "18" in args.driver:
        connection.append("Encrypt=yes")
        connection.append("TrustServerCertificate=yes")
    
    connection_string = ";".join(connection) + ";"
    
    try: 
        conn = pyodbc.connect(connection_string)
        print("Conexión exitosa!")
        print(connection_string)
        #requisito1(conn)
        #requisito4(conn)
        #requisito7(conn)
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

# 1. Listar el nombre de las tablas e índices existentes en el esquema
# streaming.

def requisito1(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()

    query1 = """
        SELECT TABLE_NAME AS 'nombre' 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'streaming' 
        AND TABLE_TYPE = 'BASE TABLE';
    """

    query2 = """
        SELECT i.name AS 'nombre'
        FROM sys.tables t
        JOIN sys.indexes i ON t.object_id = i.object_id
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE s.name = 'streaming'
    """

    cursor.execute(query1)

    rows = cursor.fetchall()

    print("Nombre de Tablas:")
    for row in rows:
        print(row.nombre)

    # Otra manera de hacerlo (no se entiende pero se puede)
    # print("Nombre de Tablas:")
    # print("\n".join(["\n".join([str(val) for val in row]) for row in rows]))

    print("")

    cursor.execute(query2)
    rows = cursor.fetchall()

    print("Nombre de Indices:")
    for row in rows:
        print(row.nombre)

# 4. Para cada índice creado en el esquema, listar las columnas que lo
# conforman, indicar si es único o no, y mostrar información
# relevante del índice disponible en el Diccionario de Datos de SQL Server.

def requisito4(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()

    query = """
        SELECT 
            t.name AS tabla, 
            i.name AS indice, 
            c.name AS columna, 
            i.is_unique, 
            i.type_desc AS tipo,
            ps.avg_fragmentation_in_percent AS fragmentacion
        FROM sys.indexes i
        JOIN sys.tables t 
            ON i.object_id = t.object_id
        JOIN sys.schemas s 
            ON t.schema_id = s.schema_id
        JOIN sys.index_columns ic 
            ON i.object_id = ic.object_id 
            AND i.index_id = ic.index_id
        JOIN sys.columns c 
            ON ic.object_id = c.object_id 
            AND ic.column_id = c.column_id
        CROSS APPLY sys.dm_db_index_physical_stats(DB_ID(), t.object_id, i.index_id, NULL, 'LIMITED') ps
        WHERE s.name = 'streaming'
        ORDER BY t.name, i.name, ic.index_column_id;
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    dictrow = {}

    for row in rows:
        tabla = row.tabla
        indice = row.indice
        columna = row.columna
        es_unico = row.is_unique
        tipo = row.tipo
        fragmentacion = row.fragmentacion

        if tabla not in dictrow:
            dictrow[tabla] = {}
            
        if indice not in dictrow[tabla]:
            dictrow[tabla][indice] = {
                "columnas": [],
                "es_unico": bool(es_unico),
                "tipo": tipo_format(tipo),
                "fragmentacion_porcentaje": round(float(fragmentacion), 2) if fragmentacion is not None else 0.0
            }
        
        dictrow[tabla][indice]["columnas"].append(columna)
    
    for key, value in dictrow.items():
        print(key, value)
        print("")
    
    #TODO
    '''
    ancho_tabla = 20
    ancho_indice = 30

    print(f"{'TABLA':<{ancho_tabla}} | {'INDICE':<{ancho_indice}} | COLUMNAS")
    print("-" * (ancho_tabla + ancho_indice + 27))

    
    
    for tabla, indices in dictrow.items():
        es_primera_vez_tabla = True
        
        for indice, datos in indices.items():
            es_primera_vez_indice = True  
            
            for columna in datos["columnas"]:
                
                texto_tabla = tabla if es_primera_vez_tabla else ""
                
                texto_indice = indice if es_primera_vez_indice else ""
                
                
                print(f"{texto_tabla:<{ancho_tabla}} | {texto_indice:<{ancho_indice}} | {columna}")
                
                
                es_primera_vez_tabla = False
                es_primera_vez_indice = False
        print(f"{' ':<{ancho_tabla}} | {' ':<{ancho_indice}} |")
    '''
        
# 7. Calcular o estimar el tamaño de cada registro en bytes.

def requisito7(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()

    query = """
        SELECT 
            t.name AS tabla, 
            c.name AS columna, 
            c.max_length AS tam
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        JOIN sys.columns c ON t.object_id = c.object_id
        WHERE s.name = 'streaming'
        ORDER BY t.name;
    """

    cursor.execute(query)

    rows = cursor.fetchall()


    for row in rows:
        tabla = row.tabla
        columna = row.columna
        tam = row.tam
        
        print(tabla, columna, tam)
        

# 10. Dada una consulta de igualdad sobre un campo de una tabla,
# indicar si existe un índice que pueda ser utilizado y estimar el
# costo en cantidad de accesos a disco y en tiempo.

def tipo_format(tipo: str) -> str:
    mapeo_tipos = {
        "CLUSTERED": "AGRUPADO",
        "NONCLUSTERED": "NO AGRUPADO"
    }
    
    return mapeo_tipos.get(tipo, tipo)

def format(row: str) -> str:
    return row.lstrip("(").lstrip("'").rstrip(")").rstrip(",").rstrip("'")

if __name__ == "__main__":
    main()