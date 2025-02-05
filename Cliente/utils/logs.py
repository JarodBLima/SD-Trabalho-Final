import logging
import os

def setup_logger(name, log_file, level=logging.INFO):
    """Configura um logger."""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Cria o diretório de logs se não existir
    logs_dir = os.path.dirname(log_file)
    if logs_dir and not os.path.exists(logs_dir):  # Verifica se logs_dir não é vazio
        os.makedirs(logs_dir)

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
