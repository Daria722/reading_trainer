from django.contrib import admin
from .models import Text, Question, Answer, ReadingResult

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('title', 'word_count', 'difficulty', 'readability_score', 'created_at')
    readonly_fields = ('word_count', 'readability_score', 'difficulty')
    search_fields = ('title', 'content')

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'text')
    list_filter = ('text',)
    inlines = [AnswerInline]

@admin.register(ReadingResult)
class ReadingResultAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'words_per_minute', 'reading_time_seconds', 'completed_at')
    list_filter = ('completed_at',)