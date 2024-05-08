from rest_framework.permissions import BasePermission
from eventapi.models import Event,RoleManagement,Role

class IsOrganizer(BasePermission):
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False
        
        eventId = view.kwargs['event_id']
        event = Event.objects.get(pk=eventId)
        role_id_organizer = Role.objects.get(role='organizer')
        
        try:
            eventOrganizers = RoleManagement.objects.filter(event_id=event, role_id=role_id_organizer)
        except RoleManagement.DoesNotExist:
            eventOrganizers = None
      
        if(eventOrganizers):
            for organizer in eventOrganizers:
                if request.user == organizer.user_id:
                    print('ereh')
                    return True
        return False

class IsHost(BasePermission):
    def has_permission(self, request, view):
      
        if not request.user.is_authenticated:
            return False
        
        eventId = view.kwargs['event_id'] 
        event = Event.objects.get(pk=eventId)
        role_id_host = Role.objects.get(role='host')
        print(request.user)
        print(event)
        print(role_id_host)
        try:
            eventhost = RoleManagement.objects.get(user_id=request.user, event_id=event, role_id=role_id_host)
        except RoleManagement.DoesNotExist:
            eventhost = None
        print(eventhost)
        if eventhost and request.user == eventhost.user_id:
            return True
        return False
    
class IsNotOrganizerOrHost(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        event_id = request.data['event_id']
        role_id_host = Role.objects.get(name='host')
        eventHost = RoleManagement.objects.get(event_id=event_id, role_id=role_id_host)

        if request.user == eventHost.user_id:
            return False

        role_id_organizer = Role.objects.get(role='organizer')
        eventOrganizers = RoleManagement.objects.filter(event_id=event_id, role_id=role_id_organizer)

        for eventOrganizer in eventOrganizers:
            if request.user == eventOrganizer.user_id:
                return False

        return True

class IsPartOfEvent(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        event_id = view.kwargs['event_id']
        event = Event.objects.get(pk=event_id)

        users = RoleManagement.objects.filter(event_id=event)

        for user in users:
            if request.user == user.user_id:
                return True

        return False
    
class IsEventPart(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        user = request.user
        event_id = view.kwargs['event_id']
        event = Event.objects.get(pk=event_id)

        try:
            RoleManagement.objects.filter(event_id=event, user_id=user).exclude(role_id__role='attendee')

            return True
        except RoleManagement.DoesNotExist:
            return False    

class IsHostOrOrganizer(BasePermission):
    def has_permissions(self, request, view):
        if not request.user.is_authenticated:
            return False
        event_id = view.kwargs['event_id']
        event = Event.objects.get(pk=event_id)
        user = request.user

        user_role = RoleManagement.objects.filter(event_id=event, user_id=user, is_acknowledge=True)

        if 'host' in user_role.role_id.role or 'organizer' in user_role.role_id.role:
            return True
        else:
            return False        