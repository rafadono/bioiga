import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_correlation_matrix(df: pd.DataFrame, output_path: str):
    cols_to_correlate = [col for col in df.columns if col.startswith('params_')] + ['value']
    corr_df = df[cols_to_correlate].copy()
    
    rename_dict = {
        'params_pop_size': 'Tamano Swarm',
        'params_w': 'Peso Inercia (w)',
        'params_c1': 'Cognitivo (c1)',
        'params_c2': 'Social (c2)',
        'value': 'Error Final'
    }
    corr_df = corr_df.rename(columns=rename_dict)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        corr_df.corr(), 
        annot=True, 
        cmap='coolwarm', 
        vmin=-1, 
        vmax=1, 
        fmt=".2f", 
        linewidths=.5
    )
    plt.title('MBPSO Correlacion: Hiperparametros vs Error Final', pad=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] Matriz de correlacion guardada en: {output_path}")

def plot_bottleneck_impact(df: pd.DataFrame, output_path: str):
    best_results = df.groupby(['benchmark_problem', 'evolutionary_model'])['value'].min().unstack()
    colores = ['#e74c3c', '#2ecc71'] 
    
    ax = best_results.plot(kind='bar', figsize=(10, 6), color=colores)
    
    plt.title('MBPSO: Impacto del Cuello de Botella por Topografia Matematica', pad=20)
    plt.ylabel('Mejor Error Alcanzado (Escala Logaritmica - Menor es mejor)')
    plt.xlabel('Problema Matematico')
    plt.xticks(rotation=0)
    plt.yscale('log') 
    
    plt.legend(title='Modelo Evolutivo')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] Grafico de impacto guardado en: {output_path}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "output")
    input_csv = os.path.join(output_dir, "robust_optuna_catalog_mbpso.csv")
    
    print("-" * 60)
    print("INICIANDO ANALISIS DE RESULTADOS MBPSO")
    print("-" * 60)

    if not os.path.exists(input_csv):
        print(f"Error: No se encontro el archivo de datos en {input_csv}")
        print("Asegurate de ejecutar 'python src/study.py' primero.")
        return

    df = pd.read_csv(input_csv)
    
    if 'state' in df.columns:
        df = df[df['state'] == 'COMPLETE']

    plot_correlation_matrix(df, os.path.join(output_dir, "matriz_correlacion_mbpso.png"))
    plot_bottleneck_impact(df, os.path.join(output_dir, "impacto_cuello_botella_mbpso.png"))
    
    print("-" * 60)
    print("Analisis finalizado. Revisa la carpeta 'output/'.")

if __name__ == "__main__":
    main()
