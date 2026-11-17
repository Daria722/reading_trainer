from django.conf import settings

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