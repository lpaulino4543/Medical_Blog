# Register your models here.
from django.contrib import admin
from .models import BlogPost, Category, Comment, User

admin.site.register(BlogPost)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(User)
