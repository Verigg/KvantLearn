from django.contrib import admin
from .models import Lesson, Material, Module


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    fields = ('title', 'order', 'content')


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ('title', 'order')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'direction', 'author', 'is_published', 'created_at', 'updated_at')
    list_filter = ('direction', 'is_published', 'created_at')
    search_fields = ('title', 'short_description', 'author__username', 'author__full_name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'material', 'order')
    list_filter = ('material',)
    search_fields = ('title', 'material__title')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order')
    list_filter = ('module__material',)
    search_fields = ('title', 'content', 'module__title')

