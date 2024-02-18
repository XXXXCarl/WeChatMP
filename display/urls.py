from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register),
    path('list', views.displayMissingFamilyPostList, name='list'),
    path('info', views.displayMissingFamilyPostInfo, name='info'),
    path('release', views.postRelease, name='release'),
    path('user_login', views.user_login, name='user_login'),
    path('comment', views.commentControl, name='comment'),
    path('interact', views.postInteraction, name='interact'),
    path('userprofile', views.follow_or_unfollow_user, name='userprofile'),
    path('postquery', views.postQuery, name='post_query'),
    path('usermodify', views.modify_personal_info, name='modify_personal_info'),
    path('feedback', views.submit_feedback, name='feedback'),
    path('volunteer', views.apply_volunteer, name='volunteer'),
    path('search', views.searchMissingFamilyPost, name='search'),
    path('verification', views.apply_verification, name='verification'),
    path('get_note', views.get_notifications, name='get_note')
]