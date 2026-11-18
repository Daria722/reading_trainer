import random
import time

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Text, Question, Answer, ReadingResult
from .services import calculate_metrics

from django.db.models import Avg, Count
from .badges import get_badges


def text_list(request):
    texts = Text.objects.all()
    return render(request, 'text_list.html', {'texts': texts})


def text_read(request, pk):
    text = get_object_or_404(Text, pk=pk)
    # Начинаем чтение заново: сбрасываем всё от прошлых попыток
    for key in ('read_end', 'question_ids'):
        request.session.pop(key, None)
    request.session['read_start'] = time.time()
    request.session['read_text_id'] = text.pk
    return render(request, 'text_read.html', {'text': text})


def text_finish(request, pk):
    """Вызывается из JS при нажатии «Я прочитал(а)»: фиксирует конец чтения."""
    start = request.session.get('read_start')
    if start is None or request.session.get('read_text_id') != pk:
        return JsonResponse({'error': 'reading not started'}, status=400)
    if 'read_end' not in request.session:
        request.session['read_end'] = time.time()
    seconds = request.session['read_end'] - start
    return JsonResponse({'seconds': round(seconds, 1)})


def text_test(request, pk):
    text = get_object_or_404(Text, pk=pk)

    # Нельзя открыть тест, не прочитав текст
    if request.session.get('read_text_id') != text.pk or 'read_end' not in request.session:
        return redirect('text_read', pk=text.pk)

    if request.method == 'GET':
        # При обновлении страницы вопросы не должны меняться
        if 'question_ids' not in request.session:
            all_questions = list(text.questions.all())
            n = settings.QUESTIONS_PER_TEST
            selected = random.sample(all_questions, min(n, len(all_questions)))
            request.session['question_ids'] = [q.pk for q in selected]
        questions = Question.objects.filter(
            pk__in=request.session['question_ids']
        ).prefetch_related('answers')
        return render(request, 'test.html', {'text': text, 'questions': questions})

    # POST: проверяем ответы
    question_ids = request.session.get('question_ids', [])
    questions = Question.objects.filter(pk__in=question_ids, text=text)

    correct = 0
    for q in questions:
        user_answer_id = request.POST.get(f'q_{q.pk}')
        if user_answer_id and Answer.objects.filter(
            pk=user_answer_id, question=q, is_correct=True
        ).exists():
            correct += 1

    total = len(question_ids)
    reading_time = request.session['read_end'] - request.session['read_start']

    metrics = calculate_metrics(
        word_count=text.word_count,
        time_seconds=reading_time,
        correct=correct,
        total=total,
    )

    result = ReadingResult.objects.create(
        text=text,
        user=request.user if request.user.is_authenticated else None,
        reading_time_seconds=reading_time,
        words_per_minute=metrics['wpm'],
        questions_total=total,
        correct_answers=correct,
        comprehension=metrics['quality_percent'],
        norm_time_seconds=metrics['norm_time'],
        efficiency=metrics['efficiency'],
    )

    for key in ('read_start', 'read_end', 'read_text_id', 'question_ids'):
        request.session.pop(key, None)

    return redirect('result', pk=result.pk)

def result(request, pk):
    result = get_object_or_404(ReadingResult.objects.select_related('text'), pk=pk)
    badge, extra_badges = get_badges(result.words_per_minute, result.comprehension)

    # Сравнение с другими попытками на этом же тексте (текущая не учитывается)
    others = (ReadingResult.objects
              .filter(text=result.text, words_per_minute__lte=600)
              .exclude(pk=result.pk))
    stats = others.aggregate(
        attempts=Count('pk'),
        avg_wpm=Avg('words_per_minute'),
        avg_q=Avg('comprehension'),
        avg_e=Avg('efficiency'),
    )

    compare = []
    if stats['attempts']:
        pairs = [
            ('Скорость V', result.words_per_minute, stats['avg_wpm'], 'слов/мин', 'слов/мин'),
            ('Понимание Q', result.comprehension, stats['avg_q'], '%', 'п.п.'),
            ('Эффективность E', result.efficiency, stats['avg_e'], 'усв. слов/мин', 'усв. слов/мин'),
        ]
        for label, value, avg, unit, diff_unit in pairs:
            diff = value - avg
            compare.append({
                'label': label,
                'value': value,
                'avg': avg,
                'unit': unit,
                'diff_unit': diff_unit,
                'up': diff >= 0,
                'same': abs(diff) < 0.5,
                'abs_diff': abs(diff),
            })

    time_diff = abs(result.reading_time_seconds - result.norm_time_seconds)
    faster = result.reading_time_seconds <= result.norm_time_seconds

    return render(request, 'result.html', {
        'result': result,
        'badge': badge,
        'extra_badges': extra_badges,
        'stats': stats,
        'compare': compare,
        'time_diff': time_diff,
        'faster': faster,
    })