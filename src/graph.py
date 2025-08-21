from utils.utils import setup_logging
from langgraph.graph import StateGraph, END
import logging
from typing import Dict

from agents.data_downloader import DataDownloaderAgent
from agents.data_preprocessor import DataPreprocessorAgent
from agents.metrics_calculator import MetricsCalculatorAgent
from agents.visualizations import VisualizationsAgent
from agents.news_collector import NewsCollectorAgent
from agents.report_generator import ReportGeneratorAgent
from agents.final_report_generator import FinalReportGeneratorAgent
from typing import TypedDict
from typing import Optional


class AgentState(TypedDict):
    downloaded_file_path: Optional[str]
    metadata_file_path: Optional[str]
    processed_data_file_path: Optional[str]
    metrics_file_path: Optional[str]
    periods_file_path: Optional[str]
    last_30_days_json_file_path: Optional[str]
    last_12_months_json_file_path: Optional[str]
    last_30_days_plot_file_path: Optional[str]
    last_12_months_plot_file_path: Optional[str]
    news_file_path: Optional[str]
    report_file_path: Optional[str]
    final_report_file_path: Optional[str]


class FinancialReportWorkflow:
    """
    Orquestra um fluxo de trabalho de ponta a ponta para gerar relatórios financeiros.

    Esta classe encapsula a lógica de um grafo de agentes, onde cada nó executa
    uma tarefa específica (download, processamento, análise, etc.). A classe é
    responsável por construir o grafo, definir a sequência de execução e
    invocar o processo completo.

    O estado do workflow é um dicionário que é passado entre os nós,
    acumulando os resultados de cada etapa (ex: caminhos de arquivos gerados).
    """

    def __init__(self):
        """
        Inicializa o workflow, configurando o logging e construindo o grafo compilado.
        """
        setup_logging()
        logging.info("Inicializando o FinancialReportWorkflow.")
        self.graph = self._build_graph()

    def _build_graph(self):
        """
        Constrói o grafo de execução definindo todos os nós e suas conexões (arestas).

        Retorna:
            graph: O grafo compilado e pronto para ser executado.
        """
        workflow = StateGraph(AgentState)

        logging.info("Adicionando nós ao grafo...")
        workflow.add_node("data_downloader", self._node_data_downloader)
        workflow.add_node("data_preprocessor", self._node_data_preprocessor)
        workflow.add_node("metrics_calculator", self._node_metrics_calculator)
        workflow.add_node("visualizations", self._node_visualizations)
        workflow.add_node("news_collector", self._node_news_collector)
        workflow.add_node("report_generator", self._node_report_generator)
        workflow.add_node("final_report_generator", self._node_final_report_generator)

        logging.info("Definindo as arestas do grafo...")

        workflow.set_entry_point("data_downloader")

        workflow.add_edge("data_downloader", "data_preprocessor")
        workflow.add_edge("data_preprocessor", "metrics_calculator")
        workflow.add_edge("metrics_calculator", "visualizations")
        workflow.add_edge("visualizations", "news_collector")
        workflow.add_edge("news_collector", "report_generator")
        workflow.add_edge("report_generator", "final_report_generator")

        workflow.add_edge("final_report_generator", END)

        logging.info("Compilando o grafo.")
        return workflow.compile()

    def _node_data_downloader(self, state: Dict) -> Dict:
        """Executa o agente para baixar os dados brutos e metadados."""
        logging.info("Executando nó: DataDownloader")
        downloader = DataDownloaderAgent()
        result = downloader.run()
        state["downloaded_file_path"] = result["downloaded_file_path"]
        state["metadata_file_path"] = result["metadata_file_path"]
        logging.debug(f"Estado após DataDownloader: {state}")
        return state

    def _node_data_preprocessor(self, state: Dict) -> Dict:
        """Executa o agente para limpar e pré-processar os dados baixados."""
        logging.info("Executando nó: DataPreprocessor")
        preprocessor = DataPreprocessorAgent(
            downloaded_file_path=state.get("downloaded_file_path")
        )
        result = preprocessor.run()
        state["processed_data_file_path"] = result["processed_data_file_path"]
        logging.debug(
            f"Arquivo de dados processado: {state.get('processed_data_file_path')}"
        )
        return state

    def _node_metrics_calculator(self, state: Dict) -> Dict:
        """Executa o agente para calcular métricas financeiras a partir dos dados processados."""
        logging.info("Executando nó: MetricsCalculator")
        calculator = MetricsCalculatorAgent(
            processed_data_file_path=state.get("processed_data_file_path")
        )
        result = calculator.run()
        state["periods_file_path"] = result["periods_file_path"]
        state["metrics_file_path"] = result["metrics_file_path"]
        logging.debug("Arquivos de métricas e períodos gerados.")
        return state

    def _node_visualizations(self, state: Dict) -> Dict:
        """Executa o agente para gerar gráficos e dados para visualização."""
        logging.info("Executando nó: Visualizations")
        visualizer = VisualizationsAgent(
            processed_data_file_path=state.get("processed_data_file_path")
        )
        result = visualizer.run()
        state["last_30_days_json_file_path"] = result["last_30_days_json_file_path"]
        state["last_30_days_plot_file_path"] = result["last_30_days_plot_file_path"]
        state["last_12_months_json_file_path"] = result["last_12_months_json_file_path"]
        state["last_12_months_plot_file_path"] = result["last_12_months_plot_file_path"]
        logging.debug("Arquivos de visualização (JSON e plots) gerados.")
        return state

    def _node_news_collector(self, state: Dict) -> Dict:
        """Executa o agente para coletar notícias financeiras relevantes."""
        logging.info("Executando nó: NewsCollector")
        news_collector = NewsCollectorAgent()
        result = news_collector.run()
        state["news_file_path"] = result["news_file_path"]
        logging.debug(f"Arquivo de notícias: {state.get('news_file_path')}")
        return state

    def _node_report_generator(self, state: Dict) -> Dict:
        """Executa o agente para gerar um relatório analítico em texto."""
        logging.info("Executando nó: ReportGenerator")
        report_generator = ReportGeneratorAgent(
            metrics_file_path=state.get("metrics_file_path"),
            last_30_days_json_file_path=state.get("last_30_days_json_file_path"),
            last_12_months_json_file_path=state.get("last_12_months_json_file_path"),
            news_file_path=state.get("news_file_path"),
        )
        result = report_generator.run()
        state["report_file_path"] = result["report_file_path"]
        logging.debug(
            f"Arquivo do relatório analítico: {state.get('report_file_path')}"
        )
        return state

    def _node_final_report_generator(self, state: Dict) -> Dict:
        """Executa o agente para montar o relatório final em formato HTML."""
        logging.info("Executando nó: FinalReportGenerator")
        final_report = FinalReportGeneratorAgent(
            metadata_file_path=state.get("metadata_file_path"),
            periods_file_path=state.get("periods_file_path"),
            metrics_file_path=state.get("metrics_file_path"),
            report_file_path=state.get("report_file_path"),
            last_30_days_plot_file_path=state.get("last_30_days_plot_file_path"),
            last_12_months_plot_file_path=state.get("last_12_months_plot_file_path"),
        )
        result = final_report.run()
        state["final_report_file_path"] = result["final_report_file_path"]
        logging.info(
            f"Relatório final gerado com sucesso: {state.get('final_report_file_path')}"
        )
        return state

    def run(self) -> Dict:
        """
        Executa o fluxo de trabalho completo a partir de um estado inicial vazio.

        Retorna:
            Dict: O estado final contendo os caminhos para todos os artefatos gerados.
        """
        logging.info("Iniciando a execução do workflow completo.")
        initial_state = {}
        final_state = self.graph.invoke(initial_state)
        logging.info("Workflow concluído com sucesso.")
        return final_state
