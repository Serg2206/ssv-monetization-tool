
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI application for SSV Monetization Tool.

Provides REST API endpoints for integration with ssv-web-dashboard.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Добавление родительской директории в путь для импорта модулей
sys.path.append(str(Path(__file__).parent.parent))

from utils.config_loader import load_and_validate_config
from utils.logger import setup_logger
from modules.strategy_planner import determine_actions_for_strategy
from modules.content_injector import inject_monetization_elements
from modules.compliance_checker import (
    check_youtube_description_compliance,
    check_amazon_kdp_compliance,
    check_general_compliance
)
from modules.analytics_tracker import (
    generate_unique_affiliate_link,
    calculate_monetization_metrics,
    prepare_monetization_report
)

# Настройка логирования
logger = setup_logger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="SSV Monetization Tool API",
    description="REST API for ethical monetization of medical/surgical content",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS для интеграции с веб-панелью
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production следует указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загрузка конфигурации при запуске
try:
    config = load_and_validate_config("monetization_config.yaml")
    logger.info("Configuration loaded successfully")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    config = None


# Pydantic модели для запросов и ответов

class ContentInput(BaseModel):
    """Модель входного контента."""
    id: str = Field(..., description="Unique content identifier")
    title: str = Field(..., description="Content title")
    description: str = Field(..., description="Content description")

class MonetizeRequest(BaseModel):
    """Модель запроса на монетизацию."""
    content: ContentInput
    strategy: Optional[str] = Field(None, description="Monetization strategy (full, partial, masked, hidden)")
    methods: Optional[List[str]] = Field(None, description="List of monetization methods to use")

class MonetizeResponse(BaseModel):
    """Модель ответа на запрос монетизации."""
    success: bool
    result: Dict[str, Any]
    metrics: Optional[Dict[str, Any]] = None
    compliance_warnings: Optional[Dict[str, List[str]]] = None

class ComplianceResponse(BaseModel):
    """Модель ответа проверки соответствия."""
    compliant: bool
    issues: List[str]

class StrategiesResponse(BaseModel):
    """Модель ответа со списком стратегий."""
    strategies: List[Dict[str, str]]

class UniqueLinkRequest(BaseModel):
    """Модель запроса генерации уникальной ссылки."""
    base_url: str
    content_id: str
    source: str
    medium: Optional[str] = "description"

class UniqueLinkResponse(BaseModel):
    """Модель ответа с уникальной ссылкой."""
    link: str


# API Endpoints

@app.get("/")
async def root():
    """Корневой endpoint."""
    return {
        "name": "SSV Monetization Tool API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Проверка состояния API."""
    return {
        "status": "healthy",
        "config_loaded": config is not None
    }

@app.post("/api/v1/monetize", response_model=MonetizeResponse)
async def monetize_content(request: MonetizeRequest):
    """
    Применяет монетизацию к контенту.
    
    Args:
        request: Запрос с контентом и параметрами монетизации
    
    Returns:
        Монетизированный контент с метриками
    """
    try:
        if config is None:
            raise HTTPException(status_code=500, detail="Configuration not loaded")
        
        # Подготовка конфигурации
        current_config = config.copy()
        if request.strategy:
            current_config['monetization']['strategy'] = request.strategy
        if request.methods:
            current_config['monetization']['methods'] = request.methods
        
        # Преобразование входного контента в словарь
        content = request.content.model_dump()
        
        # Определение действий
        strategy = current_config['monetization']['strategy']
        actions = determine_actions_for_strategy(strategy, current_config)
        
        # Применение монетизации
        result = inject_monetization_elements(content, actions, current_config)
        
        # Расчёт метрик
        metrics = calculate_monetization_metrics(result)
        
        # Проверка соответствия
        compliance_warnings = {}
        description = result.get('description', '')
        
        youtube_issues = check_youtube_description_compliance(description)
        if youtube_issues:
            compliance_warnings['youtube'] = youtube_issues
        
        general_issues = check_general_compliance(description)
        if general_issues:
            compliance_warnings['general'] = general_issues
        
        logger.info(f"Content {content['id']} monetized successfully with strategy {strategy}")
        
        return MonetizeResponse(
            success=True,
            result=result,
            metrics=metrics,
            compliance_warnings=compliance_warnings if compliance_warnings else None
        )
    
    except Exception as e:
        logger.error(f"Error monetizing content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/compliance/youtube", response_model=ComplianceResponse)
async def check_youtube_compliance(description: str):
    """
    Проверяет описание на соответствие политикам YouTube.
    
    Args:
        description: Текст описания для проверки
    
    Returns:
        Результат проверки с найденными проблемами
    """
    try:
        issues = check_youtube_description_compliance(description)
        return ComplianceResponse(
            compliant=len(issues) == 0,
            issues=issues
        )
    except Exception as e:
        logger.error(f"Error checking YouTube compliance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/compliance/amazon-kdp", response_model=ComplianceResponse)
async def check_amazon_kdp_compliance(description: str):
    """
    Проверяет описание на соответствие политикам Amazon KDP.
    
    Args:
        description: Текст описания для проверки
    
    Returns:
        Результат проверки с найденными проблемами
    """
    try:
        issues = check_amazon_kdp_compliance(description)
        return ComplianceResponse(
            compliant=len(issues) == 0,
            issues=issues
        )
    except Exception as e:
        logger.error(f"Error checking Amazon KDP compliance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/strategies", response_model=StrategiesResponse)
async def get_strategies():
    """
    Возвращает список доступных стратегий монетизации.
    
    Returns:
        Список стратегий с описаниями
    """
    strategies = [
        {
            "name": "full",
            "display_name": "Полная монетизация",
            "description": "Все методы монетизации активны с явными дисклеймерами"
        },
        {
            "name": "partial",
            "display_name": "Частичная монетизация",
            "description": "Выборочные методы монетизации"
        },
        {
            "name": "masked",
            "display_name": "Замаскированная монетизация",
            "description": "Деликатная монетизация без явных дисклеймеров"
        },
        {
            "name": "hidden",
            "display_name": "Скрытая монетизация",
            "description": "Минимальное вмешательство, приоритет на UX"
        }
    ]
    return StrategiesResponse(strategies=strategies)

@app.post("/api/v1/analytics/link", response_model=UniqueLinkResponse)
async def generate_link(request: UniqueLinkRequest):
    """
    Генерирует уникальную партнёрскую ссылку с UTM-метками.
    
    Args:
        request: Параметры для генерации ссылки
    
    Returns:
        Уникальная ссылка с UTM-параметрами
    """
    try:
        link = generate_unique_affiliate_link(
            base_url=request.base_url,
            content_id=request.content_id,
            source=request.source,
            medium=request.medium
        )
        return UniqueLinkResponse(link=link)
    except Exception as e:
        logger.error(f"Error generating link: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/report")
async def generate_report(content_ids: List[str]):
    """
    Генерирует отчёт о монетизации для списка контента.
    
    Args:
        content_ids: Список идентификаторов контента
    
    Returns:
        Агрегированный отчёт о монетизации
    """
    try:
        # TODO: Реализовать загрузку данных контента и генерацию отчёта
        return {
            "success": True,
            "content_count": len(content_ids),
            "message": "Report generation not yet implemented"
        }
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting SSV Monetization Tool API server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
