import pandas as pd

#def cargar_y_procesar_datos(ruta):
#    df = pd.read_csv(ruta)
#    df.dropna(inplace=True)
#    df['nivel_desnutricion'] = df['nivel_desnutricion'].str.lower()
#    return df

def cargar_y_procesar_datos(ruta_excel, ruta_salida_csv="desnutricion_filtrada.csv"):
    columnas_relevantes = [
        "PCTE_IDE", "PCTE_SEXO", "PCTE_FEC_NAC", "PCTE_ANIOS_EN_MESES", "PCTE_PESO", "PCTE_TALLA",
        "PCTE_ULT_IMC", "PCTE_CAT_PESO_EDAD_Z", "PCTE_CAT_IMC_EDAD_Z", "PCTE_CAT_PESO_LONGTALLA_Z",
        "ATEMED_CIE10", "ATEMED_DES_CIE10", "NIVEL_DESCRIPCION",
        "ENT_DES_PROV", "ENT_DES_CANT", "ENT_DES_PARR"
    ]

    # Leer archivo Excel completo
    df = pd.read_excel(ruta_excel)

    # Asegurar que las columnas necesarias estén presentes
    columnas_faltantes = [col for col in columnas_relevantes if col not in df.columns]
    if columnas_faltantes:
        raise ValueError(f"Faltan columnas en el archivo Excel: {columnas_faltantes}")

    # Filtrar solo columnas relevantes
    df = df[columnas_relevantes]

    # Filtrar por tipo específico de desnutrición
    tipos_desnutricion = [
        'DESNUTRICION PROTEICOCALORICA LEVE', 
        'DESNUTRICION PROTEICOCALORICA MODERADA', 
        'DESNUTRICION PROTEICOCALORICA SEVERA'
    ]
    
    # Filtrar solo las filas que contienen estos tipos de desnutrición
    df = df[df["ATEMED_DES_CIE10"].isin(tipos_desnutricion)]

    # Eliminar filas incompletas en campos clave
    df.dropna(subset=["PCTE_IDE", "PCTE_PESO", "PCTE_TALLA"], inplace=True)

    # Guardar a CSV
    df.to_csv(ruta_salida_csv, index=False)

    return df

if __name__ == '__main__':
    df = cargar_y_procesar_datos('../data/desnutricion.csv')
    print(df.head())
