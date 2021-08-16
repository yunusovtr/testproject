from rest_framework import serializers
from .models import QuestionSet

# class QuestionSetSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField()
#     description = serializers.CharField()
#     start_date = serializers.DateTimeField()
#     end_date = serializers.DateTimeField()

class QuestionSetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = QuestionSet
        fields = ['id', 'title', 'description', 'start_date', 'end_date']

class InterviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = QuestionSet
        fields = ['id', 'interviewee_id', 'loggedin_user', 'start_date', 'question_set']

# class InterviewSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     interviewee_id = serializers.IntegerField()
#     start_date = serializers.DateTimeField()
#     #question_list_id = serializers.DjangoModelField()