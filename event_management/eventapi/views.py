from django.shortcuts import render
from django.http import JsonResponse
import random
from .serializers import EventSerializer,TicketTypeSerializer ,TicketSerializer,DonarSerializer,DonarManagementSerializer,SilentAuctionSerializer,EventImagesSerializer
from rest_framework import status
from rest_framework.views import APIView,View
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Event, Role, RoleManagement,Ticket,TicketType,FeedBack,Wishlist,Message,NonRegisteredRSVP,Donar,DonarManagement,SilentAuction,EventImages
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from eventapi.permissions import IsHost, IsOrganizer,IsNotOrganizerOrHost,IsEventPart,IsPartOfEvent,IsHostOrOrganizer
from cloudinary_storage.storage import RawMediaCloudinaryStorage
import cloudinary
from django.core.files import File
from xml.dom import ValidationErr
import qrcode
from io import BytesIO
from xml.dom import ValidationErr
from userapi.models import CustomUser
from eventapi.util import Util
from decouple import config


class EventView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        if request.user.is_authenticated:
            events = Event.objects.all()
        else:
            events = Event.objects.filter(type='public')
        try:
            serializer = EventSerializer(events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            event = serializer.save()
            roles = Role.objects.filter(role__in=['host', 'organizer'])
            user = request.user

            for role in roles:
                RoleManagement.objects.create(event_id=event, role_id=role, user_id=user, is_acknowledge=True)
            return Response({'message': 'Event Created','data':serializer.data}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def perform_create(self, serializer):
        image_file = self.request.data.get('image')
        
        if image_file:
           
            cloudinary_response = cloudinary.uploader.upload(image_file)
            image_url = cloudinary_response.get('url')
            serializer.validated_data['image'] = image_url
        
        super().perform_create(serializer)

class EventImagesView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method == 'POST':
            return [IsHostOrOrganizer()]

    def get(self, request, event_id):
        try:
            event_photos = Event.objects.prefetch_related('eventimages_set').get(id=event_id).eventimages_set.all()
            serializer = EventImagesSerializer(event_photos, many=True)

            return Response((serializer.data), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, event_id):
        event = Event.objects.get(pk=event_id)

        try:
            images = request.data
            serializer = EventImagesSerializer(data=images, many=True)

            for image_file in images.values():
                serializer.is_valid(raise_exception=True)
                cloudinary_response = cloudinary.uploader.upload(image_file, folder='event_images')
                EventImages.objects.create(event=event, image=cloudinary_response['secure_url'])

            return Response({'message': 'added'})
        except Exception as e:
            return Response({'error': str(e)})

class IsPartOfEventView(APIView):
   
    def get(self, request):
        try:
            events = Event.objects.none()
            user = request.user       
            listevent = RoleManagement.objects.filter(user_id=user)
           

            for list in listevent:
                events = events.union(Event.objects.filter(pk=list.event_id.id))
            
            serializer = EventSerializer(events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EventDetailView(APIView):

    def get_permissions(self):
        if self.request.method == 'PUT' or self.request.method == 'DELETE':
            return [IsHostOrOrganizer()]
        else:
            return [IsAuthenticated()]

    def get(self, request, event_id):
        try:
            event = get_object_or_404(Event, pk=event_id)
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, event_id):
        try:
            event = get_object_or_404(Event, pk=event_id)
            serializer = EventSerializer(event, data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'message': 'Event Updated'}, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, event_id):
        try:
            event = get_object_or_404(Event, pk=event_id)
            event.delete()
            return Response({'message': 'Event Deleted'}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
class EventSearchView(APIView):
    def get(self, request):
        try:
           
            search_query = request.query_params.get('query', '') 
            events = Event.objects.filter(name__istartswith=search_query)
            serializer = EventSerializer(events, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
class EventTeamView(APIView):
    def get_permissions(self):
        if self.request.method=='GET':
            return [IsEventPart()]
        elif self.request.method=='POST':
            return [IsHostOrOrganizer()]
   
    def get(self,request,event_id):
        data = {}
        try:
            roles = Role.objects.all()
            for role in roles:
                users = []
                try:
                    roleManager = RoleManagement.objects.filter(event_id=event_id,role_id=role)
                    for user in roleManager:
                        users.append(user.user_id.email)
                    data[role.role]=users
                    print(data)
                except RoleManagement.DoesNotExist:
                    data[role.role]=users
                    continue
                    print(data)

            return Response({'data':data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST) 
               
    def post(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
            data = request.data

            for key in data:
                if(key=='host'):
                    continue
                role = Role.objects.get(role=key)
                for value in data[key]:
                   
                    if len(value):
                        try:
                            user = CustomUser.objects.get(email=value)
                            try:
                                RoleManagement.objects.get(event_id=event, role_id=role, user_id=user)
                            except RoleManagement.DoesNotExist:
                                RoleManagement.objects.create(role_id=role, user_id=user, event_id=event)
                                info = {
                                    'subject': 'New Role Invitation For Event Mail',
                                    'body': 'You have been invited to be a part of ' + event.name + ' by ' + request.user.first_name + ' ' + request.user.last_name + ' for the role of ' + role.role + '. Please accept your invitation by redirecting to http://localhost:3000/home. Please login and kindly accespt the invitation for the same thing given to you here.',
                                    'from_email': config('EMAIL_HOST_USER'),
                                    'recipient_list': [user.email],
                                }

                                Util.send_email(info)
                        except CustomUser.DoesNotExist:
                            NonRegisteredRSVP.objects.create(email=value, event=event, role=role)
                            info = {
                                'subject': 'New Role Invitation For Event Mail',
                                'body': 'You have been invited to be a part of ' + event.name + ' by ' + request.user.first_name + ' ' + request.user.last_name + ' for the role of ' + role.role + '. Please accept your invitation by redirecting to http://localhost:3000/home. Please signup and kindly accespt the invitation for the same thing given to you here.',
                                'from_email': config('EMAIL_HOST_USER'),
                                'recipient_list': [value],
                            }

                            Util.send_email(info)

            return Response({'message': 'Email send successfully for respective users for inviting to the event.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TicketView(APIView):
    def get_permissions(self):
        if self.request.method=='GET':
            return [IsAuthenticated]
        elif self.request.method=='POST':
            return  [AllowAny()]
            
    def get(self, request):
        try:
            user = request.user
            ticket = Ticket.objects.filter(user=user)

            return Response({'ticket': ticket}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, event_id):
        
        try:
            user = request.user
            event = Event.objects.get(pk=event_id)
            ticket_type_id = request.data['ticket_type']

            ticket_type = TicketType.objects.get(event=event, id=ticket_type_id)

           
            ticket = Ticket(user=user, ticket_type=ticket_type)
           
            ticket.save()
           

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
           

            qr.add_data(f"http://localhost:3000/event-management/scanner/{ticket.id}")
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer)
            
            buffer.seek(0)
            filename = f'qr_{ticket.id}.png'
            ticket.qr.save(filename, File(buffer), save=True)
            data = {
                'subject': 'Ticket for the Event',
                'body': 'You have successfully booked your ticket for ' + event.name + ' at ' + event.location + ' on ' + str(event.date) + '.',
                'from_email': config('EMAIL_HOST_USER'),
                'recipient_list': [user.email],
            }

            Util.send_email(data)
            role_attendee = Role.objects.get(role='attendee')
            RoleManagement.objects.create(user_id=user, event_id=event, role_id=role_attendee, is_acknowledge=True)

            return Response({'message': 'Ticket Mail Send Successfully'}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
           

class TicketTypeView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method == 'POST':
            return [IsHost() or IsOrganizer()]

    def get(self, request, event_id):
        try:
            data = []
            event = Event.objects.get(pk=event_id)
            ticket_types = TicketType.objects.filter(event=event)
            print(ticket_types)
            serializer = TicketTypeSerializer(ticket_types, many=True)

            # for ticket_type in ticket_types:
            #     temp_dict = {}
            #     temp_dict['id'] = ticket_type.id
            #     temp_dict['name'] = ticket_type.name
            #     temp_dict['price'] = ticket_type.price
            #     data.append(temp_dict)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, event_id):
        try:
            data = request.data
            event = Event.objects.get(pk=event_id)

            if len(data) == 0:
                raise ValidationErr("You need to create at least one ticket type.")

            event_tickets_instance = TicketType.objects.filter(event=event)
            event_tickets_instance.delete()

            for ticket_type in data:
                serializer = TicketTypeSerializer(data=ticket_type)
                serializer.is_valid(raise_exception=True)
                TicketType.objects.create(event=event, name=ticket_type['name'], price=ticket_type['price'])

            return Response({"message": "Ticket types successfully created!"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, event_id):
            try:
                data = request.data
                event = Event.objects.get(pk=event_id)

                for ticket_type_data in data:
                    ticket_type = TicketType.objects.get(pk=ticket_type_data['id'])
                    serializer = TicketTypeSerializer(instance=ticket_type, data=ticket_type_data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                return Response({"message": "Ticket types successfully updated!"}, status=status.HTTP_200_OK)
            except Event.DoesNotExist:
                return Response({'error': 'Event does not exist.'}, status=status.HTTP_404_NOT_FOUND)        

class UserTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            tickets = Ticket.objects.filter(user=user)
            serializer = TicketSerializer(tickets, many=True)
            print(serializer.data)
            return Response({'tickets': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)    
            
class UserRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        try:
            user = request.user
            event = Event.objects.get(pk=event_id)
            user_role = RoleManagement.objects.filter(user_id=user, event_id=event,is_acknowledge=True)

           
            if len(user_role) != 0:
                role = user_role[0].role_id.role
            else:
                role = 'authenticated'

            return Response({'role': role}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FeedBackView(APIView):
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [IsOrganizer()]
    #     elif self.request.method == 'POST':
    #         return [IsAuthenticated]
    
    def get(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
            feedback_list = FeedBack.objects.filter(event=event)
            feedbacks = []
            
            for feedback in feedback_list:
                data = {}
                data["user"] = feedback.user.name 
                data["type"] = feedback.type
                data["details"] = feedback.details
                feedbacks.append(data)

            return Response({'feedbacks': feedbacks}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, event_id):
        try:
            # Check check-in status of the user so that only attended user can give review
            
            event = Event.objects.get(pk=event_id)
            user = request.user
            feedbacks = request.data["feedbacks"]
            
            for feedback in feedbacks:
              
                type = feedback["type"]
                details = feedback["details"]
                FeedBack.objects.create(user=user, event=event, type=type, details=details)
            return Response({'message': 'Feedbacks given successfully for the event'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
     
class WishlistView(APIView):
    permission_classes = [IsAuthenticated]
    def has_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method == 'POST':
            return [IsNotOrganizerOrHost()]

    def get(self, request):
        try:
            user = request.user  
            eventList = Wishlist.objects.filter(user=user).select_related('event')

            events = []
            for wishlist in eventList:
                events.append(wishlist.event)

            serializer = EventSerializer(events, many=True)
            return Response({"events": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        try:
            user = request.user
            event_id = request.data['event_id']
            event = Event.objects.get(pk=event_id)

            try:
                wish = Wishlist.objects.get(user=user, event=event)
            except Wishlist.DoesNotExist:
                Wishlist.objects.create(user=user, event=event)

                return Response({'message': 'Event added to Wishlist'}, status=status.HTTP_200_OK)

            return Response({'message': 'Event already present for you'}, status=status.HTTP_208_ALREADY_REPORTED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, event_id):
        try:
            user = request.user
            event = Event.objects.get(pk=event_id)
            wish = Wishlist.objects.get(user=user, event=event)
            wish.delete()
            return Response({'message': 'Event removed from Wishlist'}, status=status.HTTP_200_OK)
        
        except Wishlist.DoesNotExist:
            return Response({'error': 'Event not found in Wishlist'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)     
        
class MessageView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsPartOfEvent()]
        elif self.request.method == 'POST':
            return [IsHost() or IsOrganizer()]

    def get(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
            messages = Message.objects.filter(event=event)

            event_messages = []

            for message in messages:
                data = {}
                data['mail'] = message.user.email
                data['content'] = message.content
                event_messages.append(data)

            return Response({'messages': event_messages}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, event_id):
      
        try:
            user = request.user
            event = Event.objects.get(pk=event_id)
            content = request.data['content']

            message = Message.objects.create(event=event, user=user, content=content)
            return Response({'message': 'Message Sent'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PendingRSVPView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            pendingRSVP = []
            pendingRequests = RoleManagement.objects.filter(user_id=user, is_acknowledge=False)

            for pendingRequest in pendingRequests:
                data = {}

                data['id'] = pendingRequest.id
                data['event_name'] = pendingRequest.event_id.name
                data['role'] = pendingRequest.role_id.role

                pendingRSVP.append(data)

            return Response({'pendingRSVP': pendingRSVP}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            
            res = request.data['res']
            instance_id = request.data['rsvpId']
            role_instance = RoleManagement.objects.get(pk=instance_id)
            if res == 'accept':
                role_instance.is_acknowledge = True
                role_instance.save()
                return Response({'message': 'Accepted'}, status.HTTP_200_OK)
            elif res == 'reject':
                role_instance.delete()
                return Response({'message': 'Rejected'}, status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid response'}, status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)        

class DonarView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
           
            donar_management = DonarManagement.objects.filter(user_id=request.user)
            
            donor_ids = donar_management.values_list('donar_id', flat=True)
            # Filter the Donar objects based on the donor_ids from queryset
            donars = Donar.objects.filter(id__in=donor_ids)
            serializer = DonarSerializer(donars, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
    def post(self, request):
        
        if request.user.is_authenticated:
            serializer = DonarSerializer(data=request.data)

            if serializer.is_valid():
                donar_instance = serializer.save()
                existing_entry = DonarManagement.objects.filter(user_id=request.user, donar_id=donar_instance).first()

                if existing_entry:
                    return Response({'message': 'DonarManagement entry already exists for this Donar'}, status=status.HTTP_200_OK)
                else:
                    # Create a new DonarManagement entry
                    new_entry_serializer = DonarManagementSerializer(data={'user_id': request.user.id, 'donar_id': donar_instance.id})
                    if new_entry_serializer.is_valid():
                        new_entry_serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        return Response(new_entry_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

class SilentAuctionView(APIView):

    def get(self, request,event_id):
            user = request.user
            event = Event.objects.get(pk=event_id)
            auctions = SilentAuction.objects.get(user_id=user,event_id=event)
            serializer = SilentAuctionSerializer(auctions)
            return Response(serializer.data)
    
    def post(self, request, event_id):
            user_id = request.user.id
            
            # Combine user_id and event_id with the bid data
            bid_data = {
                'user_id': user_id,
                'event_id': event_id,
                'bid': request.data.get('bid')
            }

            serializer = SilentAuctionSerializer(data=bid_data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
class HighestBidView(APIView):
    def get(self, request, event_id):
        try:
            # Fetch the highest bid object including user details
            highest_bid = SilentAuction.objects.filter(event_id=event_id).order_by('-bid').select_related('user_id').first()
            if highest_bid:
                
                serializer = SilentAuctionSerializer(highest_bid)
                # Extract user name from the related user object
                user_name = highest_bid.user_id.first_name
                serialized_data = serializer.data
                serialized_data['user_name'] = user_name
                return Response(serialized_data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'No bids for this event yet'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)     
        

class RandomRaffleView(View):
    def get(self, request, event_id):
        try:

            attendees = RoleManagement.objects.filter(event_id=event_id, role_id__role='attendee', is_acknowledge=True)
            
            if attendees.exists():
                # Select a random attendee
                random_attendee = random.choice(attendees)
                user_info = {
                    'user_id': random_attendee.user_id.id,
                    'user_name': random_attendee.user_id.first_name,
                    'user_email': random_attendee.user_id.email
                }
                
                return JsonResponse(user_info, status=200)
            else:
                return JsonResponse({'message': 'No attendees found for the event'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
         