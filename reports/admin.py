from django.contrib import admin

from . import models

admin.site.register([models.Card, models.DirectPayment, models.PayByLink])
