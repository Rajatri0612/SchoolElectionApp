from django.contrib import admin
from .models import Question, Choice

# Customize the admin interface headers
admin.site.site_header = "St. Francis School Student Council Elections"
admin.site.site_title = "Voting Admin Portal"
admin.site.index_title = "Welcome to the Voting Admin Area"

# Inline editing for Choices within the Question admin page
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3  # Number of empty choice forms to display
    fields = ('choice_text', 'image', 'votes')  # Include the image field

# Customize the Question admin interface
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date Information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]  # Add ChoiceInline for inline editing
    list_display = ('question_text', 'pub_date', 'was_published_recently')  # Columns to display
    list_filter = ['pub_date']  # Add a filter for pub_date
    search_fields = ['question_text']  # Add a search bar for question_text

# Customize the Choice admin interface
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'question', 'image', 'votes')  # Include the image field
    list_filter = ['question']  # Add a filter for question
    search_fields = ['choice_text']  # Add a search bar for choice_text

# Register models with custom admin classes
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)