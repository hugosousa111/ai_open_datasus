import logging
from typing import Dict, Optional

from tools.data_preprocessor import DataPreprocessorTool
from utils.utils import setup_logging


class DataPreprocessorAgent:
    """
    Agente que utiliza o DataPreprocessorTool para limpar e transformar os dados e
    retorna o resultado de forma estruturada.
    """

    def __init__(self, downloaded_file_path):
        """
        Inicializa o agente e sua ferramenta principal, o DataPreprocessorTool.
        """
        setup_logging()
        logging.info("Inicializando o DataPreprocessorAgent...")
        self.downloaded_file_path = downloaded_file_path
        try:
            self.preprocessor_tool = DataPreprocessorTool(self.downloaded_file_path)
        except ValueError as e:
            logging.error(f"Erro fatal na inicialização do agente: {e}")
            raise

    def run(self) -> Optional[Dict[str, str]]:
        """
        Executa o processo de pré-processamento através da ferramenta e formata a saída.

        Returns:
            dict: Um dicionário com os caminhos dos arquivos gerados ('processed_data_path', 'metadata_path').
            None: Retorna None se o pré-processamento falhar.
        """
        logging.info(
            "--- Agente acionado para executar a tarefa de pré-processamento ---"
        )

        result = self.preprocessor_tool.run_preprocessing_process()

        if result:
            logging.info("=" * 50)
            logging.info("SUCESSO: Agente concluiu a tarefa de pré-processamento.")
            logging.info(
                f"Arquivo de dados salvo em: {result['processed_data_file_path']}"
            )
            logging.info("=" * 50)
            return result
        else:
            logging.error("=" * 50)
            logging.error(
                "FALHA: Agente falhou ao executar a tarefa de pré-processamento."
            )
            logging.error("=" * 50)
            return None
