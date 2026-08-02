
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Client library for SSV Monetization Tool API.

Provides easy integration with ssv-web-dashboard and other tools.
"""

import requests
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class MonetizationClient:
    """
    Клиент для взаимодействия с SSV Monetization Tool API.
    
    Example:
        ```python
        client = MonetizationClient(base_url="http://localhost:8000")
        
        result = client.monetize_content(
            content={
                'id': 'video_001',
                'title': 'Техника операции',
                'description': 'Описание...'
            },
            strategy='masked'
        )
        
        print(result['result']['description'])
        ```
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Инициализация клиента.
        
        Args:
            base_url: Базовый URL API сервера
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Проверка состояния API сервера.
        
        Returns:
            Словарь со статусом сервера
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Health check failed: {e}")
            raise
    
    def monetize_content(
        self,
        content: Dict[str, Any],
        strategy: Optional[str] = None,
        methods: Optional[List[str]] = None,
        content_type: str = "video"
    ) -> Dict[str, Any]:
        """
        Применяет монетизацию к контенту.

        Args:
            content: Словарь с контентом (id, title, description)
            strategy: Стратегия монетизации (опционально)
            methods: Список методов монетизации (опционально)
            content_type: Тип контента ('video' или 'book')

        Returns:
            Словарь с результатом монетизации

        Raises:
            requests.RequestException: При ошибке запроса
        """
        try:
            payload = {
                "content": content,
                "strategy": strategy,
                "methods": methods,
                "content_type": content_type
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/monetize",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to monetize content: {e}")
            raise

    def monetize_book(
        self,
        content: Dict[str, Any],
        strategy: Optional[str] = None,
        methods: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Применяет монетизацию к книге/главе с проверкой соответствия Amazon KDP.

        Args:
            content: Словарь с контентом книги (id, title, description)
            strategy: Стратегия монетизации (опционально)
            methods: Список методов монетизации (опционально)

        Returns:
            Словарь с результатом монетизации
        """
        return self.monetize_content(content, strategy=strategy, methods=methods, content_type="book")

    def monetize_book_batch(
        self,
        items: List[Dict[str, Any]],
        strategy: Optional[str] = None,
        methods: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Применяет монетизацию к списку глав книги за один запрос.

        Args:
            items: Список словарей с контентом (id, title, description)
            strategy: Стратегия монетизации (опционально)
            methods: Список методов монетизации (опционально)

        Returns:
            Словарь с результатами монетизации для каждой главы

        Raises:
            requests.RequestException: При ошибке запроса
        """
        try:
            payload = {
                "items": items,
                "strategy": strategy,
                "methods": methods,
                "content_type": "book"
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/monetize/batch",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to batch monetize book content: {e}")
            raise
    
    def check_youtube_compliance(self, description: str) -> Dict[str, Any]:
        """
        Проверяет описание на соответствие политикам YouTube.
        
        Args:
            description: Текст описания
        
        Returns:
            Словарь с результатом проверки
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/compliance/youtube",
                params={"description": description}
            )
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Failed to check YouTube compliance: {e}")
            raise
    
    def check_amazon_kdp_compliance(self, description: str) -> Dict[str, Any]:
        """
        Проверяет описание на соответствие политикам Amazon KDP.
        
        Args:
            description: Текст описания
        
        Returns:
            Словарь с результатом проверки
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/compliance/amazon-kdp",
                params={"description": description}
            )
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Failed to check Amazon KDP compliance: {e}")
            raise
    
    def get_strategies(self) -> List[Dict[str, str]]:
        """
        Получает список доступных стратегий монетизации.
        
        Returns:
            Список стратегий с описаниями
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v1/strategies")
            response.raise_for_status()
            return response.json()['strategies']
        
        except requests.RequestException as e:
            logger.error(f"Failed to get strategies: {e}")
            raise
    
    def generate_unique_link(
        self,
        base_url: str,
        content_id: str,
        source: str,
        medium: str = "description"
    ) -> str:
        """
        Генерирует уникальную партнёрскую ссылку с UTM-метками.
        
        Args:
            base_url: Базовый URL ссылки
            content_id: Идентификатор контента
            source: Источник трафика
            medium: Тип размещения
        
        Returns:
            Уникальная ссылка с UTM-параметрами
        """
        try:
            payload = {
                "base_url": base_url,
                "content_id": content_id,
                "source": source,
                "medium": medium
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analytics/link",
                json=payload
            )
            response.raise_for_status()
            return response.json()['link']
        
        except requests.RequestException as e:
            logger.error(f"Failed to generate unique link: {e}")
            raise


# Пример использования
if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Создание клиента
    client = MonetizationClient(base_url="http://localhost:8000")
    
    # Проверка состояния сервера
    try:
        health = client.health_check()
        print(f"✅ Сервер работает: {health}")
    except Exception as e:
        print(f"❌ Ошибка подключения к серверу: {e}")
        exit(1)
    
    # Пример контента
    content = {
        'id': 'video_demo_001',
        'title': 'Демонстрационное видео',
        'description': 'В этом видео рассматриваются хирургические инструменты и медицинские книги.'
    }
    
    # Применение монетизации
    print("\n📝 Применение монетизации...")
    result = client.monetize_content(content, strategy='masked')
    
    print(f"\n✅ Результат:")
    print(f"   ID: {result['result']['id']}")
    print(f"   Title: {result['result']['title']}")
    print(f"   Description: {result['result']['description'][:100]}...")
    print(f"   Metrics: {result['metrics']}")
    
    # Проверка соответствия
    print("\n🔍 Проверка соответствия YouTube...")
    compliance = client.check_youtube_compliance(result['result']['description'])
    print(f"   Соответствует: {compliance['compliant']}")
    if not compliance['compliant']:
        print(f"   Проблемы: {compliance['issues']}")
    
    # Получение списка стратегий
    print("\n📊 Доступные стратегии:")
    strategies = client.get_strategies()
    for strategy in strategies:
        print(f"   - {strategy['display_name']}: {strategy['description']}")
    
    # Генерация уникальной ссылки
    print("\n🔗 Генерация уникальной ссылки...")
    link = client.generate_unique_link(
        base_url="https://amazon.com/product",
        content_id="video_demo_001",
        source="youtube",
        medium="description"
    )
    print(f"   Ссылка: {link}")
