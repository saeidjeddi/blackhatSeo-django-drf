from django.db import models



class Proxy(models.Model):
    proxy_test = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.proxy_test


# models.py
class TaskStatus(models.Model):
    task_id = models.CharField(max_length=255, unique=True)
    url = models.URLField()
    referer = models.URLField()
    request_granted = models.IntegerField()
    completed_requests = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default="PENDING")
    duration = models.PositiveIntegerField(null=True, blank=True)
    stop_requested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class UserAgentDesktop(models.Model):
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class UserAgentMobile(models.Model):
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class RequestLog(models.Model):
    task = models.ForeignKey(TaskStatus, on_delete=models.CASCADE, related_name="logs")
    status_code = models.IntegerField(null=True, blank=True)
    url = models.URLField()
    proxy = models.TextField(null=True, blank=True)
    referer = models.TextField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    language = models.TextField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


