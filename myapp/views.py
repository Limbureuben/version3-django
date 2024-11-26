import datetime
from django.http import JsonResponse
from django.shortcuts import render
from graphql import GraphQLError
import jwt
import requests
from projectBuilders.projectBuilders import UserBuilder, TicketService, UserProfileBuilder
from project_dto.project import *
from .models import *
import graphene
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from project_dto.Response import *

from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.views import APIView # type: ignore
from .serializer import FileSerializer
from .models import Files
from rest_framework.response import Response # type: ignore
from graphene import Mutation, Boolean, String
from django.core.exceptions import PermissionDenied
import base64
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


    
class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserRegistrationObject)
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        input = UserRegistrationInputObject(required=True)
        
    def mutate(self, info, input):
        
        username = input.username
        email = input.email
        password = input.password
        password_confirm = input.password_confirm
        
        ##check if the user exist
        if User.objects.filter(username=username).exists():
            return RegisterUser(success=False, message="username alredy exists")
        
        ##check if the email exist
        if User.objects.filter(email=email).exists():
            return RegisterUser(success=False, message="Email alredy exists")
        
        if password != password_confirm:
            return RegisterUser(success=False, message="Passwords do not match")
        
        user = User(username=username, email=email)
        user.set_password(password)
        user.is_superuser = False
        user.is_staff = False
        user.save()
        return RegisterUser(
            user = UserRegistrationObject(id=user.id, username=user.username, email=user.email),
            success = True,
            message = "Registration successfully"
        )
        
        
class LoginUser(graphene.Mutation):
    user = graphene.Field(UserLoginObject)
    success = graphene.Boolean()
    message = graphene.String()

    
    class Arguments:
        input = UserLoginInputObject(required=True)
        
    def mutate(self, info, input):
        
       username = input.username
       password = input.password
       
       try:
           # Authenticate and log in the user
            result = UserBuilder.login_user(username, password)
            user = result['user']
            
            # angalia kama  ni superuser au hapana
            is_superuser = user.is_superuser
            
            
            return LoginUser(
                user = UserLoginObject(
                    id = user.id,
                    username = user.username,
                    email = user.email,
                    refresh_token = result['refresh_token'],
                    access_token = result['access_token'],
                    isSuperuser=is_superuser
                    
                ),
                success=True,
                message="Login successful",
                
            )
       except PermissionDenied as e:
           return LoginUser(success=False, message=str(e))


        
class RegisterEvent(graphene.Mutation):
    class Arguments:
        input = EventRegistrationInputObject(required=True)
        # file = Upload(required=True)
    
    event = graphene.Field(EventRegistrationObject)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            # image_file = input.image if 'image' in input else None
            
            event_instance = Event.objects.create(
                event_username = input.event_username,
                event_name = input.event_name,
                event_date=input.event_date,
                event_location=input.event_location,
                event_category=input.event_category
                # image = image_file
            )
            
            # Create the event response object
            event_response = EventRegistrationObject(
                event_username=event_instance.event_username,
                event_name=event_instance.event_name,
                event_date=event_instance.event_date,
                event_location=event_instance.event_location,
                event_category=event_instance.event_category,
                # image = event_instance.image.url if event_instance.image else None
            )
            
            return RegisterEvent(
                event=event_response,
                success=True,
                message="Event registered successfully."
            )
            
        except Exception as e:
            # Handle exceptions and return error message
            return RegisterEvent(
                event=None,
                success=False,
                message=str(e)  # or a custom error message
            )


