from django.urls import path
from . import views
from .views import SaveWordResultsView

urlpatterns = [
    path('save/', views.save_game_result, name='save_game_result'),
    path('save-word-results/', SaveWordResultsView.as_view(), name='save_word_results'),

]