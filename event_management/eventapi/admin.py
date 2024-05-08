from django.contrib import admin
from .models import Event,Role,RoleManagement,TicketType,Ticket,FeedBack,Wishlist,Message,Donar,DonarManagement,SilentAuction,EventImages



@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time','location','type')
    search_fields = ('name', 'date')

admin.site.register(Role)
admin.site.register(Ticket)
admin.site.register(TicketType)
admin.site.register(Wishlist)
admin.site.register(Message)
admin.site.register(SilentAuction)
admin.site.register(EventImages)
# admin.site.register(FeedBack)

@admin.register(RoleManagement)
class RoleManagementAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'user_id', 'role_id', 'is_acknowledge')
    list_filter = ('event_id', 'user_id', 'role_id', 'is_acknowledge')
    search_fields = ('event_id__name', 'user_id__username', 'role_id__name')
    list_per_page = 20

@admin.register(FeedBack)
class FeedBackadmin(admin.ModelAdmin):
    list_display=('user_id','event_id','type','details')

@admin.register(Donar)
class DonarAdmin(admin.ModelAdmin):
    list_display=('donar_name','email')

@admin.register(DonarManagement)
class DonarManagementAdmin(admin.ModelAdmin):
    list_display=('donar_id','user_id')