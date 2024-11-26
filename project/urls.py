
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from myapp.views import FileUploadView
from django.conf import settings
# from myapp.views import send_test_email
from myapp.views import MyGraphQLView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    # path('graphql/', csrf_exempt(MyGraphQLView.as_view(graphiql=True))),
    path('upload-file/', FileUploadView.as_view(), name="file_upload"),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('allauth.urls')),
    # path('send-email/', send_test_email, name='send_test_email'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# urls.py

# from django.urls import path, include
# from django.contrib import admin
# from graphene_django.views import GraphQLView
# from myapp.views import MyGraphQLView  # Import your custom GraphQLView
# from django.conf import settings
# from django.conf.urls.static import static
# from myapp.views import FileUploadView
# from django.views.decorators.csrf import csrf_exempt

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('graphql/', csrf_exempt(MyGraphQLView.as_view(graphiql=True))),  # Use MyGraphQLView here
#     path('upload-file/', FileUploadView.as_view(), name="file_upload"),
#     path('accounts/', include('allauth.urls')),
#     # path('send-email/', send_test_email, name='send_test_email'),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)