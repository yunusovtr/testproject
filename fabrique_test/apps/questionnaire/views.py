from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions
from .models import Answer, Interview, Question, QuestionSet, AnswerVariant, Answer
from .serializers import QuestionSetSerializer, QuestionWithAnswerVariantsSerializer,\
    InterviewSerializer, InterviewQuestionsWithAnswersSerializer
from rest_framework import serializers
from django.db.models import Q
from django.core.exceptions import PermissionDenied

class ActiveQuestionSetsView(APIView):
    """
    Представление для получения пользователем активных списков вопросов (анкет)
    """
    def get(self, request):
        """
        Используем GET для получения результата без входных параметров, отсеив неактивные опросы
        """
        now = datetime.now()
        active_question_sets = QuestionSet.objects.exclude(
            Q(end_date__lt = now) | Q(start_date__gt = now)
        )
        serializer = QuestionSetSerializer(active_question_sets, many=True)
        return Response(serializer.data)

class StartInterviewView(APIView):
    """
    Представление для старта прохождения опроса пользователем (интервью)

    Входные данные: question_set_id, interviewee_id
    question_set_id - id списка вопросов (анкеты)
    interviewee_id - id анонимного интервьюируемого

    interviewee_id = 0 - использовать аутентификацию Django
    interviewee_id != 0 - анонимное прохождение опроса
    """
    def post(self, request):
        """
        Используем POST для обработки запроса старта интервью
        """
        question_set_id = request.data.get('question_set_id')
        interviewee_id = request.data.get('interviewee_id')
        # Определяемся с анонимностью интервью
        if interviewee_id==0:
            if not request.user.is_authenticated:
                raise PermissionDenied
            interviewee_id = None
            loggedin_user = request.user
        else:
            loggedin_user = None
        # Не позволяем пользователю зарегистрировать интервью на неактивный опрос
        now = datetime.now()
        if not QuestionSet.objects.filter(
            Q(id=question_set_id, start_date__lt=now), Q(end_date__isnull=True)|Q(end_date__gt=now)
        ):
        #if question_set.start_date > now or (question_set.end_date and question_set.end_date < now):
            raise serializers.ValidationError(
                "Выбран неактивный опрос"
            )
        interview = Interview(interviewee_id=interviewee_id, loggedin_user=loggedin_user, \
            question_set=QuestionSet.objects.get(id=question_set_id), start_date=datetime.now())
        interview.save()
        serializer = InterviewSerializer(interview)
        return Response(serializer.data)

class InterviewQuestionsView(APIView):
    """
    Представление для получения вопросов зарегистрированного прохождения опроса (интервью)
    """
    def get(self, request, interview_id):
        """
        Показалось разумным, что пользователь должен иметь получить список вопросов по тому
        интервью, что он зарегистрировал
        """
        interview = Interview.objects.get(id=interview_id)
        question_set = interview.question_set
        questions = Question.objects.filter(question_set=question_set)
        serializer = QuestionWithAnswerVariantsSerializer(questions, many=True)
        return Response(serializer.data)

class RegisterAnswerView(APIView):
    """
    Представление регистрации ответа интервьюируемого
    """
    def post(self, request):
        question_id = request.data.get('question_id')
        interview_id = request.data.get('interview_id')
        answers = request.data.get('answers')
        # Проверяем соответствие пользователя, если интервью неанонимное
        interview = Interview.objects.get(id=interview_id)
        if interview.loggedin_user != None and interview.interviewee_id == None \
            and request.user != interview.loggedin_user:
            raise PermissionDenied
        # Проверяем наличие такого вопроса в проходимом опросе
        try:
            question = Question.objects.get(id=question_id, question_set=interview.question_set)
        except:
            raise serializers.ValidationError(
                "Можно отвечать на вопросы только из зарегистрированного опроса."
            )
        # Проверяем соответствие количества ответов
        if (question.answer_type == Question.AnswerType.TEXT or \
            question.answer_type == Question.AnswerType.ONEVARIANT) and len(answers) != 1:
            raise serializers.ValidationError(
                "При типе ответа TEXT или ONEVARIANT должен быть ровно один ответ."
            )
        # Проверяем соответствие ответа перечню вариантов ответа вопроса, если надо
        if question.answer_type == Question.AnswerType.ONEVARIANT or \
            question.answer_type == Question.AnswerType.MULTIVARIANT:
            answer_variants = AnswerVariant.objects.filter(question=question)\
                .values_list('answer_text', flat=True)
            for answer in answers:
                if answer not in answer_variants:
                    raise serializers.ValidationError(
                        "В вопросах с типом ответа ONEVARIANT или MULTIVARIANT можно использовать" +
                        " ответы только из приведенного переченя."
                    )
        # Удаляем повторяющиеся ответы
        not_dupl_answers = []
        for answer in answers:
            if answer not in not_dupl_answers:
                not_dupl_answers.append(answer)
        # Заменяем существующие ответы в этом интервью на этот вопрос
        Answer.objects.filter(interview__id=interview_id, question__id=question_id).delete()
        new_answers = [ Answer(question=question, interview=interview, answer_text=answer) for answer in not_dupl_answers ]
        Answer.objects.bulk_create(new_answers)
        return Response({ "answer": "ready" }) # ?????
            

class UserInterviewsView(APIView):
    """
    Представление для вывода пользовательских интервью
    """
    def get(self, request, interviewee_id):
        # Если interviewee_id = 0, то проверяем авторизацию
        if interviewee_id==0:
            if not request.user.is_authenticated:
                raise PermissionDenied
            else:
                interviews = Interview.objects.filter(loggedin_user=request.user)
        else:
            interviews = Interview.objects.filter(interviewee_id=interviewee_id)
        serializer = InterviewQuestionsWithAnswersSerializer(interviews, many=True)
        return Response(serializer.data)

class QuestionSetViewSet(viewsets.ModelViewSet):
    """
    CRUD для QuestionSet. Только для админов
    """
    queryset = QuestionSet.objects.all()
    serializer_class = QuestionSetSerializer
    permission_classes = [permissions.IsAdminUser]

class QuestionViewSet(viewsets.ModelViewSet):
    """
    CRUD для Question. Только для админов
    """
    queryset = Question.objects.all()
    serializer_class = QuestionWithAnswerVariantsSerializer
    permission_classes = [permissions.IsAdminUser]