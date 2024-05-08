from django.core.mail import send_mail

class Util:
    @staticmethod
    def send_email(data):
        send_mail(data['subject'], data['body'], data['from_email'], data['recipient_list'], fail_silently=False)