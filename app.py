from flask import Flask, request, jsonify
from rdflib import Graph
import re
from flask_cors import CORS

# Inicializamos la aplicación Flask
app = Flask(__name__)

CORS(app)
# Niveles de desnutrición y ubicaciones disponibles
niveles_desnutricion = ["Normal", "Normal/Seguimiento", "Bajo Peso", "Bajo Peso Severo", "Obesidad", "Desnutrición Crónica"]
ubicaciones = ["Loja", "Zamora", "El Oro"]  # Ejemplo de ubicaciones

# Función para procesar la consulta en lenguaje natural
def procesar_consulta(consulta):
    consulta = consulta.lower()

    cantidad = 20  # Valor por defecto
    nivel_desnutricion = None
    ubicacion = None
    edad_min = None
    edad_max = None
    peso_min = None
    peso_max = None
    sexo = None

    # Buscar la cantidad de casos mencionada (por ejemplo, 10, 20, etc.)
    cantidad_match = re.search(r'\d+', consulta)  # Buscar el primer número en la consulta
    if cantidad_match:
        cantidad = int(cantidad_match.group(0))

    # Buscar el nivel de desnutrición
    for nivel in niveles_desnutricion:
        if nivel.lower() in consulta:
            nivel_desnutricion = nivel

    # Buscar la ubicación (por ejemplo, Loja, El Oro, Zamora)
    for lugar in ubicaciones:
        if lugar.lower() in consulta:
            ubicacion = lugar

    # Buscar el rango de edad de forma más flexible
    edad_match = re.search(r'edad\s*(\d+)\s*(?:hasta|a|y)?\s*(\d+)?', consulta)
    if edad_match:
        edad_min = int(edad_match.group(1))  # Edad mínima
        edad_max = int(edad_match.group(2)) if edad_match.group(2) else edad_min  # Edad máxima o igual a la mínima

    # Buscar el rango de peso de forma más flexible
    peso_match = re.search(r'peso\s*(\d+(\.\d+)?)\s*(?:hasta|a|y)?\s*(\d+(\.\d+)?)?', consulta)
    if peso_match:
        peso_min = float(peso_match.group(1))  # Peso mínimo
        peso_max = float(peso_match.group(3)) if peso_match.group(3) else peso_min  # Peso máximo o igual al mínimo

    # Buscar sexo (si se menciona)
    if "hombre" in consulta:
        sexo = "Hombre"
    elif "mujer" in consulta:
        sexo = "Mujer"

    return cantidad, nivel_desnutricion, ubicacion, edad_min, edad_max, peso_min, peso_max, sexo

# Función para generar la consulta SPARQL dinámica basada en los parámetros
def generar_consulta_sparql(cantidad, nivel_desnutricion, ubicacion, edad_min, edad_max, peso_min, peso_max, sexo):
    # Usamos rdflib para consultar el archivo RDF
    graph = Graph()
    graph.parse('data/desnutricion_ontologia_con_centros.ttl', format='ttl')

    # Construir la consulta SPARQL de manera dinámica
    query = f"""
    SELECT ?nino ?nivelDesnutricion ?canton ?nombreCentro ?parroquia ?edad ?peso ?talla ?sexo
    WHERE {{
        ?nino a <http://example.org/desnutricion#Nino> ;
              <http://example.org/desnutricion#nivelDesnutricion> ?nivelDesnutricion ;
              <http://example.org/desnutricion#atendidoPor> ?centro ;
              <http://example.org/desnutricion#edad> ?edad ;
              <http://example.org/desnutricion#peso> ?peso ;
              <http://example.org/desnutricion#talla> ?talla ;
              <http://example.org/desnutricion#sexo> ?sexo .
        ?centro a <http://example.org/desnutricion#CentroSalud> ;
                <http://example.org/desnutricion#canton> ?canton ;
                <http://example.org/desnutricion#nombreCentro> ?nombreCentro ;
                <http://example.org/desnutricion#parroquia> ?parroquia .
    """

    # Filtros opcionales basados en la consulta
    if nivel_desnutricion:
        query += f"        FILTER (?nivelDesnutricion = '{nivel_desnutricion}')\n"
    if ubicacion:
        query += f"        FILTER (?canton = '{ubicacion.upper()}')\n"
    if edad_min is not None and edad_max is not None:
        query += f"        FILTER (?edad >= {edad_min} && ?edad <= {edad_max})\n"
    if peso_min is not None:
        query += f"        FILTER (?peso >= {peso_min})\n"  # Filtro para el peso
    if sexo:
        query += f"        FILTER (?sexo = '{sexo}')\n"

    query += f"    }}\nLIMIT {cantidad}"

    # Ejecutar la consulta en el grafo RDF
    results = graph.query(query)

    # Procesar los resultados y devolverlos en formato JSON
    sparql_results = []
    for row in results:
        sparql_results.append({
            "nino": str(row.nino),
            "nivelDesnutricion": str(row.nivelDesnutricion),
            "canton": str(row.canton),
            "nombreCentro": str(row.nombreCentro),
            "parroquia": str(row.parroquia),
            "edad": str(row.edad),
            "peso": str(row.peso),
            "talla": str(row.talla),
            "sexo": str(row.sexo)
        })

    return sparql_results

# Función para inicializar los datos antes de que el servidor comience a recibir peticiones
def inicializar_datos():
    try:
        # Ejecutar la carga y el procesamiento de datos
        from procesamiento.limpiar_y_procesar import cargar_y_procesar_datos
        from semantic.generar_ontologia import generar_rdf_con_centros

        ruta_csv = 'data/desnutricionExcel.xlsx'
        df_resultado = cargar_y_procesar_datos(ruta_csv, "data/desnutricion_filtrada1.csv")

        # Ejecutar la generación del archivo RDF
        ruta_rdf = 'data/desnutricion_ontologia_con_centros.ttl'
        generar_rdf_con_centros(df_resultado, ruta_rdf)

        print("Datos procesados y ontología generada exitosamente.")
    except Exception as e:
        print(f"Error al inicializar datos: {str(e)}")

# Inicializar los datos antes de que llegue la primera petición
inicializar_datos()

# Endpoint para recibir la consulta en lenguaje natural
@app.route("/consulta", methods=["POST"])
def consulta():
    try:
        # Obtener la consulta en lenguaje natural
        consulta_json = request.json
        consulta_texto = consulta_json.get("consulta", "")

        # Procesar la consulta
        cantidad, nivel_desnutricion, ubicacion, edad_min, edad_max, peso_min, peso_max, sexo = procesar_consulta(consulta_texto)

        # Generar la consulta SPARQL con los parámetros obtenidos
        sparql_results = generar_consulta_sparql(cantidad, nivel_desnutricion, ubicacion, edad_min, edad_max, peso_min, peso_max, sexo)

        # Devolver los resultados de la consulta SPARQL
        return jsonify(sparql_results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ejecutar el servidor Flask
if __name__ == "__main__":
    app.run(debug=True)
