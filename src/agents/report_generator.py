import logging
from tools.report_generator import ReportGeneratorTool
from utils.utils import setup_logging


class ReportGeneratorAgent:
    """
    Agente que utiliza o ReportGeneratorTool para criar um relatório analítico
    e retorna o resultado de forma estruturada.
    """

    def __init__(
        self,
        metrics_file_path,
        last_30_days_json_file_path,
        last_12_months_json_file_path,
        news_file_path,
    ):
        """
        Inicializa o agente e sua ferramenta principal, o ReportGeneratorTool.
        """
        setup_logging()
        logging.info("Inicializando o ReportGeneratorAgent...")
        self.metrics_file_path = metrics_file_path
        self.last_30_days_json_file_path = last_30_days_json_file_path
        self.last_12_months_json_file_path = last_12_months_json_file_path
        self.news_file_path = news_file_path
        try:
            self.report_tool = ReportGeneratorTool(
                self.metrics_file_path,
                self.last_30_days_json_file_path,
                self.last_12_months_json_file_path,
                self.news_file_path,
            )
        except ValueError as e:
            logging.error(f"Erro fatal na inicialização do agente: {e}")
            raise

    def run(self) -> dict | None:
        """
        Executa o processo de geração de relatório através da ferramenta e formata a saída.

        Returns:
            dict: Um dicionário com a chave 'report_file_path' e o caminho do relatório gerado.
            None: Retorna None se a geração falhar.
        """
        logging.info(
            "--- Agente acionado para executar a tarefa de geração de relatório ---"
        )

        report_path = self.report_tool.run_report_process()

        if report_path:
            logging.info(
                f"Agente concluiu a tarefa com sucesso. Relatório em: {report_path}"
            )
            return {"report_file_path": report_path}
        else:
            logging.error("Agente falhou ao executar a tarefa de geração de relatório.")
            return None
