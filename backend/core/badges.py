from dataclasses import dataclass


@dataclass(frozen=True)
class Badge:
    code: str
    icon: str
    title: str
    description: str
    category: str      # success / neutral / growth


B = {
    'accuracy': Badge('accuracy', '🎯', 'Абсолютная точность',
                      'Все ответы верные.', 'success'),
    'golden': Badge('golden', '🧠', 'Золотой стандарт',
                    'Скорость в пределах нормы и отличное понимание.', 'success'),
    'speed': Badge('speed', '🚀', 'Скорочтец',
                   'Очень высокая скорость при хорошем понимании.', 'success'),
    'thoughtful': Badge('thoughtful', '🐢', 'Вдумчивый читатель',
                        'Читаете неторопливо, но понимаете текст полностью.', 'success'),
    'balanced': Badge('balanced', '⚖️', 'Сбалансированный подход',
                      'Нормальная скорость и нормальное понимание.', 'neutral'),
    'stable': Badge('stable', '📖', 'Стабильный результат',
                    'Хороший проходной результат.', 'neutral'),
    'growth': Badge('growth', '🌱', 'Есть куда расти',
                    'Результат средний: скорость и понимание можно подтянуть.', 'neutral'),
    'rushing': Badge('rushing', '🏃', 'Поверхностное чтение',
                     'Читаете слишком быстро: слова проглатываются, суть ускользает. '
                     'Скорость без понимания не даёт эффекта.', 'growth'),
    'lost_thread': Badge('lost_thread', '🌪', 'Потеря нити',
                         'Скорость нормальная, но почти ничего не усвоено. '
                         'Попробуйте читать внимательнее.', 'growth'),
    'slow': Badge('slow', '🐌', 'Медленное чтение',
                  'Понимание среднее, а скорость низкая. Стоит поработать над темпом.', 'growth'),
    'practice': Badge('practice', '🧩', 'Нужна практика',
                      'Низкая скорость и слабое понимание. Начните с более лёгких текстов.', 'growth'),
    'no_focus': Badge('no_focus', '💤', 'Отсутствие концентрации',
                      'Текст не был усвоен. Попробуйте ещё раз без отвлекающих факторов.', 'growth'),
}


def get_badges(v, q):
    """v — скорость (слов/мин), q — понимание (0..100).
    Возвращает (главный бейдж, список дополнительных достижений)."""
    # Главный бейдж: первое совпадение по приоритету, последний вариант — запасной
    if q == 0:
        main = B['no_focus']
    elif v > 200 and q < 50:
        main = B['rushing']
    elif q < 50 and v >= 100:
        main = B['lost_thread']
    elif q < 50:
        main = B['practice']
    elif v < 120 and q == 100:
        main = B['thoughtful']
    elif v < 100:
        main = B['slow']
    elif 180 <= v <= 220 and q >= 80:
        main = B['golden']
    elif v > 200 and q >= 80:
        main = B['speed']
    elif 120 <= v <= 200 and q >= 60:
        main = B['balanced']
    elif v >= 120 and q >= 60:
        main = B['stable']
    else:
        main = B['growth']

    extras = []
    if q == 100:
        extras.append(B['accuracy'])
    return main, extras