from django.db import models
from django.conf import settings

# Create your models here.
from django.contrib.auth.models import User
from .services import calculate_readability

class Text(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Лёгкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
    ]
    title = models.CharField(max_length=255, verbose_name="Название текста")
    content = models.TextField(verbose_name="Текст для чтения")
    word_count = models.PositiveIntegerField(verbose_name="Количество слов", default=0)
    readability_score = models.FloatField(default=0, verbose_name="Индекс читабельности")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES,
                                  blank=True, verbose_name="Сложность")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def save(self, *args, **kwargs):
        if self.content:
            self.word_count = len(self.content.split())
            r = calculate_readability(self.content)
            self.readability_score = r['score']
            self.difficulty = r['difficulty']
        super().save(*args, **kwargs)

    @property
    def reading_minutes(self):
        """Расчётное время чтения по нормативу, минимум 1 минута."""
        return max(1, round(self.word_count / settings.NORM_WPM))    

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Текст"
        verbose_name_plural = "Тексты"

class Question(models.Model):
    text = models.ForeignKey(Text, on_delete=models.CASCADE,
                             related_name='questions', verbose_name="Текст")
    question_text = models.CharField(max_length=500, verbose_name="Вопрос")

    def __str__(self):
        return self.question_text

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 related_name='answers', verbose_name="Вопрос")
    answer_text = models.CharField(max_length=300, verbose_name="Вариант ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Верный")

    def __str__(self):
        return self.answer_text

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"

class ReadingResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    text = models.ForeignKey(Text, on_delete=models.CASCADE, verbose_name="Прочитанный текст")
    reading_time_seconds = models.FloatField(verbose_name="Время чтения (сек)")
    words_per_minute = models.FloatField(verbose_name="Скорость (слов/мин)")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата прохождения")
    questions_total = models.PositiveIntegerField(default=0, verbose_name="Всего вопросов")
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="Верных ответов")
    comprehension = models.FloatField(default=0, verbose_name="Понимание Q (%)")
    norm_time_seconds = models.FloatField(default=0, verbose_name="Норматив времени (сек)")
    efficiency = models.FloatField(default=0, verbose_name="Эффективность E")

    def __str__(self):
        return f"Результат: {self.words_per_minute} с/мин ({self.completed_at.strftime('%d.%m.%Y %H:%M')})"

    class Meta:
        verbose_name = "Результат чтения"
        verbose_name_plural = "Результаты чтения"