# accounts/urls.py ĐÃ CHỈNH SỬA
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Social Auth URLs
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('profile/', views.profile, name='profile'),

    path('', views.home, name='home'),  # url liên kết với trang home
    path('home/', views.home_after_login, name='home_after_login'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),

    # Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/send_reminders/', views.trigger_send_reminders, name='trigger_send_reminders'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('skills/', views.skills, name='skills'),
    path('skills/certificate/<int:course_id>/', views.certificate_view, name='certificate_view'),

    # 🛠️ START: AI chat proxy - ĐÃ SỬA URL ĐỂ KHỚP VỚI JAVASCRIPT
    # Đổi tên từ 'api/ai_chat/' thành 'ai-analyze/'
    path('ai-analyze/', views.ai_chat_api, name='ai_chat_api'),
    # Nếu bạn vẫn muốn giữ status check, hãy sửa nó
    path('api/ai_chat/status/', views.ai_chat_status, name='ai_chat_status'),
    # 🛠️ END: AI chat proxy

    # Course routes
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    # Progress overview page
    path('progress/', views.progress_overview, name='progress_overview'),

    # Mock exams (thi thử)
    path('mock-exams/', views.mock_exams_list, name='mock_exams_list'),
    path('mock-exam/<int:exam_id>/take/', views.take_mock_exam, name='take_mock_exam'),
    path('mock-exam/<int:exam_id>/submit/', views.submit_mock_exam, name='submit_mock_exam'),
    path('scores/', views.scores_page, name='scores_page'),

    # Lesson routes
    path('course/<int:course_id>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/submit/', views.submit_lesson, name='submit_lesson'),
    path('lesson/<int:lesson_id>/retry/', views.retry_lesson, name='retry_lesson'),
]