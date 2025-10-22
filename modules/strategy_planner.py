
# modules/strategy_planner.py
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

def determine_actions_for_strategy(strategy: str, config: Dict[str, Any]) -> List[str]:
    """
    Определяет действия монетизации на основе выбранной стратегии.
    
    Args:
        strategy: Стратегия монетизации ('full', 'partial', 'masked', 'hidden')
        config: Конфигурация монетизации
    
    Returns:
        Список действий для выполнения
    """
    actions = []
    monetization = config.get('monetization', {})
    methods = monetization.get('methods', [])
    
    if strategy == 'full':
        # Полная монетизация: все доступные методы
        logger.info("Strategy: FULL - applying all monetization methods")
        if 'affiliate_links' in methods and monetization.get('affiliate_links', {}).get('enabled'):
            actions.append('inject_affiliate_links')
            actions.append('add_affiliate_disclaimer')
        if 'sponsorship' in methods and monetization.get('sponsorship', {}).get('enabled'):
            actions.append('inject_sponsorship')
            actions.append('add_sponsorship_disclaimer')
        if 'premium_content' in methods and monetization.get('premium_content', {}).get('enabled'):
            actions.append('add_premium_cta')
    
    elif strategy == 'partial':
        # Частичная монетизация: выборочные методы
        logger.info("Strategy: PARTIAL - applying selected monetization methods")
        if 'affiliate_links' in methods and monetization.get('affiliate_links', {}).get('enabled'):
            actions.append('inject_affiliate_links')
            actions.append('add_affiliate_disclaimer')
    
    elif strategy == 'masked':
        # Замаскированная монетизация: ссылки без явных дисклеймеров
        logger.info("Strategy: MASKED - applying subtle monetization")
        if 'affiliate_links' in methods and monetization.get('affiliate_links', {}).get('enabled'):
            actions.append('inject_affiliate_links')
        if 'premium_content' in methods and monetization.get('premium_content', {}).get('enabled'):
            actions.append('add_premium_cta')
    
    elif strategy == 'hidden':
        # Скрытая монетизация: минимальное вмешательство
        logger.info("Strategy: HIDDEN - minimal monetization")
        # Можно добавить только незаметные элементы
        pass
    
    logger.info(f"Determined actions: {actions}")
    return actions
