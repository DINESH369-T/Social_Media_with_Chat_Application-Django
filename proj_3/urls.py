from django.urls import path
from . import views 


urlpatterns=[
    path('',views.login_view,name='login'),
    path('home/',views.home,name='home'),
    path('register/',views.register_view,name='register'),
    path('logout/',views.logout_view,name='logout'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comments/<int:post_id>/', views.comment_list, name='comment_list'),
    path('comment/add/<int:post_id>/', views.add_comment, name='add_comment'),
    path("post/delete/<int:post_id>/", views.delete_post, name="delete_post"),
    path("post/edit/<int:post_id>/", views.edit_post, name="delete_post"),
    path("edit-profile/", views.update_profile_image, name="edit_profile_image"),
    path('api/create-post/',views.create_post,name="create_post"),
    path('api/delete-post/',views.delete_post_api,name="delete_post"),
    path('api/edit-post/', views.edit_post_api, name="edit_post"),
    path('api/posts-by-user/', views.posts_by_user, name="posts_by_user"),

]