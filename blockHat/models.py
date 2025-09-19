from django.db import models

class Proxy(models.Model):
    proxy_test = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.proxy_test