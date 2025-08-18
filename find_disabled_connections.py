#!/usr/bin/env python3
"""
Скрипт для поиска мозгов с неактивными связями.

Проверяет API endpoints и показывает, у каких мозгов есть disabled connections.
"""

import requests
import json
from typing import Dict, List

def check_brain_connections(brain_id: int, api_url: str = "http://localhost:8000") -> Dict:
    """Проверяет связи конкретного мозга."""
    try:
        response = requests.get(f"{api_url}/api/population/{brain_id}")
        if response.status_code == 200:
            data = response.json()
            connections = data.get('connections', [])
            
            total_connections = len(connections)
            active_connections = len([c for c in connections if c.get('enabled', True)])
            disabled_connections = len([c for c in connections if not c.get('enabled', True)])
            
            disabled_list = [
                {
                    'id': c['id'],
                    'from': c['from'],
                    'to': c['to'],
                    'weight': c['weight']
                }
                for c in connections if not c.get('enabled', True)
            ]
            
            return {
                'brain_id': brain_id,
                'status': 'success',
                'total_connections': total_connections,
                'active_connections': active_connections,
                'disabled_connections': disabled_connections,
                'disabled_list': disabled_list,
                'has_disabled': disabled_connections > 0
            }
        else:
            return {
                'brain_id': brain_id,
                'status': 'error',
                'error': f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            'brain_id': brain_id,
            'status': 'error',
            'error': str(e)
        }

def find_brains_with_disabled_connections(brain_range: range = range(1, 21), api_url: str = "http://localhost:8000"):
    """Находит все мозги с неактивными связями."""
    print("🔍 Поиск мозгов с неактивными связями...")
    print(f"🌐 API URL: {api_url}")
    print(f"🧠 Проверяю мозги: {brain_range.start}-{brain_range.stop-1}")
    print("-" * 80)
    
    brains_with_disabled = []
    brains_without_disabled = []
    errors = []
    
    for brain_id in brain_range:
        print(f"🧠 Проверяю мозг #{brain_id}...", end=" ")
        result = check_brain_connections(brain_id, api_url)
        
        if result['status'] == 'success':
            if result['has_disabled']:
                brains_with_disabled.append(result)
                print(f"✅ Найдены неактивные связи: {result['disabled_connections']}")
                for disabled in result['disabled_list']:
                    print(f"   🔗 Связь {disabled['id']}: {disabled['from']} → {disabled['to']} (вес: {disabled['weight']})")
            else:
                brains_without_disabled.append(result)
                print("⚪ Все связи активны")
        else:
            errors.append(result)
            print(f"❌ Ошибка: {result['error']}")
    
    print("-" * 80)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"🟢 Мозги с неактивными связями: {len(brains_with_disabled)}")
    if brains_with_disabled:
        brain_ids = [b['brain_id'] for b in brains_with_disabled]
        print(f"   📋 ID мозгов: {brain_ids}")
        
    print(f"⚪ Мозги только с активными связями: {len(brains_without_disabled)}")
    if brains_without_disabled:
        brain_ids = [b['brain_id'] for b in brains_without_disabled]
        print(f"   📋 ID мозгов: {brain_ids}")
        
    print(f"❌ Ошибки: {len(errors)}")
    
    if brains_with_disabled:
        print("\n🎯 РЕКОМЕНДАЦИЯ:")
        print(f"Для тестирования неактивных связей используйте мозг #{brains_with_disabled[0]['brain_id']}")
        print("Включите показ неактивных связей кнопкой с иконкой Activity")

if __name__ == "__main__":
    print("🧠 Поиск мозгов с неактивными связями для тестирования")
    print("=" * 80)
    
    # Проверяем доступность API
    try:
        response = requests.get("http://localhost:8000/api/health")
        if response.status_code == 200:
            print("✅ API доступно")
        else:
            print(f"⚠️ API вернуло статус {response.status_code}")
    except Exception as e:
        print(f"❌ API недоступно: {e}")
        print("💡 Запустите API: cd api && python main.py")
        exit(1)
    
    # Ищем мозги с неактивными связями
    find_brains_with_disabled_connections()