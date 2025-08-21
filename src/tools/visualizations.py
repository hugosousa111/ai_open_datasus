import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import logging
import json
from datetime import datetime

from utils.utils import setup_logging, load_config


class VisualizationsTool:
    """
    Classe responsável por gerar e salvar visualizações (gráficos e dados)
    com base nos dados processados.
    """

    def __init__(self, processed_data_file_path):
        """
        Inicializa a ferramenta de visualização, configura o logging e carrega as configurações.
        """
        setup_logging()
        self.processed_data_file_path = processed_data_file_path
        try:
            config = load_config()
            self.cfg = config["visualizations_tool"]
            logging.info(
                "Configuração da ferramenta de visualizações carregada com sucesso."
            )
        except (FileNotFoundError, KeyError) as e:
            logging.error(
                f"Falha ao carregar configuração para VisualizationsTool. Detalhes: {e}"
            )
            raise ValueError(
                "Erro de configuração impede a continuação da geração de visualizações."
            ) from e

    def _load_and_preprocess_data(self, filepath: str) -> pd.DataFrame | None:
        """
        Carrega os dados do arquivo CSV e realiza o pré-processamento da coluna de data.
        (Método privado)
        """
        try:
            df = pd.read_csv(filepath)
            df["DATA_NOTIFICACAO"] = pd.to_datetime(df["DATA_NOTIFICACAO"])
            logging.info(f"Dados carregados e pré-processados de '{filepath}'.")
            return df
        except FileNotFoundError:
            logging.error(f"Erro: O arquivo de dados '{filepath}' não foi encontrado.")
            return None
        except Exception as e:
            logging.error(f"Erro inesperado ao ler o arquivo '{filepath}': {e}")
            return None

    def _save_json_file(self, data: dict, filename: str):
        """
        Salva um dicionário como um arquivo JSON no diretório de saída configurado.
        (Método privado)
        """
        output_dir = self.cfg["output_dir"]
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info(f"Arquivo '{filepath}' salvo com sucesso.")
        except Exception as e:
            logging.error(f"Falha ao salvar o arquivo '{filepath}': {e}")

    def _generate_last_30_days_analysis(self, df: pd.DataFrame):
        """
        Gera a análise dos últimos 30 dias, salvando um gráfico de linha e um arquivo JSON.
        (Método privado)
        """
        output_folder = self.cfg["output_dir"]

        end_date = df["DATA_NOTIFICACAO"].max()
        start_date = end_date - pd.Timedelta(days=30)

        last_30_days_df = df[df["DATA_NOTIFICACAO"] >= start_date].copy()
        daily_counts = (
            last_30_days_df.groupby("DATA_NOTIFICACAO").size().reset_index(name="count")
        )

        daily_counts_json = daily_counts.copy()
        daily_counts_json["DATA_NOTIFICACAO"] = daily_counts_json[
            "DATA_NOTIFICACAO"
        ].dt.strftime("%Y-%m-%d")
        self._save_json_file(
            daily_counts_json.to_dict(orient="records"), "last_30_days.json"
        )

        plt.figure(figsize=(15, 8))
        plt.plot(
            daily_counts["DATA_NOTIFICACAO"],
            daily_counts["count"],
            marker="o",
            linestyle="-",
        )
        plt.title("Número Diário de Casos nos Últimos 30 Dias")
        plt.xlabel("Data")
        plt.ylabel("Número de Casos")
        plt.grid(True)

        ax = plt.gca()
        ax.set_xticks(daily_counts["DATA_NOTIFICACAO"])
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))
        plt.xticks(rotation=90)

        plt.tight_layout()

        plot_path = os.path.join(output_folder, "last_30_days.png")
        plt.savefig(plot_path)
        logging.info(f"Gráfico dos últimos 30 dias salvo em: {plot_path}")
        plt.close()

    def _generate_last_12_months_analysis(self, df: pd.DataFrame):
        """
        Gera a análise dos últimos 12 meses, salvando um gráfico de barras e um arquivo JSON.
        (Método privado)
        """
        output_folder = self.cfg["output_dir"]

        end_date = df["DATA_NOTIFICACAO"].max()
        start_date = end_date - pd.DateOffset(months=12)

        last_12_months_df = df[
            (df["DATA_NOTIFICACAO"] >= start_date)
            & (df["DATA_NOTIFICACAO"] <= end_date)
        ].copy()
        monthly_counts = (
            last_12_months_df.groupby(
                last_12_months_df["DATA_NOTIFICACAO"].dt.to_period("M")
            )
            .size()
            .reset_index(name="count")
        )
        monthly_counts["DATA_NOTIFICACAO"] = monthly_counts["DATA_NOTIFICACAO"].astype(
            str
        )

        self._save_json_file(
            monthly_counts.to_dict(orient="records"), "last_12_months.json"
        )

        monthly_counts["month_label"] = pd.to_datetime(
            monthly_counts["DATA_NOTIFICACAO"]
        ).dt.strftime("%b-%Y")

        plt.figure(figsize=(12, 6))
        plt.bar(monthly_counts["month_label"], monthly_counts["count"])
        plt.title("Número Mensal de Casos nos Últimos 12 Meses")
        plt.xlabel("Mês")
        plt.ylabel("Número de Casos")
        plt.xticks(rotation=45)
        plt.tight_layout()

        plot_path = os.path.join(output_folder, "last_12_months.png")
        plt.savefig(plot_path)
        logging.info(f"Gráfico dos últimos 12 meses salvo em: {plot_path}")
        plt.close()

    def run_visualization_process(self) -> dict | None:
        """
        Orquestra o processo de geração de visualizações.
        Retorna um dicionário com os caminhos dos arquivos gerados em caso de sucesso,
        ou None em caso de falha.
        """
        logging.info(
            "--- Iniciando processo de geração de visualizações (via Tool) ---"
        )

        filepath = self.processed_data_file_path
        output_folder = self.cfg["output_dir"]

        os.makedirs(output_folder, exist_ok=True)

        now = datetime.now()
        metadata = {"update_date": now.strftime("%Y-%m-%d %H:%M:%S")}
        self._save_json_file(metadata, "metadata.json")

        df = self._load_and_preprocess_data(filepath)

        if df is None:
            logging.error(
                "Processo de visualização interrompido devido à falha no carregamento dos dados."
            )
            return None

        self._generate_last_30_days_analysis(df)
        self._generate_last_12_months_analysis(df)

        result = {
            "last_30_days_json_file_path": os.path.join(
                output_folder, "last_30_days.json"
            ),
            "last_30_days_plot_file_path": os.path.join(
                output_folder, "last_30_days.png"
            ),
            "last_12_months_json_file_path": os.path.join(
                output_folder, "last_12_months.json"
            ),
            "last_12_months_plot_file_path": os.path.join(
                output_folder, "last_12_months.png"
            ),
        }

        logging.info(
            "--- Processo de geração de visualizações (via Tool) finalizado com sucesso. ---"
        )
        return result
