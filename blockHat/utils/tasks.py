
from celery import shared_task
from blockHat.models import TaskStatus, Proxy, UserAgentDesktop, UserAgentMobile, RequestLog
import random, time, requests
from concurrent.futures import ThreadPoolExecutor, as_completed



@shared_task(bind=True, name="request_data_task_simple")
def request_data_task_simple(self, url_request, range_request, user_agent_choice, referrers_choice):
    scheduled_task = TaskStatus.objects.filter(task_id=self.request.id).first()
    if scheduled_task:
        scheduled_task.status = "RUNNING"
        scheduled_task.save()

    task_status = None
    try:
        task_status, created = TaskStatus.objects.get_or_create(
            task_id=self.request.id,
            defaults={
                "url": url_request,
                "referer": referrers_choice,
                "request_granted": range_request,
                "completed_requests": 0,
                "status": "RUNNING",
                "stop_requested": False,
            }
        )

        proxies_list = list(Proxy.objects.values_list("proxy_test", flat=True))
        if user_agent_choice == "mobile":
            user_agents = list(UserAgentMobile.objects.values_list("user_agent", flat=True))
        elif user_agent_choice == "desktop":
            user_agents = list(UserAgentDesktop.objects.values_list("user_agent", flat=True))
        else:
            user_agents = list(UserAgentDesktop.objects.values_list("user_agent", flat=True)) + \
                          list(UserAgentMobile.objects.values_list("user_agent", flat=True))

        languages = ["en-US", "en-CA", "es-ES"]
        start_time = time.time()

        for i in range(task_status.completed_requests, range_request):
            current_status = TaskStatus.objects.filter(task_id=self.request.id).first()
            if current_status and current_status.stop_requested:
                current_status.status = "STOPPED"
                current_status.save()
                if scheduled_task:
                    scheduled_task.status = "STOPPED"
                    scheduled_task.save()
                print(f"Task {self.request.id} stopped by user request")
                return

            user_agent = random.choice(user_agents)
            language = random.choice(languages)
            headers = {
                "User-Agent": user_agent,
                "Accept-Language": language,
                "Referer": referrers_choice,
                "Keep-Alive": str(random.randint(1, 100)),
                "Connection": "keep-alive",
            }

            proxy = {"http": random.choice(proxies_list)} if proxies_list else None
            status_code, error = None, None

            try:
                response = requests.get(url_request, headers=headers, proxies=proxy, timeout=10)
                status_code = response.status_code
                print(f"Request {i+1}/{range_request} to {url_request} - Status: {status_code}")
            except Exception as e:
                error = str(e)
                print(f"Request {i+1}/{range_request} failed: {error}")

            RequestLog.objects.create(
                task=task_status,
                status_code=status_code,
                url=url_request,
                proxy=proxy["http"] if proxy else None,
                referer=referrers_choice,
                user_agent=user_agent,
                language=language,
                error=error
            )

            task_status = TaskStatus.objects.get(task_id=self.request.id)
            task_status.completed_requests += 1
            task_status.save()

   

        end_time = time.time()
        task_status.status = "COMPLETED"
        task_status.duration = int(end_time - start_time)
        task_status.save()

        if scheduled_task:
            scheduled_task.status = "COMPLETED"
            scheduled_task.save()

        print(f"Task {self.request.id} completed successfully")

    except Exception as exc:
        print(f"Task {self.request.id} failed with error: {exc}")
        if task_status:
            task_status.status = "FAILED"
            task_status.save()
        if scheduled_task:
            scheduled_task.status = "FAILED"
            scheduled_task.save()
        raise self.retry(exc=exc)


@shared_task(bind=True, name="request_data_thread", max_retries=3, default_retry_delay=10)
def request_data_thread(self, url_request, range_request, user_agent_choice, referrers_choice):
    scheduled_task = TaskStatus.objects.filter(task_id=self.request.id).first()
    if scheduled_task:
        scheduled_task.status = "RUNNING"
        scheduled_task.save()

    try:
        task_status, created = TaskStatus.objects.get_or_create(
            task_id=self.request.id,
            defaults={
                "url": url_request,
                "referer": referrers_choice,
                "request_granted": range_request,
                "completed_requests": 0,
                "status": "RUNNING",
                "stop_requested": False,
            }
        )

        proxies_list = list(Proxy.objects.values_list("proxy_test", flat=True))

        if user_agent_choice == "mobile":
            user_agents = list(UserAgentMobile.objects.values_list("user_agent", flat=True))
        elif user_agent_choice == "desktop":
            user_agents = list(UserAgentDesktop.objects.values_list("user_agent", flat=True))
        else:  # all
            user_agents = list(UserAgentDesktop.objects.values_list("user_agent", flat=True)) + \
                          list(UserAgentMobile.objects.values_list("user_agent", flat=True))

        languages = ["en-US", "en-CA", "es-ES"]

        def make_request(i):
            time.sleep(1)  # اگر نیاز باشه تاخیر ایجاد کنه
            current_status = TaskStatus.objects.get(task_id=self.request.id)
            if current_status.stop_requested:
                current_status.status = "STOPPED"
                current_status.save()
                if scheduled_task:
                    scheduled_task.status = "STOPPED"
                    scheduled_task.save()
                print(f"Task {self.request.id} stopped by user request")
                return

            user_agent = random.choice(user_agents)
            language = random.choice(languages)
            headers = {
                "User-Agent": user_agent,
                "Accept-Language": language,
                "Referer": referrers_choice,
                "Keep-Alive": str(random.randint(1, 100)),
                "Connection": "keep-alive",
            }

            proxy = {"http": random.choice(proxies_list)} if proxies_list else None
            status_code = None
            error = None

            try:
                response = requests.get(url_request, headers=headers, proxies=proxy, timeout=10)
                status_code = response.status_code
                print(f"[{i+1}/{range_request}] URL: {url_request} | Status: {status_code} | "
                      f"UA: {user_agent} | Proxy: {proxy['http'] if proxy else 'None'}")
            except Exception as e:
                error = str(e)
                print(f"[{i+1}/{range_request}] URL: {url_request} | ERROR: {error} | "
                      f"UA: {user_agent} | Proxy: {proxy['http'] if proxy else 'None'}")

            RequestLog.objects.create(
                task=task_status,
                status_code=status_code,
                url=url_request,
                proxy=proxy["http"] if proxy else None,
                referer=referrers_choice,
                user_agent=user_agent,
                language=language,
                error=error
            )

            # بروزرسانی و چاپ پیشرفت
            task_status.completed_requests = RequestLog.objects.filter(task=task_status).count()
            task_status.save()
            print(f"Progress: {task_status.completed_requests}/{range_request} completed")

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=min(7, range_request)) as executor:
            futures = [executor.submit(make_request, i) for i in range(range_request)]
            for _ in as_completed(futures):
                print('--------------')

        end_time = time.time()
        task_status.status = "COMPLETED"
        task_status.duration = int(end_time - start_time)
        task_status.save()

        if scheduled_task:
            scheduled_task.status = "COMPLETED"
            scheduled_task.save()

        print(f"Task {self.request.id} completed successfully in {task_status.duration}s")

    except Exception as exc:
        print(f"Task {self.request.id} failed with error: {exc}")
        task_status.status = "FAILED"
        task_status.save()
        if scheduled_task:
            scheduled_task.status = "FAILED"
            scheduled_task.save()
        raise self.retry(exc=exc)
