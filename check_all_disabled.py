import requests
import json

# Проверяем все мозги на неактивные связи
print("🔍 Проверка всех мозгов на неактивные связи...")
print("=" * 60)

brains_with_disabled = []
total_brains = 0

for brain_id in range(1, 21):  # Проверяем мозги 1-20
    try:
        r = requests.get(f'http://localhost:8000/api/population/{brain_id}')
        if r.status_code == 200:
            data = r.json()
            total_brains += 1
            
            # Ищем неактивные связи
            disabled = [c for c in data['connections'] if not c['enabled']]
            
            if disabled:
                brains_with_disabled.append({
                    'id': brain_id,
                    'disabled_count': len(disabled),
                    'connections': len(data['connections']),
                    'nodes': len(data['nodes'])
                })
                print(f"🧠 Мозг #{brain_id}: {len(disabled)} неактивных связей из {len(data['connections'])}")
            else:
                print(f"⚪ Мозг #{brain_id}: все связи активны")
        else:
            print(f"❌ Мозг #{brain_id}: ошибка {r.status_code}")
    except Exception as e:
        print(f"❌ Мозг #{brain_id}: ошибка {e}")

print("=" * 60)
print(f"📊 РЕЗУЛЬТАТЫ:")
print(f"Всего мозгов: {total_brains}")
print(f"Мозгов с неактивными связями: {len(brains_with_disabled)}")

if brains_with_disabled:
    print("\n🎯 Мозги для тестирования неактивных связей:")
    for brain in brains_with_disabled:
        print(f"  Мозг #{brain['id']}: {brain['disabled_count']} неактивных связей")
    
    print(f"\n💡 РЕКОМЕНДАЦИЯ:")
    print(f"Для тестирования используйте мозг #{brains_with_disabled[0]['id']}")
    print("Включите показ неактивных связей кнопкой с иконкой Activity")
else:
    print("❌ Неактивных связей не найдено") 