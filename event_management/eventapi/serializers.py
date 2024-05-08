from rest_framework import serializers
from .models import Event,RoleManagement,Ticket,TicketType,Donar,DonarManagement,SilentAuction,EventImages

class EventSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Event
        fields = '__all__'

class RoleSeralizer(serializers.ModelSerializer):
    class meta:
        model =RoleManagement
        fiields=['event_id','user_id','role_id']

class TicketTypeSerializer (serializers.ModelSerializer):
    event=EventSerializer(read_only=True)
    

    class Meta:
        model = TicketType
        fields = ['name','price','event']
        
class TicketSerializer(serializers.ModelSerializer):
    ticket_type=TicketTypeSerializer(read_only=True)
    class Meta:
        model = Ticket
        fields = ['id', 'user', 'ticket_type', 'qr', 'is_checkedin']

class DonarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donar
        fields = ['id', 'donar_name', 'email']

class  EventImagesSerializer(serializers.ModelSerializer):
    event=EventSerializer(read_only=True)
    class Meta:
        model=EventImages
        fields=['event','image']


class DonarManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonarManagement
        fields = ['id', 'user_id', 'donar_id']

    def create(self, validated_data):
        # Create and return a new DonarManagement instance
        return DonarManagement.objects.create(**validated_data)

class SilentAuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SilentAuction
        fields = ['id', 'user_id', 'event_id', 'bid']

    def validate_bid(self, value):
        if value <= 0:
            raise serializers.ValidationError("Bid amount must be greater than zero.")
        return value    