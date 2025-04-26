from procesamiento.limpiar_y_procesar import cargar_y_procesar_datos
from semantic.generar_ontologia import generar_rdf_con_centros
from visualizacion.dashboard import visualizar_datos

if __name__ == '__main__':
    ruta_csv = 'data/desnutricionExcel.xlsx'
    df_resultado = cargar_y_procesar_datos(ruta_csv, "data/desnutricion_filtrada1.csv")

    #df_resultado = 'data/desnutricion_filtrada1.csv'
    ruta_rdf = 'data/desnutricion_ontologia_con_centros.ttl'

    # Generar el archivo RDF con la ontología, incluyendo niños y centros de salud
    generar_rdf_con_centros(df_resultado, ruta_rdf)
    #convertir_a_rdf(ruta_csv, 'data/datos.ttl')
    #visualizar_datos(ruta_csv)
