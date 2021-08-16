from datetime import datetime
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework import viewsets, permissions
from .models import Interview, QuestionSet
from .serializers import QuestionSetSerializer, InterviewSerializer

class ActiveQuestionSetsView(APIView):
    def get(self, request):
        active_question_sets = QuestionSet.objects.exclude(end_date__lt = datetime.now())
        serializer = QuestionSetSerializer(active_question_sets, many=True)
        return Response({"active_question_sets": serializer.data})

class StartInterviewView(APIView):
    def post(self, request):
        try:
            question_set_id = request.data.get('question_set_id')
            interviewee_id = request.data.get('interviewee_id')
            interview = Interview(interviewee_id=interviewee_id, question_set=QuestionSet.objects.get(id=question_set_id), \
                start_date=datetime.now())
            interview.save()
            serializer = InterviewSerializer(interview)
            return Response({"interview": serializer.data})
        except:
            return Response({"error": True})

class QuestionSetViewSet(viewsets.ModelViewSet):
    """
    Только для админов
    """
    queryset = QuestionSet.objects.all()
    serializer_class = QuestionSetSerializer
    permission_classes = [permissions.IsAdminUser]