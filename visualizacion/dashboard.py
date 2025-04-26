import pandas as pd
import matplotlib.pyplot as plt

def visualizar_datos(ruta_csv):
    df = pd.read_csv(ruta_csv)
    conteo = df['nivel_desnutricion'].value_counts()
    conteo.plot(kind='bar', title='Niveles de desnutrición')
    plt.xlabel('Nivel')
    plt.ylabel('Número de casos')
    plt.tight_layout()
    plt.savefig('./data/grafico_desnutricion.png')
    plt.show()

if __name__ == '__main__':
    visualizar_datos('./data/desnutricion.csv')
