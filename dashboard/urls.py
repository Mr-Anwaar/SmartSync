from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='dashboard'),
    path('profile', views.profile, name='profile'),
    path('dashboard-trans', views.dashboard_trans, name='dashboard-trans'),

    # delete blog topic
    path('delete-blog-topic/<str:uniqueId>/', views.deleteBlogTopic, name='delete-blog-topic'),

    # Create blog from the topic
    path('generate-blog-from-topic/<str:uniqueId>/', views.createBlogFromTopic, name='generate-blog-from-topic'),

    # Content generation routes
    path('generate-content', views.contentTopic, name='generate-content'),
    path('view-content', views.viewContent, name='view-content'),


    # Blog generation routes
    path('generate-blog-topic', views.blogTopic, name='blog-topic'),
    path('generate-blog-sections', views.blogSections, name='blog-sections'),

    # saving the blog topic
    path('save-blog-topic/<str:blogTopic>/', views.saveBlogTopic, name='save-blog-topic'),
    path('use-blog-topic/<str:blogTopic>/', views.useBlogTopic, name='use-blog-topic'),

    path('view-generated-blog/<slug:slug>/', views.viewGeneratedBlog, name='view-generated-blog'),

    path('bulk_email_sender/', views.bulk_email_sender, name='bulk_email_sender'),
    path('deactivate_account/', views.deactivate_account, name='deactivate_account'),
]
