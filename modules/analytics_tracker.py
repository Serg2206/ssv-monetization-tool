
# modules/analytics_tracker.py
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

def generate_unique_affiliate_link(base_link: str, campaign_id: str, content_id: str) -> str:
    """Генерирует уникальную партнёрскую ссылку с UTM-метками."""
    # Реализация генерации ссылки с параметрами
    unique_link = f"{base_link}?utm_source=ssvproff&utm_campaign={campaign_id}&utm_content={content_id}"
    logger.info(f"Generated unique link: {unique_link}")
    return unique_link

def prepare_monetization_report(strategy: str, methods: List[str], metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Подготавливает отчёт о монетизации."""
    # Реализация подготовки отчёта
    report = {
        "strategy": strategy,
        "methods_used": methods,
        "metrics": metrics,
        "generated_at": datetime.now().isoformat(),
        "status": "success"
    }
    logger.info("Monetization report prepared")
    logger.info(f"Report summary: Strategy={strategy}, Methods={len(methods)}")
    return report

def track_monetization_event(event_type: str, content_id: str, metadata: Dict[str, Any] = None) -> None:
    """Отслеживает события монетизации для аналитики."""
    event = {
        "event_type": event_type,
        "content_id": content_id,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    logger.info(f"Tracked event: {event_type} for content {content_id}")
    # В будущем можно добавить сохранение в базу данных или отправку в аналитическую систему
    
def calculate_monetization_metrics(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """Вычисляет метрики эффективности монетизации."""
    metrics = {
        "total_affiliate_links": 0,
        "total_disclaimers": 0,
        "total_cta": 0,
        "content_length": len(content_data.get('description', '')),
        "monetization_density": 0.0  # Отношение элементов монетизации к длине контента
    }
    
    description = content_data.get('description', '')
    
    # Подсчёт партнёрских ссылок
    metrics["total_affiliate_links"] = description.count('http')
    
    # Подсчёт дисклеймеров
    if 'дисклеймер' in description.lower() or 'disclaimer' in description.lower():
        metrics["total_disclaimers"] = 1
    
    # Подсчёт призывов к действию
    if 'узнайте больше' in description.lower() or 'премиум' in description.lower():
        metrics["total_cta"] = 1
    
    # Вычисление плотности монетизации
    if metrics["content_length"] > 0:
        total_elements = metrics["total_affiliate_links"] + metrics["total_disclaimers"] + metrics["total_cta"]
        metrics["monetization_density"] = total_elements / (metrics["content_length"] / 1000.0)
    
    logger.info(f"Calculated monetization metrics: {metrics}")
    return metrics
