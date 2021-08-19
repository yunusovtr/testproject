from django.urls import include, path
from rest_framework import routers
from . import views

app_name = 'questionnaire'

router = routers.SimpleRouter()
router.register(r'question_set', views.QuestionSetViewSet)
router.register(r'question', views.QuestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('active_question_sets/', views.ActiveQuestionSetsView.as_view()),
    path('start_interview/', views.StartInterviewView.as_view()),
    path('interview_questions/<int:interview_id>/', views.InterviewQuestionsView.as_view()),
    path('register_answer/', views.RegisterAnswerView.as_view()),
    path('user_interviews/<int:interviewee_id>/', views.UserInterviewsView.as_view()),
]