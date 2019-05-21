from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Post, Category, Tag
from .adminforms import PostAdminForm
from typeidea.custom_site import custom_site
from typeidea.base_admin import BaseOwnerAdmin

# Register your models here.

@admin.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'is_nav', 'create_time')
    fields = ('name', 'status', 'is_nav')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(CategoryAdmin, self).save_model(request, obj, form, change)

@admin.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'create_time')
    fields = ('name', 'status')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(TagAdmin, self).save_model(request, obj, form, change)

# not work
#class PostInline(admin.TabularInline):
#    fields = ('title', 'desc')
#    extra = 1
#    model = Post

@admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    form = PostAdminForm
#    inlines = [PostInline, ]
    list_display = [
            'title', 'category', 'status',
            'create_time', 'operator',
            ]
    list_display_links = []
    list_filter = ['category', ]
    search_fields = ['title', 'category__name']

    actions_on_top = True
    actions_on_bottom = True


    # edit page
    save_on_top = True

    fieldsets = (
        ('base set', {
            'description': 'base set description',
            'fields': (
                ('title', 'category'),
                'status',
                ),
        }),

        ('content', {
            'fields': (
                'desc',
                'content',
                ),
        }),

        ('extra', {
            'classes': ('collapse',),
            'fields': ('tag', ),
        })
    )

    filter_vertical = ('tag', )
    class Media:
        css = {
            'all':("https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css", ),
        }
        js = ("https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/js/bootstrap.bundle.js", )

    def operator(self, obj):
        return format_html(
            '<a href="{}">edit</a>',
            reverse ('cus_admin:blog_post_change', args=(obj.id,)))
    operator.short_description = 'operation'

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(PostAdmin, self).save_model(request, obj, form, change)

