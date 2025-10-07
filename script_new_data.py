import pandas as pd
import random

# Читаем исходный CSV файл
df = pd.read_csv('rations.csv')

# Целевые пределы для кислот
TARGET_LIMITS = {
    'Масляная': {'min': 2.4, 'max': 4.2},
    'Капроновая': {'min': 1.5, 'max': 3.0},
    'Каприловая': {'min': 1.0, 'max': 2.0},
    'Каприновая': {'min': 2.0, 'max': 3.8},
    'Деценовая': {'min': 0.2, 'max': 0.4},
    'Лауриновая': {'min': 2.0, 'max': 4.4},
    'Миристиновая': {'min': 8.0, 'max': 13.0},
    'Миристолеиновая': {'min': 0.6, 'max': 1.5},
    'Пальмитиновая': {'min': 21.0, 'max': 32.0},
    'Пальмитолеиновая': {'min': 1.3, 'max': 2.4},
    'Стеариновая': {'min': 8.0, 'max': 13.5},
    'Олеиновая': {'min': 20.0, 'max': 28.0},
    'Линолевая': {'min': 2.2, 'max': 5.0},
    'Линоленовая': {'min': 0, 'max': 1.5},
    'Арахиновая': {'min': 0, 'max': 0.3},
    'Бегеновая': {'min': 0, 'max': 0.1},
    'Прочие': {'min': 4.5, 'max': 6.5}
}

# Добавляем колонки для каждой кислоты
for acid_name, limits in TARGET_LIMITS.items():
    min_val = limits['min']
    max_val = limits['max']
    # Генерируем случайные значения в пределах для каждой строки
    df[acid_name] = [round(random.uniform(min_val, max_val), 2) for _ in range(len(df))]

# Сохраняем новый CSV файл
output_filename = 'rations_with_acids.csv'
df.to_csv(output_filename, index=False, encoding='utf-8-sig')

print(f"✅ Создан файл {output_filename}")
print(f"📊 Добавлено {len(TARGET_LIMITS)} колонок с кислотами")
print("📋 Список добавленных колонок:")
for acid_name in TARGET_LIMITS.keys():
    print(f"   • {acid_name}")

# Проверяем первые несколько строк
print(f"\n📄 Первые 3 строки нового файла:")
print(df.head(3)[['ration_id'] + list(TARGET_LIMITS.keys())[:5]].to_string())