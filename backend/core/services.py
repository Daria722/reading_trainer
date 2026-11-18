from django.conf import settings

import re

def calculate_metrics(word_count, time_seconds, correct, total):
    minutes = time_seconds / 60
    v = word_count / minutes if minutes > 0 else 0          # V, слов/мин
    q = correct / total if total else 0                      # Q, доля 0..1
    norm_time = word_count / settings.NORM_WPM * 60          # норматив, сек
    return {
        'wpm': round(v, 1),
        'quality_percent': round(q * 100, 1),
        'norm_time': round(norm_time, 1),
        'time_ratio': round(time_seconds / norm_time, 2) if norm_time else 0,
        'efficiency': round(v * q, 1),                       # E = V * Q
    }

# Пороги шкалы читабельности (формула Флеша, адаптация для русского языка)
READABILITY_EASY = 60
READABILITY_HARD = 30

RU_VOWELS = set('аеёиоуыэюя')
WORD_RE = re.compile(r'[A-Za-zА-Яа-яЁё]+(?:-[A-Za-zА-Яа-яЁё]+)*')


def count_syllables(word):
    """В русском языке число слогов равно числу гласных."""
    return max(1, sum(1 for ch in word.lower() if ch in RU_VOWELS))


def calculate_readability(text):
    """Индекс читабельности FR = 206.835 - 1.3*ASL - 60.1*ASW."""
    words = WORD_RE.findall(text)
    sentences = [s for s in re.split(r'[.!?…]+', text) if s.strip()]
    if len(words) < 20:
        return {'score': 0.0, 'difficulty': ''}
    if not words or not sentences:
        return {'score': 0.0, 'difficulty': ''}

    asl = len(words) / len(sentences)                                 # слов в предложении
    asw = sum(count_syllables(w) for w in words) / len(words)         # слогов в слове
    score = 206.835 - 1.3 * asl - 60.1 * asw

    if score >= READABILITY_EASY:
        difficulty = 'easy'
    elif score >= READABILITY_HARD:
        difficulty = 'medium'
    else:
        difficulty = 'hard'
    return {'score': round(score, 1), 'difficulty': difficulty}