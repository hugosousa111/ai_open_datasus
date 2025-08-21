import pandas as pd
from datetime import datetime, timedelta
import json
import os
import logging

from utils.utils import setup_logging, load_config


class MetricsCalculatorTool:
    """
    Classe responsável por calcular e salvar as métricas de saúde com base nos dados processados.
    """

    def __init__(self, processed_data_file_path):
        """
        Inicializa o calculador, configura o logging e carrega as configurações.
        """
        setup_logging()
        self.processed_data_file_path = processed_data_file_path
        try:
            config = load_config()
            self.cfg = config["metrics_calculator"]
            logging.info(
                "Configuração da ferramenta de métricas carregada com sucesso."
            )
        except (FileNotFoundError, KeyError) as e:
            logging.error(
                f"Falha ao carregar configuração para MetricsCalculatorTool. Detalhes: {e}"
            )
            raise ValueError(
                "Erro de configuração impede a continuação do cálculo de métricas."
            ) from e

    def _load_and_preprocess_data(self, filepath: str) -> pd.DataFrame | None:
        """
        Carrega os dados do arquivo CSV e realiza o pré-processamento.
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

    def _calculate_increase_rate(
        self,
        df,
        current_period_start,
        current_period_end,
        previous_period_start,
        previous_period_end,
    ) -> float:
        """Calcula a taxa de aumento de casos entre dois períodos. (Método privado)"""
        current_cases = df[
            (df["DATA_NOTIFICACAO"] >= current_period_start)
            & (df["DATA_NOTIFICACAO"] <= current_period_end)
        ].shape[0]
        previous_cases = df[
            (df["DATA_NOTIFICACAO"] >= previous_period_start)
            & (df["DATA_NOTIFICACAO"] <= previous_period_end)
        ].shape[0]

        if previous_cases == 0:
            return float("inf") if current_cases > 0 else 0.0

        return ((current_cases - previous_cases) / previous_cases) * 100

    def _calculate_mortality_rate(self, df, start_date, end_date) -> float:
        """Calcula a taxa de mortalidade em um determinado período. (Método privado)"""
        period_df = df[
            (df["DATA_NOTIFICACAO"] >= start_date)
            & (df["DATA_NOTIFICACAO"] <= end_date)
        ]
        evolution_defined = period_df[period_df["EVOLUCAO"].isin(["CURA", "OBITO"])]
        if evolution_defined.empty:
            return 0.0
        deaths = evolution_defined[evolution_defined["EVOLUCAO"] == "OBITO"].shape[0]
        return (deaths / evolution_defined.shape[0]) * 100

    def _calculate_uti_occupancy_rate(self, df, start_date, end_date) -> float:
        """Calcula a taxa de ocupação de UTI em um determinado período. (Método privado)"""
        period_df = df[
            (df["DATA_NOTIFICACAO"] >= start_date)
            & (df["DATA_NOTIFICACAO"] <= end_date)
        ]
        uti_defined = period_df[period_df["UTI"].isin(["SIM", "NAO"])]
        if uti_defined.empty:
            return 0.0
        uti_cases = uti_defined[uti_defined["UTI"] == "SIM"].shape[0]
        return (uti_cases / uti_defined.shape[0]) * 100

    def _calculate_vaccination_rate(
        self, df, start_date, end_date, vaccine_column
    ) -> float:
        """Calcula a taxa de vacinação em um determinado período. (Método privado)"""
        period_df = df[
            (df["DATA_NOTIFICACAO"] >= start_date)
            & (df["DATA_NOTIFICACAO"] <= end_date)
        ]
        vaccine_defined = period_df[period_df[vaccine_column].isin(["SIM", "NAO"])]
        if vaccine_defined.empty:
            return 0.0
        vaccinated_cases = vaccine_defined[
            vaccine_defined[vaccine_column] == "SIM"
        ].shape[0]
        return (vaccinated_cases / vaccine_defined.shape[0]) * 100

    def _save_json_file(self, data: dict, filename: str):
        """Salva um dicionário como um arquivo JSON no diretório de saída configurado."""
        output_dir = self.cfg["output_dir"]
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info(f"Arquivo '{filepath}' salvo com sucesso.")
        except Exception as e:
            logging.error(f"Falha ao salvar o arquivo '{filepath}': {e}")

    def run_metrics_calculation(self) -> dict | None:
        """
        Orquestra o processo de cálculo de métricas e salvamento dos resultados.
        Retorna um dicionário com os caminhos dos arquivos gerados ou None em caso de falha.
        """
        logging.info("--- Iniciando processo de cálculo de métricas (via Tool) ---")

        filepath = self.processed_data_file_path
        df = self._load_and_preprocess_data(filepath)

        if df is None:
            logging.error(
                "Processo de cálculo de métricas interrompido devido à falha no carregamento dos dados."
            )
            return None

        now = datetime.now()

        last_30_days_end = now
        last_30_days_start = now - timedelta(days=30)
        previous_30_days_end = last_30_days_start - timedelta(days=1)
        previous_30_days_start = previous_30_days_end - timedelta(days=30)

        last_7_days_end = now
        last_7_days_start = now - timedelta(days=7)
        previous_7_days_end = last_7_days_start - timedelta(days=1)
        previous_7_days_start = previous_7_days_end - timedelta(days=7)

        current_month_start = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        metadata = {
            "update_date": now.strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": filepath,
        }

        periods_analyzed = {
            "current_month": {
                "start": current_month_start.strftime("%Y-%m-%d"),
                "end": now.strftime("%Y-%m-%d"),
            },
            "last_month": {
                "start": last_month_start.strftime("%Y-%m-%d"),
                "end": last_month_end.strftime("%Y-%m-%d"),
            },
            "last_7_days": {
                "start": last_7_days_start.strftime("%Y-%m-%d"),
                "end": last_7_days_end.strftime("%Y-%m-%d"),
            },
            "previous_7_days": {
                "start": previous_7_days_start.strftime("%Y-%m-%d"),
                "end": previous_7_days_end.strftime("%Y-%m-%d"),
            },
            "last_30_days": {
                "start": last_30_days_start.strftime("%Y-%m-%d"),
                "end": last_30_days_end.strftime("%Y-%m-%d"),
            },
            "previous_30_days": {
                "start": previous_30_days_start.strftime("%Y-%m-%d"),
                "end": previous_30_days_end.strftime("%Y-%m-%d"),
            },
        }

        metrics = {
            "increase_rate": {
                "last_30_days_vs_previous": round(
                    self._calculate_increase_rate(
                        df,
                        last_30_days_start,
                        last_30_days_end,
                        previous_30_days_start,
                        previous_30_days_end,
                    ),
                    2,
                ),
                "last_7_days_vs_previous": round(
                    self._calculate_increase_rate(
                        df,
                        last_7_days_start,
                        last_7_days_end,
                        previous_7_days_start,
                        previous_7_days_end,
                    ),
                    2,
                ),
                "current_month_vs_previous": round(
                    self._calculate_increase_rate(
                        df, current_month_start, now, last_month_start, last_month_end
                    ),
                    2,
                ),
            },
            "mortality_rate": {
                "last_30_days": round(
                    self._calculate_mortality_rate(
                        df, last_30_days_start, last_30_days_end
                    ),
                    2,
                ),
                "last_7_days": round(
                    self._calculate_mortality_rate(
                        df, last_7_days_start, last_7_days_end
                    ),
                    2,
                ),
                "current_month": round(
                    self._calculate_mortality_rate(df, current_month_start, now), 2
                ),
            },
            "uti_occupancy_rate": {
                "last_30_days": round(
                    self._calculate_uti_occupancy_rate(
                        df, last_30_days_start, last_30_days_end
                    ),
                    2,
                ),
                "last_7_days": round(
                    self._calculate_uti_occupancy_rate(
                        df, last_7_days_start, last_7_days_end
                    ),
                    2,
                ),
                "current_month": round(
                    self._calculate_uti_occupancy_rate(df, current_month_start, now), 2
                ),
            },
            "vaccination_rate_flu": {
                "last_30_days": round(
                    self._calculate_vaccination_rate(
                        df, last_30_days_start, last_30_days_end, "VACINA"
                    ),
                    2,
                ),
                "last_7_days": round(
                    self._calculate_vaccination_rate(
                        df, last_7_days_start, last_7_days_end, "VACINA"
                    ),
                    2,
                ),
                "current_month": round(
                    self._calculate_vaccination_rate(
                        df, current_month_start, now, "VACINA"
                    ),
                    2,
                ),
            },
            "vaccination_rate_covid": {
                "last_30_days": round(
                    self._calculate_vaccination_rate(
                        df, last_30_days_start, last_30_days_end, "VACINA_COV"
                    ),
                    2,
                ),
                "last_7_days": round(
                    self._calculate_vaccination_rate(
                        df, last_7_days_start, last_7_days_end, "VACINA_COV"
                    ),
                    2,
                ),
                "current_month": round(
                    self._calculate_vaccination_rate(
                        df, current_month_start, now, "VACINA_COV"
                    ),
                    2,
                ),
            },
        }

        self._save_json_file(metadata, "metadata.json")
        self._save_json_file(periods_analyzed, "periods.json")
        self._save_json_file(metrics, "metrics.json")

        output_dir = self.cfg["output_dir"]
        result_paths = {
            "periods_file_path": os.path.join(output_dir, "periods.json"),
            "metrics_file_path": os.path.join(output_dir, "metrics.json"),
        }

        logging.info(
            "--- Processo de cálculo de métricas (via Tool) finalizado com sucesso. ---"
        )
        return result_paths
