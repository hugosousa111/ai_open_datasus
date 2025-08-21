import logging

from tools.final_report_generator import FinalReportGeneratorTool
from utils.utils import setup_logging


class FinalReportGeneratorAgent:
    """
    Agente que utiliza o FinalReportGeneratorTool para criar o relatório final
    e retorna o resultado de forma estruturada.
    """

    def __init__(
        self,
        metadata_file_path,
        periods_file_path,
        metrics_file_path,
        report_file_path,
        last_30_days_plot_file_path,
        last_12_months_plot_file_path,
    ):
        """
        Inicializa o agente e sua ferramenta principal, o FinalReportGeneratorTool.
        """
        setup_logging()
        logging.info("Inicializando o FinalReportGeneratorAgent...")
        self.metadata_file_path = metadata_file_path
        self.periods_file_path = periods_file_path
        self.metrics_file_path = metrics_file_path
        self.report_file_path = report_file_path
        self.last_30_days_plot_file_path = last_30_days_plot_file_path
        self.last_12_months_plot_file_path = last_12_months_plot_file_path
        try:
            self.report_generator_tool = FinalReportGeneratorTool(
                metadata_file_path,
                periods_file_path,
                metrics_file_path,
                report_file_path,
                last_30_days_plot_file_path,
                last_12_months_plot_file_path,
            )
        except ValueError as e:
            logging.error(f"Erro fatal na inicialização do agente: {e}")
            raise

    def run(self) -> dict | None:
        """
        Executa o processo de geração de relatório através da ferramenta e formata a saída.

        Returns:
            dict: Um dicionário com a chave 'final_report_path' e o caminho do relatório gerado.
            None: Retorna None se a geração do relatório falhar.
        """
        logging.info(
            "--- Agente acionado para executar a tarefa de geração de relatório ---"
        )

        report_path = self.report_generator_tool.run_generation_process()

        if report_path:
            logging.info(
                f"Agente concluiu a tarefa com sucesso. Relatório em: {report_path}"
            )
            return {"final_report_file_path": report_path}
        else:
            logging.error("Agente falhou ao executar a tarefa de geração de relatório.")
            return None
