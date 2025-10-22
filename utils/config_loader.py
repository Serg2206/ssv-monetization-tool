
# utils/config_loader.py
import yaml
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_and_validate_config(config_path: str) -> Dict[str, Any]:
    """Загружает и валидирует конфигурацию монетизации."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Простая валидация (можно расширить)
        required_keys = ['monetization']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required key '{key}' in config.")

        monetization = config['monetization']
        if 'strategy' not in monetization or monetization['strategy'] not in ['full', 'partial', 'masked', 'hidden']:
            raise ValueError("Invalid or missing 'strategy' in monetization config.")

        logger.info(f"Configuration loaded and validated from {config_path}")
        return config

    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config: {e}")
        raise
    except ValueError as e:
        logger.error(f"Config validation error: {e}")
        raise
