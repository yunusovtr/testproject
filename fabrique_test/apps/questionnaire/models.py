from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.base import Model

class QuestionList(models.Model):
    poll_name = models.CharField('наименование опроса', max_length=100)
    description = models.TextField('описание', max_length=500)
    start_date = models.DateTimeField('дата старта')
    end_date = models.DateTimeField('дата окончания')
    active = models.BooleanField('активный')

class Question(models.Model):
    question_list = models.ForeignKey(QuestionList, on_delete=models.CASCADE)
    question_text = models.CharField('текст вопроса', max_length=250)
    class AnswerType:
        TEXT = 'TEXT'
        VARIANT = 'ONEVARIANT'
        MULTIVARIANT = 'MULTIVARIANT'
        CHOICES = (
            (TEXT, 'текстом'),
            (VARIANT, 'с выбором одного варианта'),
            (MULTIVARIANT, 'с выбором нескольких вариантов'),
        )
    answer_type = models.CharField('тип ответа', choices=AnswerType.CHOICES, default=AnswerType.TEXT, max_length=12)

class AnswerVariant(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField('текст ответа', max_length=50)

class Interview(models.Model):
    question_list = models.ForeignKey(QuestionList, on_delete=models.CASCADE)
    interviewee_id = models.IntegerField('код пользователя')
    start_date = models.DateTimeField('дата опроса')

class Answer(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField('текст ответа', max_length=50)