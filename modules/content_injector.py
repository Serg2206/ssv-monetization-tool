
# modules/content_injector.py
import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def inject_monetization_elements(
    content: Dict[str, Any],
    actions: List[str],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Внедряет элементы монетизации в контент.
    
    Args:
        content: Словарь с контентом (description, chapters, etc.)
        actions: Список действий для выполнения
        config: Конфигурация монетизации
    
    Returns:
        Обновлённый контент с элементами монетизации
    """
    logger.info("Starting content injection")
    modified_content = content.copy()
    
    if 'inject_affiliate_links' in actions:
        modified_content = _inject_affiliate_links(modified_content, config)
    
    if 'add_affiliate_disclaimer' in actions:
        modified_content = _inject_disclaimer_to_description(
            modified_content, 
            _generate_affiliate_disclaimer(config)
        )
    
    if 'inject_sponsorship' in actions:
        modified_content = _inject_sponsorship(modified_content, config)
    
    if 'add_sponsorship_disclaimer' in actions:
        sponsor_name = config.get('monetization', {}).get('sponsorship', {}).get('sponsor_name', 'Партнёр')
        modified_content = _inject_disclaimer_to_description(
            modified_content,
            _generate_sponsorship_disclaimer(sponsor_name, config)
        )
    
    if 'add_premium_cta' in actions:
        modified_content = _inject_premium_cta(modified_content, config)
    
    logger.info("Content injection completed")
    return modified_content

def _inject_affiliate_links(content: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Внедряет партнёрские ссылки в описание."""
    logger.info("Injecting affiliate links")
    
    description = content.get('description', '')
    affiliate_config = config.get('monetization', {}).get('affiliate_links', {})
    default_links = affiliate_config.get('default_links', {})
    
    for keyword, affiliate_url in default_links.items():
        # Простая замена ключевых слов на ссылки
        pattern = rf'\b{re.escape(keyword)}\b'
        replacement = f"{keyword} ({affiliate_url})"
        description = re.sub(pattern, replacement, description, count=1, flags=re.IGNORECASE)
        logger.debug(f"Replaced keyword '{keyword}' with affiliate link")
    
    content['description'] = description
    return content

def _inject_disclaimer_to_description(content: Dict[str, Any], disclaimer: str) -> Dict[str, Any]:
    """Добавляет дисклеймер в описание."""
    logger.info("Injecting disclaimer to description")
    
    description = content.get('description', '')
    if description:
        content['description'] = f"{description}\n\n{disclaimer}"
    else:
        content['description'] = disclaimer
    
    return content

def _inject_sponsorship(content: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Внедряет спонсорский контент."""
    logger.info("Injecting sponsorship content")
    
    sponsorship_config = config.get('monetization', {}).get('sponsorship', {})
    sponsor_mention = f"При поддержке: {sponsorship_config.get('sponsor_name', 'Наш спонсор')}"
    
    description = content.get('description', '')
    content['description'] = f"{sponsor_mention}\n\n{description}"
    
    return content

def _inject_premium_cta(content: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Добавляет призыв к действию для премиум-контента."""
    logger.info("Injecting premium CTA")
    
    cta = config.get('monetization', {}).get('premium_content', {}).get('call_to_action',
                                                                          "Узнайте больше в премиум-версии.")
    
    description = content.get('description', '')
    content['description'] = f"{description}\n\n{cta}"
    
    return content

def _generate_affiliate_disclaimer(config: Dict[str, Any]) -> str:
    """Генерирует дисклеймер для партнёрских ссылок."""
    return "⚠️ Дисклеймер: Этот контент может содержать партнёрские ссылки."

def _generate_sponsorship_disclaimer(sponsor_name: str, config: Dict[str, Any]) -> str:
    """Генерирует дисклеймер для спонсорского контента."""
    template = config.get('monetization', {}).get('sponsorship', {}).get('disclaimer_template',
                                                                          "Контент частично спонсирован [имя_партнёра].")
    return template.replace('[имя_партнёра]', sponsor_name)
