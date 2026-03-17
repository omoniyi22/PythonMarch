from django.urls import path
from . import views

urlpatterns = [
    # Home/Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Student URLs
    path('students/', views.student_list, name='student_list'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    
    # Course URLs
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/add/', views.course_add, name='course_add'),
    
    # Enrollment URLs
    path('enroll/', views.enroll_student, name='enroll_student'),
    path('grade/<int:pk>/update/', views.update_grade, name='update_grade'),
]