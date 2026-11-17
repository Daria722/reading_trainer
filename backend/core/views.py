import random
import time
from datetime import datetime

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404

from .models import Text, Question, Answer, ReadingResult
from .services import calculate_metrics


def text_list(request):
    texts = Text.objects.all()
    return render(request, 'text_list.html', {'texts': texts})


def text_read(request, pk):
    text = get_object_or_404(Text, pk=pk)
    # Сохраняем время старта в сессию
    request.session['read_start'] = time.time()
    request.session['read_text_id'] = text.pk
    return render(request, 'text_read.html', {'text': text})


def text_test(request, pk):
    text = get_object_or_404(Text, pk=pk)

    if request.method == 'GET':
        # Случайный выбор N вопросов
        all_questions = list(text.questions.all())
        n = settings.QUESTIONS_PER_TEST
        selected = random.sample(all_questions, min(n, len(all_questions)))
        request.session['question_ids'] = [q.pk for q in selected]
        return render(request, 'test.html', {
            'text': text,
            'questions': selected,
        })

    # POST — проверяем ответы
    question_ids = request.session.get('question_ids', [])
    questions = Question.objects.filter(pk__in=question_ids)

    correct = 0
    for q in questions:
        user_answer_id = request.POST.get(f'q_{q.pk}')
        if user_answer_id:
            try:
                ans = Answer.objects.get(pk=user_answer_id)
                if ans.is_correct:
                    correct += 1
            except Answer.DoesNotExist:
                pass

    total = len(question_ids)
    reading_time = time.time() - request.session.get('read_start', time.time())

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

    request.session.pop('read_start', None)
    request.session.pop('question_ids', None)

    return redirect('result', pk=result.pk)


def result(request, pk):
    result = get_object_or_404(ReadingResult, pk=pk)
    return render(request, 'result.html', {'result': result})