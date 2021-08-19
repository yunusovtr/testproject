from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.base import Model

class QuestionSet(models.Model):
    """
    Анкета - список вопросов
    """
    title = models.CharField('наименование опроса', max_length=100)
    description = models.TextField('описание', max_length=500)
    start_date = models.DateTimeField('дата старта')
    end_date = models.DateTimeField('дата окончания', null=True, blank=True)
    def __str__(self):
        return self.title

class Question(models.Model):
    """
    Конкретный вопрос в конкретной анкете
    """
    RELATED_NAME = 'questions'
    question_set = models.ForeignKey(QuestionSet, related_name=RELATED_NAME, on_delete=models.CASCADE)
    question_text = models.CharField('текст вопроса', max_length=250)
    class AnswerType:
        TEXT = 'TEXT'
        ONEVARIANT = 'ONEVARIANT'
        MULTIVARIANT = 'MULTIVARIANT'
        CHOICES = (
            (TEXT, 'текстом'),
            (ONEVARIANT, 'с выбором одного варианта'),
            (MULTIVARIANT, 'с выбором нескольких вариантов'),
        )
    answer_type = models.CharField('тип ответа', choices=AnswerType.CHOICES, default=AnswerType.TEXT, max_length=12)
    def __str__(self):
        return self.question_text

class AnswerVariant(models.Model):
    """
    Вариант ответа в конкретном вопросе
    """
    RELATED_NAME='answer_variants'
    question = models.ForeignKey(Question, related_name=RELATED_NAME, on_delete=models.CASCADE)
    answer_text = models.CharField('текст ответа', max_length=50)
    def __str__(self):
        return self.answer_text

class Interview(models.Model):
    """
    Интервью, проводимое с конкретным интервьюируемым по конкретной анкете
    """
    question_set = models.ForeignKey(QuestionSet, on_delete=models.CASCADE)
    loggedin_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    interviewee_id = models.IntegerField('код пользователя', default=None, blank=True, null=True)
    start_date = models.DateTimeField('дата опроса')

class Answer(models.Model):
    """
    Ответ на вопрос в конкретном интервью (может быть несколько на один вопрос)
    """
    RELATED_NAME='answers'
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name=RELATED_NAME, on_delete=models.CASCADE)
    # для единообразия по типам ответов сохраняем только текстовый ответ без ссылки на вариант
    answer_text = models.CharField('текст ответа', max_length=50)
    def __str__(self):
        return self.answer_text