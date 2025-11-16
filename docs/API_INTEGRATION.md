# Интеграция API - SSV Monetization Tool

## 📚 Содержание

1. [Обзор](#обзор)
2. [Установка и запуск API сервера](#установка-и-запуск-api-сервера)
3. [API Endpoints](#api-endpoints)
4. [Интеграция с ssv-web-dashboard](#интеграция-с-ssv-web-dashboard)
5. [Использование клиентской библиотеки](#использование-клиентской-библиотеки)
6. [Примеры интеграции](#примеры-интеграции)

---

## Обзор

SSV Monetization Tool предоставляет REST API для интеграции с веб-панелью управления (ssv-web-dashboard) и другими инструментами экосистемы SSVproff.

### Основные возможности API:

- ✅ Применение монетизации к контенту
- ✅ Проверка соответствия политикам платформ (YouTube, Amazon KDP)
- ✅ Генерация уникальных партнёрских ссылок
- ✅ Получение списка доступных стратегий
- ✅ Генерация отчётов о монетизации

---

## Установка и запуск API сервера

### Шаг 1: Установка зависимостей

```bash
cd ssv-monetization-tool

# Установка основных зависимостей
pip install -r requirements.txt

# Установка зависимостей для API
pip install -r requirements-api.txt
```

### Шаг 2: Запуск сервера

```bash
# Запуск на localhost:8000
python api/app.py

# Или с использованием uvicorn
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

### Шаг 3: Проверка работоспособности

Откройте в браузере:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

---

## API Endpoints

### 1. Корневой endpoint

**GET /**

Возвращает информацию об API.

**Response:**

```json
{
  "name": "SSV Monetization Tool API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

---

### 2. Проверка состояния

**GET /health**

Проверяет состояние API сервера.

**Response:**

```json
{
  "status": "healthy",
  "config_loaded": true
}
```

---

### 3. Применение монетизации

**POST /api/v1/monetize**

Применяет монетизацию к контенту.

**Request Body:**

```json
{
  "content": {
    "id": "video_001",
    "title": "Техника лапароскопической холецистэктомии",
    "description": "Подробный разбор техники операции..."
  },
  "strategy": "masked",
  "methods": ["affiliate_links", "premium_content"]
}
```

**Response:**

```json
{
  "success": true,
  "result": {
    "id": "video_001",
    "title": "Техника лапароскопической холецистэктомии",
    "description": "Подробный разбор техники операции... (https://store.com/tools?ref=ssv&utm_source=youtube&utm_campaign=video_001)"
  },
  "metrics": {
    "description_length": 350,
    "affiliate_links_count": 2,
    "has_disclaimer": false,
    "has_cta": true
  },
  "compliance_warnings": null
}
```

**cURL Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/monetize" \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "id": "video_001",
      "title": "Техника операции",
      "description": "Описание контента..."
    },
    "strategy": "masked"
  }'
```

---

### 4. Проверка соответствия YouTube

**GET /api/v1/compliance/youtube**

Проверяет описание на соответствие политикам YouTube.

**Query Parameters:**
- `description` (string, required) — текст описания для проверки

**Response:**

```json
{
  "compliant": false,
  "issues": [
    "Excessive caps detected",
    "Too many links (18), YouTube limit is 15"
  ]
}
```

**cURL Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/compliance/youtube?description=КУПИТЬ+СЕЙЧАС!!!"
```

---

### 5. Проверка соответствия Amazon KDP

**GET /api/v1/compliance/amazon-kdp**

Проверяет описание на соответствие политикам Amazon KDP.

**Query Parameters:**
- `description` (string, required) — текст описания для проверки

**Response:**

```json
{
  "compliant": true,
  "issues": []
}
```

---

### 6. Получение списка стратегий

**GET /api/v1/strategies**

Возвращает список доступных стратегий монетизации.

**Response:**

```json
{
  "strategies": [
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
}
```

---

### 7. Генерация уникальной ссылки

**POST /api/v1/analytics/link**

Генерирует уникальную партнёрскую ссылку с UTM-метками.

**Request Body:**

```json
{
  "base_url": "https://amazon.com/product",
  "content_id": "video_001",
  "source": "youtube",
  "medium": "description"
}
```

**Response:**

```json
{
  "link": "https://amazon.com/product?utm_source=youtube&utm_medium=description&utm_campaign=video_001"
}
```

---

## Интеграция с ssv-web-dashboard

### Вариант 1: Использование клиентской библиотеки

```python
# В файле ssv-web-dashboard/backend/monetization_integration.py

import sys
sys.path.append('../ssv-monetization-tool')

from client.monetization_client import MonetizationClient

# Создание клиента
monetization_client = MonetizationClient(base_url="http://localhost:8000")

# Применение монетизации при создании видео
def create_video_with_monetization(video_data, strategy='masked'):
    """Создание видео с автоматической монетизацией."""
    
    # Применение монетизации
    result = monetization_client.monetize_content(
        content={
            'id': video_data['id'],
            'title': video_data['title'],
            'description': video_data['description']
        },
        strategy=strategy
    )
    
    # Обновление описания
    video_data['description'] = result['result']['description']
    video_data['metrics'] = result['metrics']
    
    return video_data
```

### Вариант 2: Прямые HTTP запросы

```javascript
// В файле ssv-web-dashboard/frontend/src/api/monetization.js

const MONETIZATION_API_URL = 'http://localhost:8000';

export async function monetizeContent(content, strategy = 'masked') {
  const response = await fetch(`${MONETIZATION_API_URL}/api/v1/monetize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      content,
      strategy,
    }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to monetize content');
  }
  
  return response.json();
}

export async function checkYouTubeCompliance(description) {
  const params = new URLSearchParams({ description });
  const response = await fetch(
    `${MONETIZATION_API_URL}/api/v1/compliance/youtube?${params}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to check compliance');
  }
  
  return response.json();
}

export async function getStrategies() {
  const response = await fetch(`${MONETIZATION_API_URL}/api/v1/strategies`);
  
  if (!response.ok) {
    throw new Error('Failed to get strategies');
  }
  
  return response.json();
}
```

### Пример использования в React компоненте

```jsx
// ssv-web-dashboard/frontend/src/components/VideoEditor.jsx

import React, { useState, useEffect } from 'react';
import { monetizeContent, getStrategies } from '../api/monetization';

function VideoEditor() {
  const [videoData, setVideoData] = useState({
    id: 'video_001',
    title: '',
    description: '',
  });
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState('masked');
  const [isMonetizing, setIsMonetizing] = useState(false);

  useEffect(() => {
    // Загрузка списка стратегий при монтировании компонента
    getStrategies().then((data) => setStrategies(data.strategies));
  }, []);

  const handleMonetize = async () => {
    setIsMonetizing(true);
    try {
      const result = await monetizeContent(videoData, selectedStrategy);
      setVideoData((prev) => ({
        ...prev,
        description: result.result.description,
      }));
      alert('Монетизация применена успешно!');
    } catch (error) {
      alert('Ошибка монетизации: ' + error.message);
    } finally {
      setIsMonetizing(false);
    }
  };

  return (
    <div className="video-editor">
      <h2>Редактор видео</h2>
      
      <input
        type="text"
        placeholder="Заголовок"
        value={videoData.title}
        onChange={(e) => setVideoData({ ...videoData, title: e.target.value })}
      />
      
      <textarea
        placeholder="Описание"
        value={videoData.description}
        onChange={(e) => setVideoData({ ...videoData, description: e.target.value })}
      />
      
      <select
        value={selectedStrategy}
        onChange={(e) => setSelectedStrategy(e.target.value)}
      >
        {strategies.map((strategy) => (
          <option key={strategy.name} value={strategy.name}>
            {strategy.display_name}
          </option>
        ))}
      </select>
      
      <button onClick={handleMonetize} disabled={isMonetizing}>
        {isMonetizing ? 'Применение...' : 'Применить монетизацию'}
      </button>
    </div>
  );
}

export default VideoEditor;
```

---

## Использование клиентской библиотеки

### Установка

```bash
# В проекте ssv-web-dashboard
cd backend
pip install -e ../ssv-monetization-tool
```

### Базовое использование

```python
from client.monetization_client import MonetizationClient

# Создание клиента
client = MonetizationClient(base_url="http://localhost:8000")

# Проверка состояния сервера
health = client.health_check()
print(f"Статус сервера: {health['status']}")

# Применение монетизации
content = {
    'id': 'video_001',
    'title': 'Техника операции',
    'description': 'Описание...'
}

result = client.monetize_content(content, strategy='masked')
print(f"Описание: {result['result']['description']}")
print(f"Метрики: {result['metrics']}")

# Проверка соответствия
compliance = client.check_youtube_compliance(result['result']['description'])
print(f"Соответствует YouTube: {compliance['compliant']}")

# Генерация уникальной ссылки
link = client.generate_unique_link(
    base_url="https://amazon.com/product",
    content_id="video_001",
    source="youtube"
)
print(f"Уникальная ссылка: {link}")
```

---

## Примеры интеграции

### Пример 1: Автоматическая монетизация при создании видео

```python
# backend/views/video_views.py

from flask import Blueprint, request, jsonify
from client.monetization_client import MonetizationClient

video_bp = Blueprint('video', __name__)
monetization_client = MonetizationClient(base_url="http://localhost:8000")

@video_bp.route('/api/videos', methods=['POST'])
def create_video():
    """Создание видео с автоматической монетизацией."""
    data = request.json
    
    # Применение монетизации
    try:
        result = monetization_client.monetize_content(
            content={
                'id': data['id'],
                'title': data['title'],
                'description': data['description']
            },
            strategy=data.get('monetization_strategy', 'masked')
        )
        
        # Сохранение в базе данных
        video = Video(
            id=data['id'],
            title=data['title'],
            description=result['result']['description'],
            metrics=result['metrics']
        )
        db.session.add(video)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'video': video.to_dict(),
            'monetization_metrics': result['metrics']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

### Пример 2: Проверка соответствия в реальном времени

```javascript
// frontend/src/components/DescriptionEditor.jsx

import React, { useState, useEffect } from 'react';
import { checkYouTubeCompliance } from '../api/monetization';
import debounce from 'lodash/debounce';

function DescriptionEditor({ value, onChange }) {
  const [compliance, setCompliance] = useState(null);
  const [isChecking, setIsChecking] = useState(false);

  // Проверка соответствия с задержкой при изменении текста
  const checkCompliance = debounce(async (description) => {
    if (!description) return;
    
    setIsChecking(true);
    try {
      const result = await checkYouTubeCompliance(description);
      setCompliance(result);
    } catch (error) {
      console.error('Ошибка проверки:', error);
    } finally {
      setIsChecking(false);
    }
  }, 1000);

  useEffect(() => {
    checkCompliance(value);
  }, [value]);

  return (
    <div className="description-editor">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Описание видео..."
      />
      
      {isChecking && <div className="checking">Проверка...</div>}
      
      {compliance && (
        <div className={`compliance ${compliance.compliant ? 'success' : 'warning'}`}>
          {compliance.compliant ? (
            <span>✅ Соответствует политикам YouTube</span>
          ) : (
            <div>
              <span>⚠️ Обнаружены проблемы:</span>
              <ul>
                {compliance.issues.map((issue, index) => (
                  <li key={index}>{issue}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default DescriptionEditor;
```

### Пример 3: Массовая обработка контента

```python
# backend/tasks/batch_monetization.py

from celery import shared_task
from client.monetization_client import MonetizationClient
from models import Video

monetization_client = MonetizationClient(base_url="http://localhost:8000")

@shared_task
def batch_monetize_videos(video_ids, strategy='masked'):
    """
    Фоновая задача для массовой монетизации видео.
    
    Args:
        video_ids: Список ID видео для обработки
        strategy: Стратегия монетизации
    """
    results = []
    
    for video_id in video_ids:
        try:
            video = Video.query.get(video_id)
            if not video:
                continue
            
            # Применение монетизации
            result = monetization_client.monetize_content(
                content={
                    'id': video.id,
                    'title': video.title,
                    'description': video.description
                },
                strategy=strategy
            )
            
            # Обновление в базе данных
            video.description = result['result']['description']
            video.monetization_metrics = result['metrics']
            db.session.commit()
            
            results.append({
                'video_id': video_id,
                'success': True,
                'metrics': result['metrics']
            })
        
        except Exception as e:
            results.append({
                'video_id': video_id,
                'success': False,
                'error': str(e)
            })
    
    return {
        'total': len(video_ids),
        'successful': len([r for r in results if r['success']]),
        'failed': len([r for r in results if not r['success']]),
        'results': results
    }
```

---

## Дополнительные ресурсы

- [API документация](API.md)
- [Руководство пользователя](USAGE.md)
- [Примеры кода](EXAMPLES.md)
- [GitHub репозиторий](https://github.com/Serg2206/ssv-monetization-tool)

---

**Автор:** Профессор С.В. Сушков  
**Проект:** SSVproff-Ecosystem  
**Лицензия:** MIT
