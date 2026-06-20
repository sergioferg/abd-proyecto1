import argparse
import pyodbc


def safe_execute(cursor: pyodbc.Cursor, query: str, descripcion: str = "consulta", fetchone: bool = False):
    """Ejecuta una consulta y captura errores, devolviendo filas o None.

    Imprime mensajes de error en español si falla.
    """
    try:
        cursor.execute(query)
        return cursor.fetchone() if fetchone else cursor.fetchall()
    except Exception as e:
        print(f"Error al ejecutar la {descripcion}: {e}")
        return None

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
        #requisito2(conn)
        #requisito4(conn)
        #requisito5(conn)
        #requisito7(conn)
        #requisito8(conn)
        #requisito10(conn, "serie", "nombre_serie")
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

# 1. Listar el nombre de las tablas e índices existentes en el esquema
# streaming.

def requisito1(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()
    print_header(1, "Listar tablas e índices del esquema 'streaming'")

    query1 = """
        SELECT TABLE_NAME AS 'nombre' 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'streaming' 
        AND TABLE_TYPE = 'BASE TABLE';
    """

    query2 = """
        SELECT i.name AS 'nombre'
        FROM sys.tables t
        JOIN sys.indexes i 
            ON t.object_id = i.object_id
        JOIN sys.schemas s 
            ON t.schema_id = s.schema_id
        WHERE s.name = 'streaming'
    """

    rows = safe_execute(cursor, query1, "listar tablas")
    if rows is None:
        cursor.close()
        return

    print("Tablas:")
    for row in rows:
        print(f" - {row.nombre}")

    print("")
    rows = safe_execute(cursor, query2, "listar índices")
    if rows is None:
        cursor.close()
        return

    print("Índices:")
    for row in rows:
        print(f" - {row.nombre}")

    cursor.close()

# 2. Indicar la cantidad total de tablas y la cantidad de índices
# definidos por cada tabla.

def requisito2(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()
    print_header(2, "Cantidad total de tablas y cantidad de índices por tabla")

    query1 = """
        SELECT COUNT(*) AS total_tablas
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'streaming'
        AND TABLE_TYPE = 'BASE TABLE';
    """
    row = safe_execute(cursor, query1, "contar tablas", fetchone=True)
    if row is None:
        cursor.close()
        return
    print(f" - Total tablas: {row.total_tablas}")
    print("")

    query2 = """
        SELECT t.name AS tabla, COUNT(*) AS cantidad_indices
        FROM sys.indexes i
        JOIN sys.tables t
            ON i.object_id = t.object_id
        JOIN sys.schemas s
            ON t.schema_id = s.schema_id
        WHERE s.name = 'streaming'
        AND i.name IS NOT NULL
        GROUP BY t.name
        ORDER BY cantidad_indices DESC;
    """
    rows = safe_execute(cursor, query2, "contar índices por tabla")
    if rows is None:
        cursor.close()
        return

    print("Índices por tabla:")
    for row in rows:
        print(f" - {row.tabla:<20} | índices: {row.cantidad_indices:>3}")

    cursor.close()

def requisito3(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()
    print_header(3, "Restricciones del esquema 'streaming'")

    query = """
        SELECT 
            CONSTRAINT_NAME AS Nombre_Restriccion,
            TABLE_NAME AS Tabla_Asociada,
            CONSTRAINT_TYPE AS Tipo_Restriccion
        FROM 
            INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
        WHERE 
            TABLE_SCHEMA = 'streaming'
        ORDER BY 
            TABLE_NAME, CONSTRAINT_TYPE;
    """

    rows = safe_execute(cursor, query, "listar restricciones")
    if rows is None:
        cursor.close()
        return

    if not rows:
        print(" - No se encontraron restricciones en el esquema 'streaming'.")
    else:
        for row in rows:
            print(f" - {row.Tabla_Asociada:<20} | {row.Tipo_Restriccion:<15} | {row.Nombre_Restriccion}")

    cursor.close()

# 4. Para cada índice creado en el esquema, listar las columnas que lo
# conforman, indicar si es único o no, y mostrar información
# relevante del índice disponible en el Diccionario de Datos de SQL Server.

def requisito4(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()
    print_header(4, "Columnas que conforman índices y propiedades")

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

    rows = safe_execute(cursor, query, "listar índices y columnas")
    if rows is None:
        cursor.close()
        return

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
    
    if not dictrow:
        print(" - No se encontraron índices en el esquema 'streaming'.")
    else:
        for tabla, indices in dictrow.items():
            print(f" - Tabla: {tabla}")
            for indice, datos in indices.items():
                columnas = ", ".join(datos["columnas"])
                print(f"    - {indice:<30} | {datos['tipo']:<15} | Único: {str(datos['es_unico']):<8} | Frag: {datos['fragmentacion_porcentaje']:>6}% | Columnas: {columnas}")
            print("")

    cursor.close()
        
# 5. Por cada trigger existente en el esquema, indicar su nombre, tipo,
# estado y tabla que lo activa.

def requisito5(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()
    print_header(5, "Triggers existentes en el esquema 'streaming'")

    query = """
        SELECT
            tr.name AS trigger_nombre,
            t.name AS tabla,
            CASE WHEN tr.is_instead_of_trigger = 1 THEN 'INSTEAD OF' ELSE 'AFTER' END AS tipo,
            CASE WHEN tr.is_disabled = 1 THEN 'Deshabilitado' ELSE 'Habilitado' END AS estado
        FROM sys.triggers tr
        JOIN sys.tables t
            ON tr.parent_id = t.object_id
        JOIN sys.schemas s
            ON t.schema_id = s.schema_id
        WHERE s.name = 'streaming'
        ORDER BY t.name, tr.name;
    """
    rows = safe_execute(cursor, query, "listar triggers")
    if rows is None:
        cursor.close()
        return

    if not rows:
        print(" - No existen triggers en el esquema 'streaming'.")
    else:
        for row in rows:
            print(f" - Nombre: {row.trigger_nombre} | Tabla: {row.tabla} | Tipo: {row.tipo} | Estado: {row.estado}")

    cursor.close()

def requisito6(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()
    print_header(6, "Tamaño físico estimado de las tablas")

    query = """
        SELECT 
            t.name AS tabla,
            SUM(a.total_pages) AS total_paginas,
            SUM(a.total_pages) * 8 AS tamano_kb
        FROM 
            sys.tables t
        JOIN 
            sys.schemas s ON t.schema_id = s.schema_id
        JOIN 
            sys.indexes i ON t.object_id = i.object_id
        JOIN 
            sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
        JOIN 
            sys.allocation_units a ON p.partition_id = a.container_id
        WHERE 
            s.name = 'streaming'
        GROUP BY 
            t.name
        ORDER BY 
            tamano_kb DESC;
    """

    rows = safe_execute(cursor, query, "calcular tamaño físico de tablas")
    if rows is None:
        cursor.close()
        return

    if not rows:
        print(" - No se encontraron tablas en el esquema 'streaming'.")
    else:
        for row in rows:
            print(f" - {row.tabla:<30} | Páginas: {row.total_paginas:>8} | Tamaño: {row.tamano_kb:>10} KB")

    cursor.close()
# 7. Calcular o estimar el tamaño de cada registro en bytes.

def requisito7(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()
    print_header(7, "Estimación del tamaño de cada registro por columna")

    query = """
        SELECT 
            t.name AS tabla, 
            c.name AS columna, 
            c.max_length AS tam
        FROM sys.tables t
        JOIN sys.schemas s 
            ON t.schema_id = s.schema_id
        JOIN sys.columns c 
            ON t.object_id = c.object_id
        WHERE s.name = 'streaming'
        ORDER BY t.name;
    """

    rows = safe_execute(cursor, query, "listar tamaño por columna")
    if rows is None:
        cursor.close()
        return

    if not rows:
        print(" - No se encontraron columnas en el esquema 'streaming'.")
    else:
        col_w = 30
        bytes_w = 6
        current_table = None

        for row in rows:
            tabla = row.tabla
            columna = row.columna
            tam = row.tam

            if tabla != current_table:
                # Nueva tabla: imprimir título y encabezado
                print(f"\n{tabla}:\n")
                print(f"{ 'Columna':<{col_w}} | { 'bytes':>{bytes_w}}")
                current_table = tabla

            print(f"{columna:<{col_w}} | {tam:>{bytes_w}} bytes")

    cursor.close()

# 8. Indicar el tamaño de cada columna en bytes, según su tipo de dato.

def requisito8(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()
    print_header(8, "Tamaño de cada columna según tipo de dato")

    query = """
        SELECT
            t.name AS tabla,
            c.name AS columna,
            ty.name AS tipo_dato,
            c.max_length AS tamano_bytes
        FROM sys.columns c
        JOIN sys.tables t
            ON c.object_id = t.object_id
        JOIN sys.schemas s
            ON t.schema_id = s.schema_id
        JOIN sys.types ty
            ON c.user_type_id = ty.user_type_id
        WHERE s.name = 'streaming'
        ORDER BY t.name, c.column_id;
    """
    rows = safe_execute(cursor, query, "listar tamaño por columna")
    if rows is None:
        cursor.close()
        return

    if not rows:
        print(" - No se encontraron columnas en el esquema 'streaming'.")
    else:
        col_w = 22
        type_w = 12
        bytes_w = 6
        current_table = None

        for row in rows:
            tabla = row.tabla
            columna = row.columna
            tipo = row.tipo_dato
            tam = row.tamano_bytes

            if tabla != current_table:
                # Nueva tabla: imprimir título y encabezado
                print(f"\n{tabla}:\n")
                print(f"{ 'Columna':<{col_w}} | { 'tipo':<{type_w}} | { 'bytes':>{bytes_w}}")
                current_table = tabla

            print(f"{columna:<{col_w}} | {tipo:<{type_w}} | {tam:>{bytes_w}}")

    cursor.close()

def requisito9(conn: pyodbc.Connection) -> None:
    cursor = conn.cursor()
    print_header(9, "Factor de bloqueo (páginas de 8 KB)")

    query = """
        SELECT 
            t.name AS Nombre_Objeto,
            'Tabla' AS Tipo_Objeto,
            SUM(c.max_length) AS Tamano_Registro_Bytes,
            8192 / SUM(c.max_length) AS Factor_Bloqueo
        FROM 
            sys.tables t
        JOIN 
            sys.columns c ON t.object_id = c.object_id
        WHERE 
            t.schema_id = SCHEMA_ID('streaming')
        GROUP BY 
            t.name

        UNION ALL

        SELECT 
            i.name AS Nombre_Objeto,
            'Índice' AS Tipo_Objeto,
            SUM(c.max_length) AS Tamano_Registro_Bytes,
            8192 / SUM(c.max_length) AS Factor_Bloqueo
        FROM 
            sys.indexes i
        JOIN 
            sys.tables t ON i.object_id = t.object_id
        JOIN 
            sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        JOIN 
            sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        WHERE 
            t.schema_id = SCHEMA_ID('streaming')
            AND i.type > 0 
        GROUP BY 
            i.name
            
        ORDER BY 
            Tipo_Objeto DESC, Nombre_Objeto;
    """

    rows = safe_execute(cursor, query, "calcular factor de bloqueo")
    if rows is None:
        cursor.close()
        return

    if not rows:
        print(" - No se encontraron objetos para calcular factor de bloqueo.")
    else:
        for row in rows:
            tipo = row.Tipo_Objeto.lower()
            print(f" - {tipo:<6} | {row.Nombre_Objeto:<30} | Registro: {row.Tamano_Registro_Bytes:>10} B | Factor/página: {row.Factor_Bloqueo:>8}")

    cursor.close()

# 10. Dada una consulta de igualdad sobre un campo de una tabla,
# indicar si existe un índice que pueda ser utilizado y estimar el
# costo en cantidad de accesos a disco y en tiempo.

def requisito10 (conn: pyodbc.Connection, tabla: str, columna: str) -> None:
    cursor = conn.cursor()
    print_header(10, f"Búsqueda de índice y estimación de costo para {tabla}.{columna}")

    # Estimación teórica de tiempo asumiendo 10ms (0.01s) por lectura física en un disco mecánico tradicional.
    query = f"""
        DECLARE @NombreTabla NVARCHAR(128) = '{tabla}';
        DECLARE @NombreColumna NVARCHAR(128) = '{columna}';

        SELECT 
            i.name AS indice,
            i.type_desc AS tipo,
            ps.index_depth AS profundidad, 
            ps.page_count AS total_paginas,
            CAST((ps.index_depth * 0.01) AS DECIMAL(10,4)) AS tiempo_estimado
        FROM sys.indexes i
        JOIN sys.tables t ON i.object_id = t.object_id
        JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        CROSS APPLY sys.dm_db_index_physical_stats(DB_ID(), t.object_id, i.index_id, NULL, 'LIMITED') ps
        WHERE t.name = @NombreTabla
        AND c.name = @NombreColumna
        AND ic.index_column_id = 1 -- Condición clave: la columna debe ser la primera del índice para ser usada directamente
        ORDER BY ps.index_depth ASC;
    """

    rows = safe_execute(cursor, query, f"buscar índices para {tabla}.{columna}")
    if rows is None:
        cursor.close()
        return

    if not rows:
        print(f" - No existe índice para la columna '{columna}' en la tabla '{tabla}'.")
        cursor.close()
        return
    
    for row in rows:
        indice = row.indice
        tipo = row.tipo
        profundidad = row.profundidad
        total_paginas = row.total_paginas
        tiempo_estimado = float(row.tiempo_estimado)

        print(f" - Índice: {indice} | Tipo: {tipo} | Profundidad: {profundidad} | Páginas: {total_paginas} | Tiempo estimado: {tiempo_estimado} s")

    cursor.close()

def tipo_format(tipo: str) -> str:
    mapeo_tipos = {
        "CLUSTERED": "AGRUPADO",
        "NONCLUSTERED": "NO AGRUPADO"
    }
    return mapeo_tipos.get(tipo, tipo)


def print_header(numero: int, titulo: str) -> None:
    """Imprime un encabezado consistente para cada requisito."""
    print("\n" + "=" * 60)
    print(f"Requisito {numero}: {titulo}")
    print("=" * 60)


def format(row: str) -> str:
    return row.lstrip("(").lstrip("'").rstrip(")").rstrip(",").rstrip("'")

if __name__ == "__main__":
    main()
