from rdflib import Graph, Literal, RDF, URIRef, Namespace
import pandas as pd
import re 
#def convertir_a_rdf(csv_path, output_path):
#    df = pd.read_csv(csv_path)
#    g = Graph()
#    NS = Namespace("http://example.org/desnutricion#")

#    for _, row in df.iterrows():
#        nino = URIRef(NS[f"Nino{row['id']}"])
#        g.add((nino, RDF.type, NS.Nino))
#        g.add((nino, NS.edadMeses, Literal(row['edad_meses'])))
#        g.add((nino, NS.peso, Literal(row['peso'])))
#        g.add((nino, NS.talla, Literal(row['talla'])))
#        g.add((nino, NS.sexo, Literal(row['sexo'])))
#        g.add((nino, NS.ubicacion, Literal(row['ubicacion'])))
#        g.add((nino, NS.nivelDesnutricion, Literal(row['nivel_desnutricion'])))

#    g.serialize(destination=output_path, format='turtle')


def limpiar_nombre_centro(nombre):
    # Eliminar espacios extra y caracteres no válidos
    nombre_limpio = nombre.strip()  # Eliminar espacios al principio y al final
    nombre_limpio = re.sub(r'[^\w\s-]', '', nombre_limpio)  # Eliminar caracteres especiales
    nombre_limpio = re.sub(r'[\s]+', '-', nombre_limpio)  # Reemplazar espacios por guiones
    return nombre_limpio.lower()  # Convertir a minúsculas para consistencia

def generar_rdf_con_centros(df_limpio, output_path="desnutricion_ontologia_con_centros.ttl"):
    # Definir el espacio de nombres
    NS = Namespace("http://example.org/desnutricion#")

    # Crear un gráfico RDF vacío
    g = Graph()

    # Recorrer los datos limpios y agregar tripletas al gráfico
    for _, row in df_limpio.iterrows():
        # Crear un identificador único para cada niño (URI)
        nino_uri = URIRef(NS[f"Nino{row['PCTE_IDE']}"])

        # Añadir información del niño al gráfico
        g.add((nino_uri, RDF.type, NS.Nino))
        g.add((nino_uri, NS.sexo, Literal(row['PCTE_SEXO'])))
        g.add((nino_uri, NS.edad, Literal(row['PCTE_ANIOS_EN_MESES'])))
        g.add((nino_uri, NS.peso, Literal(row['PCTE_PESO'])))
        g.add((nino_uri, NS.talla, Literal(row['PCTE_TALLA'])))

        # Añadir el tipo de desnutrición
        g.add((nino_uri, NS.nivelDesnutricion, Literal(row['PCTE_CAT_PESO_EDAD_Z'])))

        # Limpiar el nombre del centro de salud para crear un URI válido
        centro_limpio = limpiar_nombre_centro(f"{row['ENT_DES_PROV']}-{row['ENT_DES_CANT']}-{row['ENT_DES_PARR']}")
        
        # Crear identificador único para el centro de salud
        centro_uri = URIRef(NS[f"Centro{centro_limpio}"])

        # Añadir información del centro de salud
        g.add((centro_uri, RDF.type, NS.CentroSalud))
        g.add((centro_uri, NS.nombreCentro, Literal(row['ENT_DES_PROV'])))  
        g.add((centro_uri, NS.tipoCentro, Literal("Centro de Salud")))  
        g.add((centro_uri, NS.provincia, Literal(row['ENT_DES_PROV'])))
        g.add((centro_uri, NS.canton, Literal(row['ENT_DES_CANT'])))
        g.add((centro_uri, NS.parroquia, Literal(row['ENT_DES_PARR'])))
        g.add((centro_uri, NS.nivelAtencion, Literal(row['NIVEL_DESCRIPCION'])))

        # Relacionar el niño con el centro de salud
        g.add((nino_uri, NS.atendidoPor, centro_uri))

    # Serializar y guardar el gráfico RDF en formato Turtle (.ttl)
    g.serialize(destination=output_path, format="turtle")
    print(f"Archivo RDF generado con centros de salud: {output_path}")

if __name__ == '__main__':
    convertir_a_rdf('../data/desnutricion.csv', '../data/datos.ttl')
