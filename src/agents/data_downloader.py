import logging

from tools.data_downloader import DataDownloaderTool
from utils.utils import setup_logging


class DataDownloaderAgent:
    """
    Agente que utiliza o DataDownloaderTool para baixar dados e
    retorna o resultado de forma estruturada.
    """

    def __init__(self):
        """
        Inicializa o agente e sua ferramenta principal, o DataDownloaderTool.
        """
        setup_logging()
        logging.info("Inicializando o DataDownloaderAgent...")
        try:
            self.downloader_tool = DataDownloaderTool()
        except ValueError as e:
            logging.error(f"Erro fatal na inicialização do agente: {e}")
            raise

    def run(self) -> dict | None:
        """
        Executa o processo de download através da ferramenta e formata a saída.

        Returns:
            dict: Um dicionário com a chave 'file_path' e o caminho do arquivo baixado.
            None: Retorna None se o download falhar.
        """
        logging.info("--- Agente acionado para executar a tarefa de download ---")

        result = self.downloader_tool.run_download_process()

        if result:
            logging.info(
                f"Agente concluiu a tarefa com sucesso. Arquivo em: {result['downloaded_file_path']}"
            )
            return result
        else:
            logging.error("Agente falhou ao executar a tarefa de download.")
            return None