class UpdateEvent(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event = graphene.Field(EventRegistrationObject)
    
    class Arguments:
        input = EventUpdateInputObject(required=True)
        
    def mutate(self, info, input):
        try:
            #chukua events kwa ID zake
            event_instance = Event.objects.get(id=input.id)
            
            #then update the event
            if input.event_username is not None:
                event_instance.event_username = input.event_username
                
            if input.event_name is not None:
                event_instance.event_name = input.event_name
                
            if input.event_date is not None:
                event_instance.event_date = input.event_date
                
            if input.event_location is not None:
                event_instance.event_location = input.event_location
                
            if input.event_category is not None:
                event_instance.event_category = input.event_category
                
                ##then save the updates
            event_instance.save()
            
            
            #the create a response event
            event_response = EventRegistrationObject(
                id = event_instance.id,
                event_username = event_instance.event_username,
                event_name = event_instance.event_name,
                event_date = event_instance.event_date,
                event_location = event_instance.event_location,
                event_category = event_instance.event_category
            )
            
            return UpdateEvent(
                event = event_response,
                success = True,
                message = "Event update successfully"
            )
            
        except Event.DoesNotExist:
            return UpdateEvent(
                event=None,
                success=False,
                message='Event not found'
            )
            
        except Exception as e:
            
            #handle chochote kitakachotokea
            return UpdateEvent(
                event=None,
                success=False,
                message=str(e)
            )
    

class DeleteEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        try:
            event = Event.objects.get(pk=id)
            event.delete()
            return DeleteEvent(
                success = True,
                message = 'Event delete successfully!'
            )
        except Event.DoesNotExist:
            return DeleteEvent(success=False, message='Event not found')
            


class DeleteApplication(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        try:
            application = EventApplication.objects.get(pk=id)
            application.delete()
            return DeleteApplication(
                success = True,
                message = 'Event Delete Successfully'
            )
        except EventApplication.DoesNotExist:
            return DeleteApplication(success=False, message='Failed to delete event')
        
        
        

class ApplicationEvent(graphene.Mutation):
    class Arguments:
        input = EventApplicationInputObject(required=True)
        
    success = Boolean()
    message = String()
    application = graphene.Field(EventApplicationObject)
    ticket_pdf = graphene.String()
    
    def mutate(self, info, input):
        application = UserBuilder.application_event(
            name=input.name,
            email=input.email,
            status=input.status,
            event_id=input.event_id
        )
        
        if application:
            ticket_id, encoded_pdf = TicketService.generate_ticket(application)
            
            application.ticket_id = ticket_id
            application.save()
            
            
            return ApplicationEvent(
                success=True,
                message='Application successfully created with ticket generated',
                application=application,
                ticket_pdf=encoded_pdf
            )
        else:
            return ApplicationEvent(
                success=False,
                message="Failed to complete application",
                application=None,
                ticket_pdf=None,
            )
            
            
class RegisterBook(graphene.Mutation):
    class Arguments:
        input = RegisterBookInputObject(required=True)
        
    success = graphene.Boolean()
    message = graphene.String()
    book = graphene.Field(RegisterBookObject)
    
    def mutate(self, info, input):
        title = input.input,
        author = input.author,
        publisher = input.publisher,
        publication_date = input.publication_date
        
        
        
        
        
            
    # def send_confrimation_email(self, email, name, ticket_pdf):
    #     subject = 'Your Event Application Confirmation'
    #     message = f'Dear {name},\n\nYour application has been successfully submitted.\n\nYou can download your ticket here: {ticket_pdf}\n\nThank you for your application!'
    #     from_email = settings.EMAIL_HOST_USER
    #     recipient_list = [email]
        
    #     try:
    #         send_mail(subject, message, from_email, recipient_list)
    #     except Exception as e:
    #         print(f'Error sending email: {e}')


## ntaitumia endapo companyreuben@gmail.com itakubal
# def send_confirmation_email(email, name, ticket_pdf):
#     subject = 'Your Event Application Confirmation'
#     message = f'Dear {name},\n\nYour application has been successfully submitted.\n\nYou can download your ticket here: {ticket_pdf}\n\nThank you for your application!'
#     from_email = settings.EMAIL_HOST_USER  # Use the configured email host user
#     recipient_list = [email]

#     try:
#         send_mail(subject, message, from_email, recipient_list)
#     except Exception as e:
#         print(f'Error sending email: {e}')
        

# class ApplicationEvent(graphene.Mutation):
#     class Arguments:
#         input = EventApplicationInputObject(required=True)
        
#     success = Boolean()
#     message = String()
#     application = graphene.Field(EventApplicationObject)
#     ticket_pdf = graphene.String()
    
#     def mutate(self, info, input):
#         application = UserBuilder.application_event(
#             name=input.name,
#             email=input.email,
#             status=input.status,
#             event_id=input.event_id
#         )
        
#         if application:
#             ticket_id, encoded_pdf = TicketService.generate_ticket(application)
            
#             application.ticket_id = ticket_id
#             application.save()

#             # Sending email logic
#             self.send_confirmation_email(application.email, application.name, encoded_pdf)

#             return ApplicationEvent(
#                 success=True,
#                 message='Application successfully created with ticket generated',
#                 application=application,
#                 ticket_pdf=encoded_pdf
#             )
#         else:
#             return ApplicationEvent(
#                 success=False,
#                 message="Failed to complete application",
#                 application=None,
#                 ticket_pdf=None
#             )

class UserProfileQuery(graphene.ObjectType):
    user = graphene.Field(UserProfileObject, id=graphene.ID())

    def resolve_user(self, info, id):
        try:
            # Fetch the user from the database using the ID
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None
        
# class ResetPassword(graphene.Mutation):
#     class Arguments:
#         input = ResetPasswordInputObject(required=True)
        
#     output = PasswordResetResponse
    
#     @staticmethod
#     def mutate(root, info, input):
#         user = info.context.get('user')
        
        
#         if not user:
#             print("No user found in context.")
#             return PasswordResetResponse(
#             success=False,
#             message="User is not authenticated."
#         )
        
#         if not user.is_authenticated:
#             return PasswordResetResponse(
#                 success = False,
#                 message = 'User not authenticated'
#             )
            
#         result = UserProfileBuilder.reset_user_password(
#             user = user,
#             old_password = input.old_password,
#             new_password = input.new_password,
#             new_password_confirm = input.new_password_confirm
#         )
        
#         return PasswordResetResponse(success=result['success'], message=result['message'])

# views.py
from graphene_django.views import GraphQLView # type: ignore
from .utils import authenticate_user

class MyGraphQLView(GraphQLView):
    def get_context(self, request):
        context = super().get_context(request)
        token = request.headers.get('Authorization', None)
        if token:
            user = authenticate_user(token)  # Authenticate using JWT
            context.user = user
        return context



    
    

from graphql_jwt.decorators import login_required # type: ignore
from .utils import reset_user_password
    
class ResetPassword(graphene.Mutation):
    
    class Arguments:
        input = ResetPasswordInputObject(required=True)
        
    success = graphene.Boolean()
    message = graphene.String()
        
    @login_required
    def mutate(self, info, input):
        user = info.context.user
        old_password = input.old_password
        new_password = input.new_password
        new_password_confirm = input.new_password_confirm
        
        
        result = reset_user_password(user, old_password, new_password, new_password_confirm)
        
        return ResetPassword(success=result['success'], message=result['message'])
    


class GitHubOAuthMutation(graphene.Mutation):
    class Arguments:
        code = graphene.String(required=True)

    success = graphene.Boolean()
    error = graphene.String()
    token = graphene.String()  # Add token to return the access token to the client

    def mutate(self, info, code):
        if not code:
            return GitHubOAuthMutation(success=False, error='Code is required')

        # Step 1: Get access token from GitHub
        try:
            token_response = requests.post(
                'https://github.com/login/oauth/access_token',
                data={
                    'client_id': settings.GITHUB_CLIENT_ID,
                    'client_secret': settings.GITHUB_CLIENT_SECRET,
                    'code': code,
                },
                headers={'Accept': 'application/json'}
            )
            token_response.raise_for_status()
        except requests.RequestException as e:
            return GitHubOAuthMutation(success=False, error=f'Error getting token: {str(e)}')

        token_data = token_response.json()
        if 'access_token' not in token_data:
            return GitHubOAuthMutation(success=False, error='Failed to retrieve access token')

        access_token = token_data['access_token']

        # Step 2: Fetch user info from GitHub
        try:
            user_response = requests.get(
                'https://api.github.com/user',
                headers={'Authorization': f'token {access_token}'}
            )
            user_response.raise_for_status()
        except requests.RequestException as e:
            return GitHubOAuthMutation(success=False, error=f'Error fetching user data: {str(e)}')

        user_data = user_response.json()
        if 'login' not in user_data:
            return GitHubOAuthMutation(success=False, error='Incomplete user data')

        # Step 3: Create or fetch user from the database
        user, created = User.objects.get_or_create(
            username=user_data['login'],
            defaults={'email': user_data.get('email', 'no-email@example.com')}  # Default email if None
        )

        # Return success with the access token
        return GitHubOAuthMutation(success=True, error=None, token=access_token)

        
        
class CategoryQuery(graphene.ObjectType):
    categories = graphene.List(CategoryObject)
    
    def resolve_categories(self, info):
        return Category.objects.all()

class EventQuery(graphene.ObjectType):
    all_events = graphene.List(EventObject)
    
    def resolve_all_events(self, info):
        return Event.objects.all()
    
class EventCountQuery(graphene.ObjectType):
    event_count = graphene.Int(description="Nipate number zote za event")
    
    def resolve_event_count(self, info):
        return Event.objects.count()


class EventUserQuery(graphene.ObjectType):
    eventuser_count = graphene.Int(description='Total applications')
    
    def resolve_eventuser_count(self, info):
        return EventApplication.objects.count()
    
class EventApplicationQuery(graphene.ObjectType):
    all_application = graphene.List(EventApplicationObject)
    
    def resolve_all_application(self, info):
        return EventApplication.objects.all()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

class FileUploadView(APIView):
    def post(self, request):
        file = request.FILES.get("file")
        
        if file:
            try:
                saved_file = Files.objects.create(file=file)
                return Response({"error": False, "data": FileSerializer(saved_file).data})
            except Exception as e:
                return Response({"error": True, "message": str(e)})
            
        return Response({"error": True, "message": "No file uploaded"})
    
    def get(self, request):
        try:
            data = Files.objects.all()
            return Response(FileSerializer(instance=data, many=True).data)
        except Exception as e:
            return Response({"error": True, "message": str(e)})















































































































# @csrf_exempt
# def execute_code(request):
#     if request.method == 'POST':
#         try:
#             # Parse the JSON data
#             data = json.loads(request.body)
#             temperature = data.get('temperature')
#             humidity = data.get('humidity')

#             # Print the temperature and humidity to the console
#             print(f"Temperature: {temperature} °C")
#             print(f"Humidity: {humidity} %")

#             # Save data to the Weather model
#             if temperature is not None and humidity is not None:
#                 Weather.objects.create(
#                     temperature=int(temperature),  # Ensure it's stored as an integer
#                     humidity=int(humidity)         # Ensure it's stored as an integer
#                 )
#                 return JsonResponse({'status': 'success', 'message': 'Data received and stored successfully'}, status=200)
#             else:
#                 return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
#         except json.JSONDecodeError:
#             return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
#         except ValueError:
#             return JsonResponse({'status': 'error', 'message': 'Invalid data type'}, status=400)
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# from rest_framework import viewsets
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from rest_framework import viewsets
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from .models import Weather
# # from .serializers import WeatherSerializer
# # import pandas as pd
# from rest_framework.views import APIView
# from .serializer import FileSerializer
# from .models import Files

# from rest_framework.parsers import FileUploadParser
# @api_view(['GET'])
# def hourly_average_summary(request):
#     data = Weather.objects.all().order_by('created_at')
#     serializer = WeatherSerializer(data, many=True)
#     df = pd.DataFrame(serializer.data)
#     df['created_at'] = pd.to_datetime(df['created_at'])
#     df.set_index('created_at', inplace=True)
#     df_resampled = df.resample('10T').agg({
#         'temperature': 'mean',
#         'humidity': 'mean'
#     }).reset_index()
#     df_resampled.fillna(0, inplace=True)  # Replace NaN values with 0
    
#     df_resampled.replace([float('inf'), float('-inf')], 0, inplace=True)  # Replace infinite values with 0
    
#     # Delete rows where either 'Temperature Average' or 'Humidity Average' is 0
#     df_resampled = df_resampled[(df_resampled['temperature'] != 0) & (df_resampled['humidity'] != 0)]
#     df_resampled.replace([float('inf'), float('-inf')], 0, inplace=True)  # Replace infinite values with 0
#     df_resampled.columns = ['Date', 'Temperature Average', 'Humidity Average']
#     response_data = df_resampled.to_dict(orient='records')
#     return Response(response_data)



# @api_view(['GET'])
# def current_weather(request):
#     try:
#         # Retrieve the latest weather record
#         latest_weather = Weather.objects.latest('created_at')
        
#         # Serialize the latest weather record
#         serializer = WeatherSerializer(latest_weather)
        
#         # Return the serialized data
#         return Response(serializer.data)
    
#     except Weather.DoesNotExist:
#         # If no weather data is available, return an empty response or an error message
#         return Response({"error": "No weather data available."}, status=404)
    
    
