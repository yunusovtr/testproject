from django.urls import include, path
from rest_framework import routers
from . import views

app_name = 'questionnaire'

router = routers.DefaultRouter()
router.register(r'question_list', views.QuestionSetViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('active_question_sets/', views.ActiveQuestionSetsView.as_view()),
    path('start_interview/', views.StartInterviewView.as_view()),
]