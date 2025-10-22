
# utils/disclaimer_generator.py
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def generate_affiliate_disclaimer(config: Dict[str, Any]) -> str:
    """Генерирует дисклеймер для партнёрских ссылок."""
    disclaimer = "⚠️ Дисклеймер: Этот контент может содержать партнёрские ссылки. "
    disclaimer += "При покупке по этим ссылкам мы можем получить комиссию без дополнительных затрат для вас."
    logger.info("Generated affiliate disclaimer")
    return disclaimer

def generate_sponsorship_disclaimer(sponsor_name: str, config: Dict[str, Any]) -> str:
    """Генерирует дисклеймер для спонсорского контента."""
    template = config.get('monetization', {}).get('sponsorship', {}).get('disclaimer_template', 
                                                                          "Контент частично спонсирован [имя_партнёра].")
    disclaimer = template.replace('[имя_партнёра]', sponsor_name)
    logger.info(f"Generated sponsorship disclaimer for {sponsor_name}")
    return disclaimer

def generate_premium_disclaimer(config: Dict[str, Any]) -> str:
    """Генерирует призыв к действию для премиум-контента."""
    cta = config.get('monetization', {}).get('premium_content', {}).get('call_to_action',
                                                                          "Узнайте больше в премиум-версии.")
    logger.info("Generated premium content disclaimer")
    return cta
