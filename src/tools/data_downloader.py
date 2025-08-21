import os
import json
import requests
import logging
from datetime import date, timedelta, datetime

from utils.utils import setup_logging, load_config


class DataDownloaderTool:
    """
    Classe responsável por baixar os arquivos CSV de SRAG.
    """

    def __init__(self):
        """
        Inicializa o downloader, configura o logging e carrega as configurações.
        """
        setup_logging()
        try:
            config = load_config()
            self.downloader_cfg = config["downloader_config"]
            self.output_cfg = config["file_output"]
        except (FileNotFoundError, KeyError) as e:
            logging.error(
                f"Falha ao inicializar o DataDownloader devido a erro de configuração. Detalhes: {e}"
            )
            raise ValueError("Erro de configuração impede a continuação.") from e

    def _generate_download_links(self) -> list:
        links = []
        today = date.today()
        days_to_check = self.downloader_cfg["days_to_try"]
        base_url = self.downloader_cfg["base_url"]

        logging.info(
            f"Gerando links para os últimos {days_to_check} dias a partir de {today.strftime('%d/%m/%Y')}..."
        )

        for i in range(days_to_check):
            current_date = today - timedelta(days=i)
            date_str = current_date.strftime("%d-%m-%Y")
            year_str = current_date.strftime("%Y")
            year_short = current_date.strftime("%y")

            filename = f"INFLUD{year_short}-{date_str}.csv"
            url = base_url.format(year=year_str, filename=filename)

            links.append({"date": current_date, "filename": filename, "url": url})

        return links

    def _download_and_save_file(self, url: str, save_path: str) -> bool:
        try:
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return True
            return False
        except requests.exceptions.RequestException as e:
            logging.warning(f"Ocorreu um erro de conexão ao tentar acessar {url}: {e}")
            return False

    def _save_metadata(self, dest_folder: str, file_date: date):
        """
        Salva um arquivo metadata.json com a data/hora do download e a data do arquivo baixado.
        """
        try:
            update_timestamp = datetime.now()
            formatted_timestamp = update_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            file_date_str = file_date.strftime("%d-%m-%Y")

            metadata = {
                "update_date": formatted_timestamp,
                "date_last_file": file_date_str,
            }

            metadata_path = os.path.join(dest_folder, "metadata.json")

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)

            logging.info(f"Metadados salvos com sucesso em: {metadata_path}")
            return metadata_path

        except (IOError, OSError) as e:
            logging.error(f"Falha ao salvar o arquivo de metadados: {e}")
            return None

    def run_download_process(self):
        """
        Função que orquestra o processo de download.
        Renomeada de 'run' para 'run_download_process' para evitar confusão.
        Retorna o caminho do arquivo em caso de sucesso, ou None em caso de falha.
        """
        logging.info(
            "--- Iniciando processo de download do arquivo SRAG (via Tool) ---"
        )

        dest_folder = self.output_cfg["destination_folder"]
        os.makedirs(dest_folder, exist_ok=True)
        full_save_path = os.path.join(
            dest_folder, self.output_cfg["destination_filename"]
        )

        links_to_try = self._generate_download_links()

        failed_attempts = []

        for link_info in links_to_try:
            date_str = link_info["date"].strftime("%d/%m/%Y")
            logging.info(f"Tentando baixar o arquivo para o dia {date_str}...")
            logging.info(f"   -> URL: {link_info['url']}")

            if self._download_and_save_file(link_info["url"], full_save_path):
                logging.info("=" * 50)
                logging.info(f"SUCESSO: Download concluído para o dia {date_str}.")
                logging.info(f"Arquivo salvo como: {full_save_path}")

                metadata_path = self._save_metadata(dest_folder, link_info["date"])

                logging.info("=" * 50)
                return {
                    "downloaded_file_path": full_save_path,
                    "metadata_file_path": metadata_path,
                }
            else:
                logging.warning(
                    f"Falha ao baixar o arquivo '{link_info['filename']}'. Tentando dia anterior."
                )
                failed_attempts.append(link_info["filename"])

        logging.error("=" * 60)
        logging.error(
            f"FALHA: Não foi possível baixar o arquivo após {self.downloader_cfg['days_to_try']} tentativas."
        )
        logging.error(
            "Os seguintes nomes de arquivo não foram encontrados ou geraram erro:"
        )
        for filename in failed_attempts:
            logging.error(f"   - {filename}")
        logging.error("=" * 60)
        return None
