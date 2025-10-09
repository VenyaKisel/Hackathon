import pandas as pd
import re

def compress_rations_to_13_features(csv_path: str, output_path: str = None) -> pd.DataFrame:

    df = pd.read_csv(csv_path)
    
    def map_component(component_name: str) -> str:
        """Сопоставляет компонент CSV с признаком модели"""
        comp_lower = component_name.lower().strip()
        
        # 1. трав_сен - травяное сено
        if any(word in comp_lower for word in ['сено', 'люцерна', 'суданка', 'тимофеевка', 'клевер']):
            return 'трав_сен'
        
        elif any(word in comp_lower for word in ['кукуруза', 'ячмень', 'пшеница', 'рожь', 'тритикале', 
                                               'зерносмесь', 'концентрат', 'комбикорм', 'фураж']):
            return 'конц_зерн'
        
        elif any(word in comp_lower for word in ['шрот', 'жмых', 'соев', 'рапс', 'льнян', 'подсолнечн']):
            return 'масличн'
        
        elif 'жир' in comp_lower:
            return 'жир'
        
        elif any(word in comp_lower for word in ['жом', 'патока', 'дробина', 'дрожж', 'пивн']):
            return 'пром_отх'
        
        elif any(word in comp_lower for word in ['премикс', 'сода', 'соль', 'поташ', 'мел', 'кальций']):
            return 'мин_техно'
        
        elif 'патока' in comp_lower:
            return 'сп'
        
        elif any(word in comp_lower for word in ['кукуруза', 'ячмень', 'пшеница', 'крахмал']):
            return 'крахмал'
        
        elif any(word in comp_lower for word in ['силос', 'сенаж', 'корнаж', 'солома', 'сено']):
            return 'andfom'
        
        elif 'патока' in comp_lower or 'сахар' in comp_lower:
            return 'сахар (вру)'

        elif 'поташ' in comp_lower:
            return 'k'
        
        else:
            return 'другое'
    
    features_columns = [
        'трав_сен', 'конц_зерн', 'масличн', 'жир', 'пром_отх', 
        'мин_техно', 'сп', 'крахмал', 'andfom', 'сахар (вру)', 
        'нву', 'ожк', 'k'
    ]
    
    result_df = pd.DataFrame()
    result_df['ration_id'] = df['ration_id']
    
    for feature in features_columns:
        result_df[feature] = 0.0
    
    component_columns = [col for col in df.columns if col != 'ration_id']
    
    print("🔍 ПРОЦЕСС ПРЕОБРАЗОВАНИЯ:")
    mapping_stats = {}
    
    for component in component_columns:
        feature = map_component(component)
        
        if feature not in mapping_stats:
            mapping_stats[feature] = []
        mapping_stats[feature].append(component)
        
        if feature in features_columns:
            result_df[feature] += df[component].fillna(0)
    
    print("\n📊 СТАТИСТИКА ПРЕОБРАЗОВАНИЯ:")
    for feature, components in mapping_stats.items():
        print(f"   {feature}: {len(components)} компонентов")
        for comp in components[:3]: 
            print(f"     - {comp}")
        if len(components) > 3:
            print(f"     ... и еще {len(components) - 3}")
    
    if output_path:
        result_df.to_csv(output_path, index=False)
        print(f"\n💾 Результат сохранен в: {output_path}")
    
    print(f"\n✅ Исходные данные: {len(component_columns)} компонентов")
    print(f"✅ Сжатые данные: 13 признаков")
    print(f"✅ Обработано рационов: {len(result_df)}")
    
    return result_df

def analyze_compressed_features(compressed_df: pd.DataFrame):
    """Анализирует распределение значений в сжатых данных"""
    print("\n📈 АНАЛИЗ РАСПРЕДЕЛЕНИЯ ПРИЗНАКОВ:")
    
    features_columns = [
        'трав_сен', 'конц_зерн', 'масличн', 'жир', 'пром_отх', 
        'мин_техно', 'сп', 'крахмал', 'andfom', 'сахар (вру)', 
        'нву', 'ожк', 'k'
    ]
    
    for feature in features_columns:
        non_zero = (compressed_df[feature] > 0).sum()
        total = len(compressed_df)
        percentage = (non_zero / total) * 100
        avg_value = compressed_df[feature].mean()
        max_value = compressed_df[feature].max()
        
        print(f"   {feature}:")
        print(f"     Заполнено: {non_zero}/{total} ({percentage:.1f}%)")
        print(f"     Среднее: {avg_value:.2f}, Максимум: {max_value:.2f}")
