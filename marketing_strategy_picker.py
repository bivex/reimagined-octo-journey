#!/usr/bin/env python3
"""
Marketing Strategy Picker для воронки продаж
Подбирает подходящие маркетинговые стратегии для каждого этапа от гостя до клиента.
"""

import json
import random
from typing import Dict, List, Set, Optional
from collections import defaultdict


class MarketingStrategyPicker:
    """
    Класс для подбора маркетинговых стратегий по этапам воронки продаж.
    """

    # Этапы воронки от гостя до клиента
    FUNNEL_STAGES = {
        'awareness': {
            'name': 'Осведомленность',
            'description': 'Привлечение внимания к продукту/бренду',
            'types': ['Awareness'],
            'order': 1
        },
        'acquisition': {
            'name': 'Привлечение',
            'description': 'Привлечение трафика на сайт/приложение',
            'types': ['Acquisition'],
            'order': 2
        },
        'activation': {
            'name': 'Активация',
            'description': 'Вовлечение пользователей, регистрация, первый опыт',
            'types': ['Activation'],
            'order': 3
        },
        'revenue': {
            'name': 'Доход',
            'description': 'Совершение первой покупки',
            'types': ['Revenue'],
            'order': 4
        },
        'retention': {
            'name': 'Удержание',
            'description': 'Повторные покупки, лояльность клиентов',
            'types': ['Retention'],
            'order': 5
        },
        'referral': {
            'name': 'Рефералы',
            'description': 'Рекомендации, сарафанное радио',
            'types': ['Referral'],
            'order': 6
        }
    }

    def __init__(self, json_file: str = 'marketing_strategies.json'):
        """Инициализация с загрузкой данных."""
        self.strategies = self._load_strategies(json_file)
        self.strategies_by_type = self._group_strategies_by_type()

    def _load_strategies(self, json_file: str) -> List[Dict]:
        """Загружает стратегии из JSON файла."""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Ошибка: файл {json_file} не найден")
            return []
        except json.JSONDecodeError as e:
            print(f"Ошибка чтения JSON: {e}")
            return []

    def _group_strategies_by_type(self) -> Dict[str, List[Dict]]:
        """Группирует стратегии по типам."""
        grouped = defaultdict(list)
        for strategy in self.strategies:
            for strategy_type in strategy.get('types', []):
                grouped[strategy_type].append(strategy)
        return dict(grouped)

    def get_strategies_for_stage(self, stage_key: str, limit: int = 10) -> List[Dict]:
        """
        Получает стратегии для конкретного этапа воронки.

        Args:
            stage_key: Ключ этапа (awareness, acquisition, etc.)
            limit: Максимальное количество стратегий

        Returns:
            Список стратегий для этапа
        """
        if stage_key not in self.FUNNEL_STAGES:
            return []

        stage_info = self.FUNNEL_STAGES[stage_key]
        strategies = []

        # Собираем стратегии по всем типам этапа
        for strategy_type in stage_info['types']:
            if strategy_type in self.strategies_by_type:
                strategies.extend(self.strategies_by_type[strategy_type])

        # Убираем дубликаты (стратегия может иметь несколько типов)
        seen_names = set()
        unique_strategies = []
        for strategy in strategies:
            if strategy['name'] not in seen_names:
                unique_strategies.append(strategy)
                seen_names.add(strategy['name'])

        # Ограничиваем количество и сортируем по impact (если есть)
        unique_strategies.sort(key=lambda x: x.get('impact', ''), reverse=True)
        return unique_strategies[:limit]

    def get_funnel_recommendations(self, selected_stages: Optional[List[str]] = None,
                                 strategies_per_stage: int = 5) -> Dict:
        """
        Получает рекомендации для всей воронки или выбранных этапов.

        Args:
            selected_stages: Список ключей этапов для анализа (None - все этапы)
            strategies_per_stage: Количество стратегий на этап

        Returns:
            Словарь с рекомендациями по этапам
        """
        if selected_stages is None:
            selected_stages = list(self.FUNNEL_STAGES.keys())
        elif not isinstance(selected_stages, list):
            selected_stages = [selected_stages]

        recommendations = {}

        # Сортируем этапы по порядку в воронке
        sorted_stages = sorted(
            [stage for stage in selected_stages if stage in self.FUNNEL_STAGES],
            key=lambda x: self.FUNNEL_STAGES[x]['order']
        )

        for stage_key in sorted_stages:
            stage_info = self.FUNNEL_STAGES[stage_key]
            strategies = self.get_strategies_for_stage(stage_key, strategies_per_stage)

            recommendations[stage_key] = {
                'stage_name': stage_info['name'],
                'description': stage_info['description'],
                'strategies': strategies,
                'count': len(strategies)
            }

        return recommendations

    def print_funnel_overview(self):
        """Выводит обзор всех этапов воронки."""
        print("🎯 ВОРОНКА ПРОДАЖ: от гостя до клиента\n")
        print("=" * 60)

        for stage_key, stage_info in sorted(self.FUNNEL_STAGES.items(),
                                          key=lambda x: x[1]['order']):
            count = len(self.strategies_by_type.get(stage_info['types'][0], []))
            print(f"{stage_info['order']}. {stage_info['name']}")
            print(f"   📝 {stage_info['description']}")
            print(f"   📊 Доступно стратегий: {count}")
            print()

    def print_recommendations(self, recommendations: Dict):
        """Выводит рекомендации в читаемом формате."""
        print("🎯 РЕКОМЕНДАЦИИ ПО ЭТАПАМ ВОРОНКИ\n")
        print("=" * 80)

        for stage_key, data in recommendations.items():
            print(f"\n{self.FUNNEL_STAGES[stage_key]['order']}. {data['stage_name']}")
            print("-" * 60)
            print(f"📝 {data['description']}")
            print(f"📊 Найдено стратегий: {data['count']}\n")

            for i, strategy in enumerate(data['strategies'], 1):
                print(f"   {i}. {strategy['name']}")
                print(f"      💡 {strategy['description'][:100]}...")

                impact = strategy.get('impact')
                if impact:
                    print(f"      📈 Влияние: {impact}")

                effort = strategy.get('effort_hours')
                if effort:
                    print(f"      ⏱️  Усилий: {effort} часов")

                print()

    def interactive_mode(self):
        """Интерактивный режим выбора этапов."""
        print("🎯 ИНТЕРАКТИВНЫЙ ПОДБОР СТРАТЕГИЙ\n")
        print("Выберите этапы воронки для анализа:")
        print("0. Все этапы")
        print()

        for stage_key, stage_info in sorted(self.FUNNEL_STAGES.items(),
                                          key=lambda x: x[1]['order']):
            count = len(self.strategies_by_type.get(stage_info['types'][0], []))
            print(f"{stage_info['order']}. {stage_info['name']} ({count} стратегий)")
            print(f"   {stage_info['description']}")

        print()

        while True:
            try:
                choice = input("Введите номера этапов через запятую (или 'q' для выхода): ").strip()

                if choice.lower() in ['q', 'quit', 'exit']:
                    break

                if choice == '0':
                    selected_stages = list(self.FUNNEL_STAGES.keys())
                else:
                    selected_numbers = [int(x.strip()) for x in choice.split(',') if x.strip()]
                    selected_stages = []
                    for num in selected_numbers:
                        for stage_key, stage_info in self.FUNNEL_STAGES.items():
                            if stage_info['order'] == num:
                                selected_stages.append(stage_key)
                                break

                if not selected_stages:
                    print("❌ Неверный выбор. Попробуйте снова.")
                    continue

                # Получаем рекомендации
                recommendations = self.get_funnel_recommendations(selected_stages)

                # Выводим результаты
                self.print_recommendations(recommendations)

                break

            except ValueError:
                print("❌ Ошибка ввода. Введите числа через запятую.")
            except KeyboardInterrupt:
                break

    def export_to_json(self, recommendations: Dict, filename: str = 'funnel_recommendations.json'):
        """Экспортирует рекомендации в JSON файл."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(recommendations, f, indent=2, ensure_ascii=False)
            print(f"✅ Рекомендации сохранены в файл: {filename}")
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")


def main():
    """Главная функция."""
    picker = MarketingStrategyPicker()

    if not picker.strategies:
        print("❌ Не удалось загрузить стратегии")
        return

    print(f"✅ Загружено {len(picker.strategies)} маркетинговых стратегий")

    # Показываем обзор
    picker.print_funnel_overview()

    # Запускаем интерактивный режим
    picker.interactive_mode()

    # Предлагаем сохранить результаты
    save = input("\nСохранить рекомендации в JSON файл? (y/n): ").strip().lower()
    if save == 'y':
        recommendations = picker.get_funnel_recommendations()
        picker.export_to_json(recommendations)


if __name__ == "__main__":
    main()
