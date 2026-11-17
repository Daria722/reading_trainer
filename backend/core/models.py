from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Text(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название текста")
    content = models.TextField(verbose_name="Текст для чтения")
    word_count = models.PositiveIntegerField(verbose_name="Количество слов", default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def save(self, *args, **kwargs):
        # Автоматически считаем количество слов при сохранении
        if self.content:
            self.word_count = len(self.content.split())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Текст"
        verbose_name_plural = "Тексты"


class ReadingResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    text = models.ForeignKey(Text, on_delete=models.CASCADE, verbose_name="Прочитанный текст")
    reading_time_seconds = models.FloatField(verbose_name="Время чтения (сек)")
    words_per_minute = models.FloatField(verbose_name="Скорость (слов/мин)")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата прохождения")

    def __str__(self):
        return f"Результат: {self.words_per_minute} с/мин ({self.completed_at.strftime('%d.%m.%Y %H:%M')})"

    class Meta:
        verbose_name = "Результат чтения"
        verbose_name_plural = "Результаты чтения"