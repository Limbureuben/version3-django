import graphene
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from project_dto.project import *
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class UserBuilder:
    @staticmethod
    def register_user(username, email, password, password_confirm):
        if password != password_confirm:
            raise ValidationError("Password do not match")
        
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        return user
    
    @staticmethod
    def login_user(username, password):
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError('Invalid username or password')
        
        # Create tokens for the authenticated user
        refresh = RefreshToken.for_user(user)
        return {
            'user': user,
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        }
        
    @staticmethod
    def create_event(event_username, event_name, event_date, event_location, event_category):
        try:
            event = Event(
                event_username = event_username,
                event_name = event_name,
                event_date = event_date,
                event_location = event_location,
                event_category = event_category
                # image = image
            )
            event.save()
            return event
        except Exception as e:
            print("Error creating event: {e}")
            return None
        
        
    @staticmethod
    def update_event(event_id, event_username=None, event_name=None, event_date=None, event_location=None, event_category=None):
        try:
            event = Event.objects.get(id=event_id)
            
            #update the provide fields
            if event_username is not None:
                event.event_username = event_username
            if event.event_name is not None:
                event.event_name = event_name
            if event.event_date is not None:
                event.event_date = event_date
            if event.event_location is not None:
                event.event_location = event_location
                
            event.save()
            return event
        except Event.DoesNotExist:
            print(f"Event with ID {event_id} does not exist.")
            return None
        except Exception as e:
            print(f"Error updating event: {e}")
            return None
    
    
    
    @staticmethod
    def application_event(name, email, status, event_id):
        try:
            event_application = EventApplication(
                name = name,
                email = email,
                status = status,
                event_id = event_id
            )
            
            event_application.save()
            
            return event_application
        except Exception as e:
            print('Error creating event application: {e}')
            return None



class UserProfileBuilder:
    
    @staticmethod
    def create_user_profile(user: User) ->UserProfileObject:
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
        
    @staticmethod
    def reset_user_password(user, old_password, new_password, new_password_confirm):
        try:
            # Check if the new passwords match
            if new_password != new_password_confirm:
                return {
                    'success': False,
                    'message': 'New password does not match confirmation'
                }
                
            # Verify the old password
            if not user.check_password(old_password):
                return {
                    'success': False,
                    'message': 'The old password is incorrect'
                }
                
            # Validate the new password against Django's password rules
            validate_password(new_password, user)
            
            # Set and save the new password
            user.set_password(new_password)
            user.save()
            
            return {
                'success': True,
                'message': 'Password reset successfully'
            }
        
        except ValidationError as e:
            # Handle password validation errors (e.g., too short, too common, etc.)
            return {
                'success': False,
                'message': ' '.join(e.messages)  # Join multiple validation error messages
            }
            
        except Exception as e:
            # General exception handling
            print(f"Error resetting password: {e}")
            return {
                'success': False,
                'message': 'An error occurred during password reset'
            }
            





























        


import base64
from io import BytesIO
from django.contrib.staticfiles import finders
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import qrcode
from PIL import Image
import tempfile
import os

