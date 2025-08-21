import os
import yaml
import logging


def setup_logging():
    """Configura o sistema de logging para salvar em arquivo e mostrar no console."""
    log_directory = "logs"
    log_filepath = os.path.join(log_directory, "logs.log")

    os.makedirs(log_directory, exist_ok=True)

    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_filepath, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
    logging.info("Logger configurado com sucesso.")


def load_config(config_path: str = "conf/parameters.yaml") -> dict:
    """
    Carrega as configurações de um arquivo YAML.
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        logging.error(f"Arquivo de configuração não encontrado em '{config_path}'")
        raise
    except Exception as e:
        logging.exception(f"Falha ao ler ou processar o arquivo de configuração: {e}")
        raise
