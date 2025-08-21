import logging
from agents.data_downloader import DataDownloaderAgent
from agents.data_preprocessor import DataPreprocessorAgent
from agents.metrics_calculator import MetricsCalculatorAgent
from agents.visualizations import VisualizationsAgent
from agents.news_collector import NewsCollectorAgent
from agents.report_generator import ReportGeneratorAgent
from agents.final_report_generator import FinalReportGeneratorAgent


def main():
    """
    Ponto de entrada principal da aplicação.
    Executa todo o pipeline de dados, desde o download até a geração do relatório.
    """
    try:
        # Etapa 1: Download do arquivo
        downloader = DataDownloaderAgent()
        result = downloader.run()
        downloaded_file_path = result["downloaded_file_path"]
        metadata_file_path = result["metadata_file_path"]
        print(downloaded_file_path)
        print(metadata_file_path)

        # Etapa 2: Pré-processamento do arquivo baixado
        preprocessor = DataPreprocessorAgent(downloaded_file_path=downloaded_file_path)
        result = preprocessor.run()
        processed_data_file_path = result["processed_data_file_path"]
        print(processed_data_file_path)

        # Etapa 3: Cálculo e salvamento das métricas
        calculator = MetricsCalculatorAgent(
            processed_data_file_path=processed_data_file_path
        )
        result = calculator.run()
        periods_file_path = result["periods_file_path"]
        metrics_file_path = result["metrics_file_path"]
        print(periods_file_path)
        print(metrics_file_path)

        # Etapa 4: Geração das visualizações (gráficos e JSONs)
        visualizer = VisualizationsAgent(
            processed_data_file_path=processed_data_file_path
        )
        result = visualizer.run()
        last_30_days_json_file_path = result["last_30_days_json_file_path"]
        last_30_days_plot_file_path = result["last_30_days_plot_file_path"]
        last_12_months_json_file_path = result["last_12_months_json_file_path"]
        last_12_months_plot_file_path = result["last_12_months_plot_file_path"]
        print(last_30_days_json_file_path)
        print(last_30_days_plot_file_path)
        print(last_12_months_json_file_path)
        print(last_12_months_plot_file_path)

        # Etapa 5: Coleta de notícias recentes sobre o tema
        news_collector = NewsCollectorAgent()
        result = news_collector.run()
        news_file_path = result["news_file_path"]
        print(news_file_path)

        # Etapa 6: Geração do relatório analítico com a IA
        report_generator = ReportGeneratorAgent(
            metrics_file_path=metrics_file_path,
            last_30_days_json_file_path=last_30_days_json_file_path,
            last_12_months_json_file_path=last_12_months_json_file_path,
            news_file_path=news_file_path,
        )
        result = report_generator.run()
        report_file_path = result["report_file_path"]
        print(report_file_path)

        # Etapa 7: Geração do arquivo HTML final com todos os dados
        final_report = FinalReportGeneratorAgent(
            metadata_file_path=metadata_file_path,
            periods_file_path=periods_file_path,
            metrics_file_path=metrics_file_path,
            report_file_path=report_file_path,
            last_30_days_plot_file_path=last_30_days_plot_file_path,
            last_12_months_plot_file_path=last_12_months_plot_file_path,
        )
        result = final_report.run()
        final_report_file_path = result["final_report_file_path"]
        print(final_report_file_path)

    except ValueError as e:
        logging.error(f"A aplicação não pôde ser executada. Motivo: {e}")
    except Exception as e:
        logging.error(
            f"Ocorreu um erro inesperado durante a execução: {e}", exc_info=True
        )


if __name__ == "__main__":
    main()
