from graph import FinancialReportWorkflow
from utils.utils import setup_logging

import logging

setup_logging()

if __name__ == "__main__":
    logging.info("Iniciando o processo de geração de relatório...")

    workflow_manager = FinancialReportWorkflow()

    result_state = workflow_manager.run()

    logging.info("\n--- Processo Finalizado ---")
    logging.info("Estado final do workflow:")
    for key, value in result_state.items():
        logging.info(f"  - {key}: {value}")
    logging.info(
        f"\nRelatório final disponível em: {result_state.get('final_report_file_path', 'N/A')}"
    )
