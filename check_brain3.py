import requests
import json

# Проверяем мозг #3
r = requests.get("http://localhost:8000/api/population/3")
data = r.json()

print(f"Мозг #{data['id']}: {len(data['connections'])} связей")
print(f"Узлы: {len(data['nodes'])}")

# Ищем неактивные связи
disabled = [c for c in data["connections"] if not c["enabled"]]
print(f"\nНеактивных связей: {len(disabled)}")

if disabled:
    print("Неактивные связи:")
    for c in disabled:
        print(f"  Связь {c['id']}: {c['from']} -> {c['to']} (вес: {c['weight']})")
else:
    print("Все связи активны")

# Показываем все связи
print(f"\nВсе связи:")
for c in data["connections"]:
    status = "🔴 НЕАКТИВНА" if not c["enabled"] else "🟢 активна"
    print(
        f"  {status} - Связь {c['id']}: {c['from']} -> {c['to']} (вес: {c['weight']})"
    )
