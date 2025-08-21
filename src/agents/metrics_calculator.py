import logging

from tools.metrics_calculator import MetricsCalculatorTool
from utils.utils import setup_logging


class MetricsCalculatorAgent:
    """
    Agente que utiliza a MetricsCalculatorTool para calcular as métricas
    e retorna o resultado de forma estruturada.
    """

    def __init__(self, processed_data_file_path):
        """
        Inicializa o agente e sua ferramenta principal, a MetricsCalculatorTool.
        """
        setup_logging()
        logging.info("Inicializando o MetricsCalculatorAgent...")
        self.processed_data_file_path = processed_data_file_path
        try:
            self.metrics_tool = MetricsCalculatorTool(self.processed_data_file_path)
        except ValueError as e:
            logging.error(f"Erro fatal na inicialização do agente de métricas: {e}")
            raise

    def run(self) -> dict | None:
        """
        Executa o processo de cálculo de métricas através da ferramenta e formata a saída.

        Returns:
            dict: Um dicionário com os caminhos para os arquivos de métricas gerados.
            None: Retorna None se o cálculo falhar.
        """
        logging.info(
            "--- Agente acionado para executar a tarefa de cálculo de métricas ---"
        )

        result = self.metrics_tool.run_metrics_calculation()

        if result:
            logging.info("Agente concluiu a tarefa com sucesso. Arquivos gerados:")
            for key, path in result.items():
                logging.info(f"  - {key}: {path}")
            return result
        else:
            logging.error("Agente falhou ao executar a tarefa de cálculo de métricas.")
            return None
