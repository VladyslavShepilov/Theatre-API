from django.contrib import admin

from theatre_service.models import (
    Actor,
    Genre,
    Play,
    Performance,
    Ticket,
    Reservation
)


class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Reservation)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInLine,)


admin.site.register(Actor)
admin.site.register(Genre)
admin.site.register(Play)
admin.site.register(Performance)
admin.site.register(Ticket)
