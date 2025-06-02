from django.contrib import admin
from .models import Course, Lesson, Subscription, Payment

admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Subscription)
admin.site.register(Payment)