class TicketService:
    @staticmethod
    def generate_ticket(application):
        ticket_id = f"TKT-{application.id}"

        # Data to encode in QR code
        qr_data = f"Ticket ID: {ticket_id}\nEvent: {application.event.event_name}\nName: {application.name}\nEmail: {application.email}\nStatus: {application.status}"

        # Generate QR code and save to temporary file
        qr = qrcode.make(qr_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as qr_temp_file:
            qr_temp_file_name = qr_temp_file.name
            qr.save(qr_temp_file_name)

        # Create a PDF in memory
        pdf_buffer = BytesIO()

        # Define the size of the ticket exactly
        ticket_width = 595  # width in points (landscape A5 width)
        ticket_height = 420  # height in points (landscape A5 height)
        
        # Create a canvas with the exact size of the ticket
        pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=(ticket_width, ticket_height))

        # Load university logo image from static files
        logo_path = finders.find("myapp/images/logo1.png")  # Adjust the path as needed
        if logo_path:
            # Open the logo image and handle transparency if present
            logo_image = Image.open(logo_path)
            # Ensure the logo image has transparency (RGBA)
            if logo_image.mode != 'RGBA':
                logo_image = logo_image.convert('RGBA')

            # Resize the logo to fit the ticket's design
            logo_image = logo_image.resize((120, 120))  # Increased size (120x120)

            # Now, we'll replace transparent areas with the ticket's background color
            # Create a new image with the same size, filling it with the lightgrey color
            background_color = (211, 211, 211, 255)  # lightgrey in RGBA (with full opacity)
            new_image = Image.new('RGBA', logo_image.size, background_color)
            new_image.paste(logo_image, (0, 0), logo_image)  # Paste the logo onto the background

            # Save the new logo to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as logo_temp_file:
                logo_temp_file_name = logo_temp_file.name
                new_image.save(logo_temp_file_name, format="PNG")

            # Position the logo inside the ticket card, near the QR code
            qr_x = 400  # QR code position on the left
            qr_y = 150  # QR code position within the ticket card
            logo_x = qr_x - 130  # Logo is positioned to the left of the QR code
            logo_y = qr_y  # Keep the logo at the same vertical position as the QR code

            # Draw the ticket content card with lightgrey background
            pdf_canvas.setFillColor(colors.lightgrey)
            pdf_canvas.roundRect(30, 100, 510, 220, 10, fill=1)

            # Set the border color to lightseagreen
            pdf_canvas.setStrokeColor(colors.lightseagreen)
            pdf_canvas.setLineWidth(2)  # Optional: Adjust the thickness of the border
            pdf_canvas.roundRect(30, 100, 510, 220, 10, fill=0)  # Draw the border

            # Draw the QR code on the card
            pdf_canvas.drawImage(qr_temp_file_name, qr_x, qr_y, width=100, height=100)

            # Draw the logo image over the ticket card with the background color
            pdf_canvas.drawImage(logo_temp_file_name, logo_x, logo_y, width=120, height=120)

        # Header Section (drawn above the ticket card)
        pdf_canvas.setFillColor(colors.midnightblue)
        pdf_canvas.setFont("Helvetica-Bold", 18)
        pdf_canvas.setFillColor(colors.white)
        pdf_canvas.drawString(160, 330, "Event Ticket")

        # Ticket Details Section
        pdf_canvas.setFont("Helvetica", 12)
        pdf_canvas.setFillColor(colors.darkblue)
        pdf_canvas.drawString(60, 300, f"Event Name: {application.event.event_name}")
        pdf_canvas.drawString(60, 280, f"Name: {application.name}")
        pdf_canvas.drawString(60, 260, f"Email: {application.email}")
        pdf_canvas.drawString(60, 240, f"Status: {application.status}")
        pdf_canvas.drawString(60, 220, f"Ticket ID: {ticket_id}")
        pdf_canvas.drawString(60, 200, f"Date: {application.event.event_date}")
        pdf_canvas.drawString(60, 180, f"Location: {application.event.event_location}")

        # Footer Message
        pdf_canvas.setFillColor(colors.darkblue)
        pdf_canvas.setFont("Helvetica-Oblique", 10)
        pdf_canvas.drawString(60, 140, "Thank you for your participation! Please keep this ticket safe.")

        # Save and Encode PDF
        pdf_canvas.showPage()
        pdf_canvas.save()
        pdf_buffer.seek(0)

        # Base64 encode the PDF
        pdf_bytes = pdf_buffer.getvalue()
        encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

        # Cleanup temporary files
        os.remove(qr_temp_file_name)
        if logo_path:
            os.remove(logo_temp_file_name)

        return ticket_id, encoded_pdf









