import os
import logging
import pandas as pd
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from utils.utils import setup_logging, load_config


class DataPreprocessorTool:
    """
    Ferramenta responsável por executar as etapas de pré-processamento
    dos dados brutos de SRAG.
    """

    def __init__(self, downloaded_file_path):
        """
        Inicializa o pré-processador, configura o logging e carrega as configurações.
        """
        setup_logging()
        self.downloaded_file_path = downloaded_file_path
        try:
            config = load_config()
            self.proc_cfg = config["preprocessing"]
        except (FileNotFoundError, KeyError) as e:
            logging.error(
                f"Falha ao inicializar o DataPreprocessorTool devido a erro de configuração. Detalhes: {e}"
            )
            raise ValueError("Erro de configuração impede a continuação.") from e

    def _load_raw_data(
        self, full_path: str, columns: List[str]
    ) -> Optional[pd.DataFrame]:
        """Carrega o arquivo CSV bruto. (Método privado)"""
        logging.info(f"Iniciando a leitura do arquivo: {full_path}")
        try:
            df = pd.read_csv(full_path, sep=";", low_memory=False)
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                logging.error(
                    f"As seguintes colunas não foram encontradas no arquivo: {missing_cols}"
                )
                return None
            logging.info(f"Arquivo carregado. Selecionando {len(columns)} colunas.")
            return df[columns].copy()
        except FileNotFoundError:
            logging.error(
                f"ARQUIVO NÃO ENCONTRADO no caminho especificado: '{full_path}'"
            )
            return None
        except Exception as e:
            logging.error(f"Ocorreu um erro inesperado ao ler o arquivo CSV: {e}")
            return None

    def _process_notification_date(self, df: pd.DataFrame) -> None:
        """Processa a coluna de data de notificação. (Método privado)"""
        logging.info("Processando a coluna de data de notificação...")
        df.dropna(subset=["DT_NOTIFIC"], inplace=True)
        df["DT_NOTIFIC"] = pd.to_datetime(df["DT_NOTIFIC"], errors="coerce")
        df.rename(columns={"DT_NOTIFIC": "DATA_NOTIFICACAO"}, inplace=True)

    def _process_mapped_columns(
        self, df: pd.DataFrame, columns: List[str], mapping: Dict[Any, str]
    ) -> None:
        """Processa colunas com mapeamento de valores. (Método privado)"""
        logging.info(f"Aplicando mapeamento nas colunas: {columns}...")
        for col in columns:
            if col in df.columns:
                df[col].fillna(9.0, inplace=True)
                df[col] = df[col].replace(mapping)
            else:
                logging.warning(f"Coluna '{col}' não encontrada para mapeamento.")

    def _process_evolution_column(
        self, df: pd.DataFrame, mapping: Dict[Any, str]
    ) -> None:
        """Processa a coluna 'EVOLUCAO'. (Método privado)"""
        logging.info("Processando a coluna de evolução do caso...")
        if "EVOLUCAO" in df.columns:
            df["EVOLUCAO"].fillna(9.0, inplace=True)
            df["EVOLUCAO"] = df["EVOLUCAO"].replace(3.0, 2.0)
            df["EVOLUCAO"] = df["EVOLUCAO"].replace(mapping)
        else:
            logging.warning("Coluna 'EVOLUCAO' não encontrada para processamento.")

    def _clean_and_transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Orquestra as etapas de limpeza. (Método privado)"""
        if df.empty:
            logging.warning(
                "O DataFrame de entrada está vazio. Nenhuma transformação será aplicada."
            )
            return pd.DataFrame()

        logging.info("--- Iniciando etapa de limpeza e transformação dos dados ---")
        map_sim_nao = {1.0: "SIM", 2.0: "NAO", 9.0: "IGNORADO"}
        map_evolucao = {1.0: "CURA", 2.0: "OBITO", 9.0: "IGNORADO"}

        self._process_notification_date(df)
        self._process_mapped_columns(df, ["UTI", "VACINA", "VACINA_COV"], map_sim_nao)
        self._process_evolution_column(df, map_evolucao)

        logging.info("--- Finalizada a etapa de limpeza e transformação ---")
        return df

    def _save_processed_data(self, df: pd.DataFrame, full_path: str) -> bool:
        """Salva o DataFrame processado. (Método privado)"""
        if df.empty:
            logging.warning("O DataFrame está vazio. Nenhum arquivo CSV será salvo.")
            return False
        try:
            logging.info(f"Salvando os dados processados em: {full_path}")
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            df.to_csv(full_path, index=False, encoding="utf-8")
            logging.info("Arquivo CSV salvo com sucesso!")
            return True
        except Exception as e:
            logging.error(f"Falha ao salvar o arquivo CSV processado: {e}")
            return False

    def _save_metadata(self, output_folder: str) -> bool:
        """
        Salva um arquivo de metadados com a data e hora da atualização. (Método privado)
        """
        metadata_path = os.path.join(output_folder, "metadata.json")
        update_timestamp = datetime.now()
        formatted_timestamp = update_timestamp.strftime("%Y-%m-%d %H:%M:%S")

        metadata = {"update_date": formatted_timestamp}

        try:
            logging.info(f"Salvando arquivo de metadados em: {metadata_path}")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)
            logging.info("Arquivo de metadados salvo com sucesso!")
            return True
        except Exception as e:
            logging.error(f"Falha ao salvar o arquivo de metadados: {e}")
            return False

    def run_preprocessing_process(self) -> Optional[Dict[str, str]]:
        """
        Função que orquestra todo o processo de pré-processamento.
        Renomeada para maior clareza no padrão Agente/Ferramenta.
        Retorna um dicionário com os caminhos dos arquivos em caso de sucesso, ou None em caso de falha.
        """
        logging.info(
            "--- Iniciando processo de pré-processamento do arquivo SRAG (via Tool) ---"
        )

        output_folder = self.proc_cfg["output_folder"]
        output_path = os.path.join(output_folder, self.proc_cfg["output_filename"])

        df_raw = self._load_raw_data(
            full_path=self.downloaded_file_path,
            columns=self.proc_cfg["columns_to_keep"],
        )

        if df_raw is None:
            logging.error(
                "FALHA: O script não pôde continuar devido a erro na leitura do arquivo de entrada."
            )
            return None

        df_processed = self._clean_and_transform_data(df_raw)

        csv_success = self._save_processed_data(df_processed, output_path)
        if not csv_success:
            logging.error(
                "FALHA: Não foi possível salvar o arquivo de dados processado."
            )
            return None

        metadata_success = self._save_metadata(output_folder)
        if not metadata_success:
            logging.warning(
                "AVISO: O arquivo de dados foi salvo, mas falhou ao salvar os metadados."
            )
            return None

        logging.info("SUCESSO: Processo da ferramenta concluído.")
        return {
            "processed_data_file_path": output_path,
        }
