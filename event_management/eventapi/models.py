from django.db import models
from userapi.models import CustomUser


class Role(models.Model):
    ROLE_CHOICES = (
        ('organizer', 'Organizer'),
        ('host', 'Host'),
        ('volunteer', 'Volunteer'),
        ('attendee','Attendee'),
        ('crew_member', 'Crew Member'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    def __str__(self):
        return self.role
    
class Event(models.Model):
    TYPE_CHOICES = (
       ('private', 'Private'),
       ('public', 'Public'),
    )

    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    details = models.CharField(max_length=400)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_volunteer_allowed=models.BooleanField(default=False)
    roles=models.ManyToManyField(Role,through='RoleManagement')
    biditem = models.CharField(max_length=40, null=True, default=None)
    is_raffle=models.BooleanField(default=False)
  

    def __str__(self):
        return self.name


class RoleManagement(models.Model):
    event_id=models.ForeignKey(Event,on_delete=models.CASCADE)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,default=None)
    role_id=models.ForeignKey(Role,on_delete=models.CASCADE)
    is_acknowledge=models.BooleanField(default=False)

    # class Meta:
    #     unique_together = ['event_id', 'user_id', 'role_id']
    
    def __str__(self):
        return str(self.event_id) + "\t" + str(self.user_id) + "\t" + str(self.role_id)


class TicketType(models.Model):
    name=models.CharField(max_length=20)
    event=models.ForeignKey(Event,on_delete=models.CASCADE)
    price=models.DecimalField(max_digits=6,decimal_places=2)

    def __str__(self):
        return str(self.name) + "\t" + str(self.event) + "\t" + str(self.price)


class Ticket(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    ticket_type=models.ForeignKey(TicketType,on_delete=models.CASCADE)
    qr=models.ImageField(upload_to='qr_images/', blank=True)
    is_checkedin = models.BooleanField(default=False)




class FeedBack(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE) 
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    type=models.CharField(max_length=20)
    details = models.TextField()

class NonRegisteredRSVP(models.Model):
    email=models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE) 
    role=models.ForeignKey(Role,on_delete=models.CASCADE)

class Wishlist(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    event=models.ForeignKey(Event,on_delete=models.CASCADE)

class Message(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    event=models.ForeignKey(Event,on_delete=models.CASCADE)
    content=models.TextField()
    

class Donar(models.Model):
     donar_name=models.CharField(max_length=20)
     email = models.EmailField(unique=True)

     def __str__(self):
        return str(self.donar_name) 

class DonarManagement(models.Model):
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    donar_id=models.ForeignKey(Donar,on_delete=models.CASCADE)

class SilentAuction(models.Model):
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    event_id=models.ForeignKey(Event,on_delete=models.CASCADE)
    bid=models.DecimalField(max_digits=10,decimal_places=2)

class EventImages(models.Model):
    event=models.ForeignKey(Event,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='event_images/', blank=True, null=True)
