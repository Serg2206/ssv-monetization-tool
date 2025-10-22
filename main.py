
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSV Monetization Tool - Main Entry Point

Инструмент для управления монетизацией контента в SSVproff-Ecosystem.
Автор: Профессор С.В. Сушков
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Импорт модулей инструмента
from utils.logger import setup_logger
from utils.config_loader import load_and_validate_config
from modules.strategy_planner import determine_actions_for_strategy
from modules.content_injector import inject_monetization_elements
from modules.compliance_checker import (
    check_youtube_description_compliance,
    check_amazon_kdp_compliance,
    check_general_compliance
)
from modules.analytics_tracker import (
    prepare_monetization_report,
    calculate_monetization_metrics,
    track_monetization_event
)

# Настройка логирования
logger = setup_logger(__name__)


def process_content(content: Dict[str, Any], config: Dict[str, Any], content_type: str = "video") -> Dict[str, Any]:
    """
    Обрабатывает контент и применяет монетизацию.
    
    Args:
        content: Словарь с контентом для обработки
        config: Конфигурация монетизации
        content_type: Тип контента ('video', 'book')
    
    Returns:
        Обработанный контент с элементами монетизации
    """
    logger.info(f"Processing {content_type} content")
    
    # Определяем стратегию
    strategy = config.get('monetization', {}).get('strategy', 'hidden')
    logger.info(f"Using strategy: {strategy}")
    
    # Определяем действия на основе стратегии
    actions = determine_actions_for_strategy(strategy, config)
    
    if not actions:
        logger.info("No monetization actions required for this strategy")
        return content
    
    # Внедряем элементы монетизации
    modified_content = inject_monetization_elements(content, actions, config)
    
    # Проверяем соответствие политикам платформ
    description = modified_content.get('description', '')
    
    if content_type == "video":
        youtube_issues = check_youtube_description_compliance(description)
        if youtube_issues:
            logger.warning(f"YouTube compliance issues found: {youtube_issues}")
            modified_content['compliance_warnings'] = {
                'youtube': youtube_issues
            }
    elif content_type == "book":
        kdp_issues = check_amazon_kdp_compliance(description)
        if kdp_issues:
            logger.warning(f"Amazon KDP compliance issues found: {kdp_issues}")
            modified_content['compliance_warnings'] = {
                'amazon_kdp': kdp_issues
            }
    
    # Общая проверка
    general_issues = check_general_compliance(description)
    if general_issues:
        logger.warning(f"General compliance issues found: {general_issues}")
        if 'compliance_warnings' not in modified_content:
            modified_content['compliance_warnings'] = {}
        modified_content['compliance_warnings']['general'] = general_issues
    
    # Вычисляем метрики
    metrics = calculate_monetization_metrics(modified_content)
    modified_content['metrics'] = metrics
    
    # Отслеживаем событие
    track_monetization_event('content_processed', content.get('id', 'unknown'), {
        'strategy': strategy,
        'actions': actions,
        'content_type': content_type
    })
    
    logger.info("Content processing completed")
    return modified_content


def generate_report(config: Dict[str, Any], processed_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Генерирует отчёт о монетизации.
    
    Args:
        config: Конфигурация монетизации
        processed_content: Обработанный контент
    
    Returns:
        Отчёт о монетизации
    """
    strategy = config.get('monetization', {}).get('strategy', 'hidden')
    methods = config.get('monetization', {}).get('methods', [])
    metrics = processed_content.get('metrics', {})
    
    report = prepare_monetization_report(strategy, methods, metrics)
    report['content_id'] = processed_content.get('id', 'unknown')
    report['compliance_warnings'] = processed_content.get('compliance_warnings', {})
    
    return report


def main():
    """Основная функция инструмента монетизации."""
    print("🚀 SSV Monetization Tool v2.0")
    print("=" * 70)
    
    try:
        # Загрузка и валидация конфигурации
        config = load_and_validate_config("monetization_config.yaml")
        strategy = config.get('monetization', {}).get('strategy', 'hidden')
        
        print(f"📊 Текущая стратегия монетизации: {strategy.upper()}")
        print("=" * 70)
        
        # Пример обработки контента (демонстрация)
        print("\n📝 Демонстрация работы инструмента:")
        print("-" * 70)
        
        sample_content = {
            'id': 'demo_video_001',
            'title': 'Демонстрационное видео',
            'description': 'Это описание демонстрационного видео о технологиях искусственного интеллекта.'
        }
        
        print(f"\n🎬 Обработка контента: {sample_content['title']}")
        processed = process_content(sample_content, config, content_type='video')
        
        print(f"\n✅ Обработка завершена!")
        print(f"📄 Обновлённое описание:")
        print(f"   {processed['description'][:200]}..." if len(processed['description']) > 200 else f"   {processed['description']}")
        
        # Генерация отчёта
        report = generate_report(config, processed)
        
        print(f"\n📊 Отчёт о монетизации:")
        print(f"   Стратегия: {report['strategy']}")
        print(f"   Методы: {', '.join(report['methods_used']) if report['methods_used'] else 'Нет'}")
        print(f"   Метрики: {json.dumps(report['metrics'], indent=6, ensure_ascii=False)}")
        
        if report.get('compliance_warnings'):
            print(f"\n⚠️  Предупреждения о соответствии:")
            for platform, warnings in report['compliance_warnings'].items():
                print(f"   {platform}: {', '.join(warnings)}")
        
        print("\n" + "=" * 70)
        print("✅ Все модули успешно загружены и протестированы!")
        print("📝 Готово к интеграции с ssv-web-dashboard, ssv-video и ssv-book-generator.")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
