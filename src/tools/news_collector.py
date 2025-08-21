import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper

from utils.utils import setup_logging, load_config


class NewsCollectorTool:
    """
    Ferramenta responsável por buscar notícias relacionadas a temas de saúde
    e salvá-las em um arquivo JSON. Contém a lógica de implementação.
    """

    def __init__(self):
        """
        Inicializa o coletor de notícias, configura o logging e carrega
        as configurações a partir do arquivo parameters.yaml.
        A chave da API SERPER é carregada a partir do arquivo .env.
        """
        setup_logging()
        load_dotenv()

        if not os.getenv("SERPER_API_KEY"):
            logging.error("A variável de ambiente SERPER_API_KEY não foi encontrada.")
            raise ValueError(
                "SERPER_API_KEY não definida no arquivo .env ou no ambiente."
            )

        try:
            config = load_config()
            self.news_cfg = config["news_config"]

        except (FileNotFoundError, KeyError) as e:
            logging.error(
                f"Falha ao inicializar o NewsCollectorTool devido a erro de configuração. Detalhes: {e}"
            )
            raise ValueError("Erro de configuração impede a continuação.") from e

    def _search_news(self) -> dict:
        """
        Executa a busca de notícias utilizando a API do Google Serper.
        (Método privado)

        Returns:
            dict: O dicionário de resultados retornado pela API.
        """
        try:
            logging.info("Iniciando a busca por notícias (via Tool)...")
            search_params = self.news_cfg["search_parameters"]

            search = GoogleSerperAPIWrapper(
                type=search_params["type"],
                tbs=search_params["time_period"],
                gl=search_params["country_code"],
                hl=search_params["language_code"],
                num=search_params["num_results"],
            )

            search_terms = self.news_cfg["search_terms"]
            logging.info(f"Buscando com os termos: {search_terms}")

            results = search.results(query=search_terms)
            return results

        except Exception as e:
            logging.error(f"Ocorreu um erro durante a chamada da API de notícias: {e}")
            return {}

    def _format_results(self, results: dict) -> list:
        """
        Formata a lista de notícias brutas para o formato desejado.
        (Método privado)

        Args:
            results (dict): O dicionário de resultados da API.

        Returns:
            list: Uma lista de dicionários, onde cada dicionário representa uma notícia formatada.
        """
        formatted_news = []
        if "news" in results and results["news"]:
            for item in results["news"]:
                noticia = {
                    "titulo": item.get("title", "N/A"),
                    "conteudo": item.get("snippet", "N/A"),
                    "data": item.get("date", "N/A"),
                    "fonte": item.get("source", "N/A"),
                }
                formatted_news.append(noticia)
        else:
            logging.warning("Nenhuma notícia encontrada para os termos de busca.")

        return formatted_news

    def _save_results(self, formatted_news: list) -> str | None:
        """
        Salva a lista de notícias formatadas em um arquivo JSON.
        (Método privado)

        Args:
            formatted_news (list): A lista de notícias a ser salva.

        Returns:
            str: O caminho do arquivo salvo em caso de sucesso.
            None: Em caso de falha.
        """
        output_dir = self.news_cfg["output_dir"]
        output_file = os.path.join(output_dir, self.news_cfg["output_filename"])

        try:
            os.makedirs(output_dir, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(formatted_news, f, ensure_ascii=False, indent=4)

            logging.info(f"Notícias salvas com sucesso em: {output_file}")
            return output_file

        except (IOError, OSError) as e:
            logging.error(f"Falha ao salvar o arquivo de notícias: {e}")
            return None

    def _save_metadata(self):
        """
        Salva um arquivo metadata.json com a data e hora da atualização.
        (Método privado)
        """
        dest_folder = self.news_cfg["output_dir"]
        metadata_path = os.path.join(dest_folder, "metadata.json")

        try:
            update_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            metadata = {"update_date": update_timestamp}

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)

            logging.info(f"Metadados salvos com sucesso em: {metadata_path}")

        except (IOError, OSError) as e:
            logging.error(f"Falha ao salvar o arquivo de metadados: {e}")

    def run_collection_process(self) -> str | None:
        """
        Função que orquestra o processo de coleta e salvamento de notícias.
        Retorna o caminho do arquivo de notícias em caso de sucesso, ou None em caso de falha.
        """
        logging.info("--- Iniciando processo de coleta de notícias (via Tool) ---")

        raw_results = self._search_news()

        if not raw_results:
            logging.error("Não foi possível obter resultados da busca de notícias.")
            return None

        formatted_news = self._format_results(raw_results)

        if not formatted_news:
            logging.warning("A busca não retornou notícias para serem salvas.")
            return None

        result = self._save_results(formatted_news)
        if result:
            self._save_metadata()
            logging.info(
                "--- Processo de coleta de notícias finalizado com sucesso (via Tool) ---"
            )
            return result
        else:
            logging.error(
                "--- Falha no processo de coleta de notícias ao salvar o arquivo ---"
            )
            return None
