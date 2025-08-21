import logging
from tools.visualizations import VisualizationsTool
from utils.utils import setup_logging


class VisualizationsAgent:
    """
    Agente que utiliza a VisualizationsTool para gerar e salvar
    gráficos e dados, retornando o resultado de forma estruturada.
    """

    def __init__(self, processed_data_file_path):
        """
        Inicializa o agente e sua ferramenta principal, a VisualizationsTool.
        """
        setup_logging()
        logging.info("Inicializando o VisualizationsAgent...")
        self.processed_data_file_path = processed_data_file_path
        try:
            self.tool = VisualizationsTool(self.processed_data_file_path)
        except ValueError as e:
            logging.error(f"Erro fatal na inicialização do agente: {e}")
            raise

    def run(self) -> dict | None:
        """
        Executa o processo de geração de visualizações através da ferramenta e formata a saída.

        Returns:
            dict: Um dicionário contendo os caminhos para os arquivos gerados.
            None: Retorna None se a geração falhar.
        """
        logging.info("--- Agente acionado para executar a tarefa de visualização ---")

        result = self.tool.run_visualization_process()

        if result:
            logging.info("Agente concluiu a tarefa com sucesso. Arquivos gerados:")
            for key, path in result.items():
                logging.info(f"  - {key}: {path}")
            return result
        else:
            logging.error("Agente falhou ao executar a tarefa de visualização.")
            return None
