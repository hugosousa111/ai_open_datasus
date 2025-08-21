import logging

from tools.news_collector import NewsCollectorTool
from utils.utils import setup_logging


class NewsCollectorAgent:
    """
    Agente que utiliza a NewsCollectorTool para buscar notícias e
    retorna o resultado de forma estruturada.
    """

    def __init__(self):
        """
        Inicializa o agente e sua ferramenta principal, a NewsCollectorTool.
        """
        setup_logging()
        logging.info("Inicializando o NewsCollectorAgent...")
        try:
            self.collector_tool = NewsCollectorTool()
        except ValueError as e:
            logging.error(f"Erro fatal na inicialização do agente: {e}")
            raise

    def run(self) -> dict | None:
        """
        Executa o processo de coleta de notícias através da ferramenta e formata a saída.

        Returns:
            dict: Um dicionário com a chave 'news_file_path' e o caminho do arquivo salvo.
            None: Retorna None se o processo falhar.
        """
        logging.info(
            "--- Agente acionado para executar a tarefa de coleta de notícias ---"
        )

        result = self.collector_tool.run_collection_process()

        if result:
            logging.info(
                f"Agente concluiu a tarefa com sucesso. Notícias salvas em: {result}"
            )
            return {"news_file_path": result}
        else:
            logging.error("Agente falhou ao executar a tarefa de coleta de notícias.")
            return None
