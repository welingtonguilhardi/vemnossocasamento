from django.db import models
import random
import string
from django.urls import reverse
from django.utils import timezone

from django.urls import reverse

from app import settings

class Guest(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome")
    code = models.CharField(max_length=4, unique=True, verbose_name="Código")
    companions = models.PositiveIntegerField(default=0, verbose_name="Acompanhantes")
    checked_in = models.BooleanField(default=False, verbose_name="Entrou")
    companions_checked_in = models.PositiveIntegerField(default=0, verbose_name="Acomp. presentes")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)
    
    def generate_unique_code(self):
        while True:
            code = ''.join(random.choices(string.digits, k=4))
            if not Guest.objects.filter(code=code).exists():
                return code
    
    def check_in(self):
        self.checked_in = True
        self.companions_checked_in = self.companions
        self.save()
    
    def check_out(self):
        self.checked_in = False
        self.companions_checked_in = 0
        self.save()
    
    def update_companions(self, new_count):
        if new_count <= self.companions:
            self.companions_checked_in = new_count
            self.checked_in = new_count > 0
            self.save()
    @property
    def last_confirmation(self):
        return self.confirmationlink_set.filter(confirmed=True).order_by('-used_at').first()
    
    def get_confirmation_history(self):
        return self.confirmationlink_set.filter(confirmed=True).order_by('-used_at')
    
    def get_all_links(self):
        return self.confirmationlink_set.all().order_by('-created_at')
            
    def generate_confirmation_links(self, quantity=3):
        links = []
        for _ in range(quantity):
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            link = ConfirmationLink.objects.create(
                guest=self,
                token=token,
                expiration_date=timezone.now() + timezone.timedelta(days=7)
            )
            full_url = reverse('confirm_presence', kwargs={'token': token})
            links.append({
                'url': f"http://{settings.DOMAIN}{full_url}",
                'token': token
            })
        return links
    
    def __str__(self):
        return f"{self.name} (Código: {self.code})"
    
    class Meta:
        ordering = ['name']
        
class ConfirmationLink(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    token = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    confirmed = models.BooleanField(default=False)

    def is_valid(self):
        return not self.confirmed and timezone.now() < self.expiration_date

    def confirm(self):
        if self.is_valid():
            self.confirmed = True
            self.used_at = timezone.now()
            self.save()
            return True
        return False