from datetime import date, datetime
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from .models import Answer, Interview, QuestionSet, Question, AnswerVariant
from django.core.exceptions import PermissionDenied
import logging
logger = logging.getLogger('my_debuger')
# class QuestionSetSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField()
#     description = serializers.CharField()
#     start_date = serializers.DateTimeField()
#     end_date = serializers.DateTimeField()

class QuestionSetSerializer(serializers.ModelSerializer):
    """
    Сериализатор анкет
    """
    class Meta:
        model = QuestionSet
        fields = ['id', 'title', 'description', 'start_date', 'end_date']
        read_only_fields = ['id']
    
    def validate_start_date(self, value):
        """
        Для запрета изменения даты старта опроса после создания устанавливаем проверку значения 
        """
        if self.instance and self.instance.start_date != value:
            raise serializers.ValidationError(
                "Запрет на изменение даты старта опроса после создания."
            )
        return value

# class AnswerVariantSerializer(serializers.Serializer):
#     class Meta:
#         model = AnswerVariant
#         fields = ['answer_text']

# class VariantsListField(serializers.ListField):
#     child = serializers.CharField()

# class AnswerVariantsSerializer(serializers.ListSerializer):
#     def create(self, validated_data):
#         books = [Book(**item) for item in validated_data]
#         return Book.objects.bulk_create(books)

class AnswerVariantArraySerializer(serializers.SlugRelatedField):
    """
    Сериализатор варианта ответа для обработки через сериализатор вопроса
    """
    def to_internal_value(self, data):
        """
        Создаём затычку на валидации данных, чтобы без проблем осуществить добавление из 
        сериализатора вопросов простым массивом строк
        """
        return data

class QuestionWithAnswerVariantsSerializer(serializers.ModelSerializer):
    """
    Сериализатор вопросов с вариантами ответов для админа
    """
    answer_variants = AnswerVariantArraySerializer(many=True, slug_field='answer_text', \
        queryset=AnswerVariant.objects.all(), required=False)
    answer_type = serializers.ChoiceField(choices=Question.AnswerType.CHOICES, \
        default=Question.AnswerType.TEXT)
    class Meta:
        model = Question
        fields = ['id', 'question_set', 'question_text', 'answer_type', AnswerVariant.RELATED_NAME]
        read_only_fields = ['id']

    """
    Подменяем действия создания и обновления вопроса для обеспечения одновременного 
    добавления в базу вариантов ответов простым массивом строк в поле вопроса
    """
    def create(self, validated_data):
        answer_variants = validated_data.pop(AnswerVariant.RELATED_NAME, [])
        instance = Question.objects.create(**validated_data)
        answer_variants_array=[AnswerVariant(question=instance, answer_text=text) \
            for text in answer_variants]
        AnswerVariant.objects.bulk_create(answer_variants_array)
        return instance
    
    def update(self, instance, validated_data):
        edit_answer_variants = AnswerVariant.RELATED_NAME in validated_data
        answer_variants = validated_data.pop(AnswerVariant.RELATED_NAME, [])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        # Редактируем варианты ответов, если нужно
        if edit_answer_variants:
            instance.answer_variants.all().delete()
            answer_variants_array=[AnswerVariant(question=instance, answer_text=text) \
                for text in answer_variants]
            AnswerVariant.objects.bulk_create(answer_variants_array)
        return instance

# class UserAnswersFieldSerializer(serializers.SlugRelatedField):
#     class Meta:
#         #list_serializer_class = FilteredUserAnswerListSerializer
#         model = Answer
#     def to_representation(self, data):
#         #data = data.filter(user=self.context['request'].user, edition__hide=False)
#         data = data.filter(answer_text__isnull=True)
#         #data=None
#         return super(UserAnswersFieldSerializer, self).to_representation(data)

# class FilteredUserAnswerListField(serializers.ManyRelatedField):
#     child = serializers.SlugRelatedField(read_only=True, slug_field='answer_text')
#     def to_representation(self, data):
#         #data = data.filter(user=self.context['request'].user, edition__hide=False)
#         #data = data.filter(answer_text__isnull=True)
#         #data=None
#         return super(FilteredUserAnswerListField, self).to_representation(data)

class FilteredUserAnswerListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        #self.data
        #data = data.filter(interview=interview)
        #logger.error('%s\n\n' % type(self.parent.parent.parent.parent.instance))
        #logger.error('%s\n\n' % self.parent.parent.parent.parent.get_fields())
        logger.error('%s\n\n' % self.data)
        #data = data.filter(user=self.context['request'].user, edition__hide=False)
        return super(FilteredUserAnswerListSerializer, self).to_representation(data)

class FilteredUserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = FilteredUserAnswerListSerializer
        model = Answer
        fields = ["answer_text"]

class UserQuestionSerializer(serializers.ModelSerializer):
    #answers = UserAnswersFieldSerializer(many=True, read_only=True, slug_field='answer_text')
    answers = FilteredUserAnswerSerializer(many=True)
    #answers = serializers.SlugRelatedField(many=True, read_only=True, slug_field='answer_text')
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'answer_type', Answer.RELATED_NAME]
        read_only_fields = ['id']
    def to_representation(self, instance):
        return super().to_representation(instance)

class UserQuestionSetSerializer(serializers.ModelSerializer):
    questions = UserQuestionSerializer(many=True)
    class Meta:
        model = QuestionSet
        fields = ['id', 'title', 'description', 'start_date', 'end_date', Question.RELATED_NAME]

class InterviewQuestionsWithAnswersSerializer(serializers.ModelSerializer):
    question_set = UserQuestionSetSerializer()
    """
    Сериализатор вывода интервью с вопросами из его списка вопросов
    """
    class Meta:
        model = Interview
        fields = ['id', 'start_date', 'question_set']
    


class InterviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор интервью
    """
    class Meta:
        model = Interview
        fields = ['id', 'interviewee_id', 'loggedin_user', 'start_date', 'question_set']
        read_only_fields = ['id']




class InterviewQuestionAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['interview', 'question', 'answers']
# class InterviewSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     interviewee_id = serializers.IntegerField()
#     start_date = serializers.DateTimeField()
#     #question_list_id = serializers.DjangoModelField()
