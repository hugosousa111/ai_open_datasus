import os
import json
import logging
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

from utils.utils import setup_logging, load_config


class ReportGeneratorTool:
    """
    Classe responsável por gerar um relatório analítico utilizando a API da OpenAI,
    com base em dados de métricas, visualizações e notícias.
    """

    def __init__(
        self,
        metrics_file_path,
        last_30_days_json_file_path,
        last_12_months_json_file_path,
        news_file_path,
    ):
        """
        Inicializa o gerador de relatórios, configura o logging, carrega as
        configurações do parameters.yaml e a chave da API OpenAI do .env.
        """
        setup_logging()
        load_dotenv()
        self.metrics_file_path = metrics_file_path
        self.last_30_days_json_file_path = last_30_days_json_file_path
        self.last_12_months_json_file_path = last_12_months_json_file_path
        self.news_file_path = news_file_path
        if not os.getenv("OPENAI_API_KEY"):
            logging.error("A variável de ambiente OPENAI_API_KEY não foi encontrada.")
            raise ValueError(
                "OPENAI_API_KEY não definida no arquivo .env ou no ambiente."
            )

        try:
            config = load_config()
            self.report_cfg = config["report_generator_config"]
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        except (FileNotFoundError, KeyError) as e:
            logging.error(
                f"Falha ao inicializar o ReportGeneratorTool devido a erro de configuração: {e}"
            )
            raise ValueError("Erro de configuração impede a continuação.") from e

    def _load_data_file(self, file_path: str, is_json: bool = False) -> str | None:
        """
        Lê o conteúdo de um arquivo de texto ou JSON e o retorna como uma string.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if is_json:
                    data = json.load(f)
                    return json.dumps(data, indent=2, ensure_ascii=False)
                return f.read()
        except FileNotFoundError:
            logging.error(f"O arquivo '{file_path}' não foi encontrado.")
            return None
        except json.JSONDecodeError:
            logging.error(f"O arquivo '{file_path}' não contém um JSON válido.")
            return None
        except Exception as e:
            logging.error(f"Erro inesperado ao ler o arquivo '{file_path}': {e}")
            return None

    def _build_prompt(self) -> str | None:
        """
        Constrói o prompt final substituindo as marcações no template com os dados
        dos arquivos JSON. (Método privado)
        """
        logging.info("Carregando template do prompt...")
        prompt_template = self._load_data_file(self.report_cfg["prompt_file"])
        if not prompt_template:
            return None

        logging.info("Carregando arquivos de dados para o prompt...")
        metrics_content = self._load_data_file(self.metrics_file_path, is_json=True)
        viz_months_content = self._load_data_file(
            self.last_12_months_json_file_path, is_json=True
        )
        viz_days_content = self._load_data_file(
            self.last_12_months_json_file_path, is_json=True
        )
        news_content = self._load_data_file(self.news_file_path, is_json=True)

        if not all(
            [metrics_content, viz_months_content, viz_days_content, news_content]
        ):
            logging.error(
                "Falha ao carregar um ou mais arquivos de dados. A construção do prompt foi interrompida."
            )
            return None

        logging.info("Montando o prompt final...")
        final_prompt = prompt_template.replace("json_metricas", metrics_content)
        final_prompt = final_prompt.replace("json_grafico_meses", viz_months_content)
        final_prompt = final_prompt.replace("json_grafico_dias", viz_days_content)
        final_prompt = final_prompt.replace("json_noticias", news_content)

        return final_prompt

    def _generate_report(self, final_prompt: str) -> str | None:
        """
        Envia o prompt para a API da OpenAI e retorna o relatório gerado.
        (Método privado)
        """
        logging.info("Enviando requisição para a API da OpenAI...")
        try:
            response = self.client.chat.completions.create(
                model=self.report_cfg["model"],
                messages=[
                    {"role": "system", "content": self.report_cfg["system_prompt"]},
                    {"role": "user", "content": final_prompt},
                ],
                temperature=self.report_cfg["temperature"],
                max_tokens=self.report_cfg["max_tokens"],
            )
            report_content = response.choices[0].message.content
            logging.info("Resposta recebida da OpenAI com sucesso.")
            return report_content

        except Exception as e:
            logging.error(f"Ocorreu um erro ao chamar a API da OpenAI: {e}")
            return None

    def _save_report(self, content: str) -> str | None:
        """
        Salva o conteúdo do relatório em um arquivo de texto.
        (Método privado)

        Returns:
            str | None: O caminho do arquivo salvo em caso de sucesso, None caso contrário.
        """
        output_dir = self.report_cfg["output_dir"]
        output_file = os.path.join(output_dir, self.report_cfg["output_filename"])

        try:
            os.makedirs(output_dir, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            logging.info(f"Relatório salvo com sucesso em: {output_file}")
            return output_file

        except IOError as e:
            logging.error(f"Falha ao salvar o arquivo de relatório: {e}")
            return None

    def _save_metadata(self):
        """
        Salva um arquivo metadata.json com a data e hora da geração do relatório.
        (Método privado)
        """
        dest_folder = self.report_cfg["output_dir"]
        metadata_path = os.path.join(dest_folder, "metadata.json")

        try:
            update_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            metadata = {"update_date": update_timestamp}

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)

            logging.info(
                f"Metadados do relatório salvos com sucesso em: {metadata_path}"
            )

        except (IOError, OSError) as e:
            logging.error(f"Falha ao salvar o arquivo de metadados do relatório: {e}")

    def run_report_process(self) -> str | None:
        """
        Orquestra o processo de geração e salvamento do relatório.
        Retorna o caminho do relatório em caso de sucesso, ou None em caso de falha.
        """
        logging.info("--- Iniciando processo de geração de relatório (via Tool) ---")

        final_prompt = self._build_prompt()

        if final_prompt:
            report_content = self._generate_report(final_prompt)
            if report_content:
                report_path = self._save_report(report_content)
                if report_path:
                    self._save_metadata()
                    logging.info("=" * 50)
                    logging.info("SUCESSO: Geração do relatório concluída.")
                    logging.info(f"Relatório salvo em: {report_path}")
                    logging.info("=" * 50)
                    return report_path

        logging.error("=" * 60)
        logging.error(
            "FALHA: Não foi possível gerar o relatório devido a erros no processo."
        )
        logging.error("=" * 60)
        return None
