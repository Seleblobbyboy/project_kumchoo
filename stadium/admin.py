from django.contrib import admin
from .models import Field, Booking, Match, FinancialRecord

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price_per_hour')
    search_fields = ('name',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'field', 'booking_date', 'start_time', 'end_time', 'total_price', 'payment_status')
    list_filter = ('payment_status', 'booking_date', 'field')
    search_fields = ('customer_name', 'customer_phone')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('title', 'field', 'team_a', 'team_b', 'match_date', 'start_time', 'status')
    list_filter = ('status', 'match_date', 'field')
    search_fields = ('title', 'team_a', 'team_b')

@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ('date', 'record_type', 'category', 'amount')
    list_filter = ('record_type', 'date')
    search_fields = ('category', 'description')
