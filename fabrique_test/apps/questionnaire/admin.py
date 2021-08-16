from django.contrib import admin
from .models import QuestionSet, Question, AnswerVariant, Interview, Answer

admin.site.register(QuestionSet)
admin.site.register(Question)
admin.site.register(AnswerVariant)
admin.site.register(Interview)
admin.site.register(Answer)