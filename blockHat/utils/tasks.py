from celery import shared_task
from blockHat.models import Proxy, TaskStatus, UserAgentDesktop, UserAgentMobile, RequestLog
import random, time, requests
from concurrent.futures import ThreadPoolExecutor, as_completed

@shared_task(bind=True, name="request_data_task")
def request_data_task(self, url_request, range_request, user_agent_choice, referrers_choice):
    task_status, _ = TaskStatus.objects.get_or_create(
        task_id=self.request.id,
        defaults={
            "url": url_request,
            "referer": referrers_choice,
            "total_requests": range_request,
            "completed_requests": 0,
            "status": "RUNNING"
        }
    )

    proxies_list = list(Proxy.objects.values_list("proxy_test", flat=True))

    if user_agent_choice == "mobile":
        user_agents = list(UserAgentMobile.objects.values_list("user_agent", flat=True))
    elif user_agent_choice == "desktop":
        user_agents = list(UserAgentDesktop.objects.values_list("user_agent", flat=True))
    elif user_agent_choice == "all":
        user_agents = list(UserAgentDesktop.objects.values_list("user_agent", flat=True)) + \
                      list(UserAgentMobile.objects.values_list("user_agent", flat=True))
    else:
        user_agents = None

    languages = ["en-US", "en-CA", "es-ES"]
    def make_request(i):
        time.sleep(1)
        user_agent = random.choice(user_agents)
        language = random.choice(languages)
        referer = referrers_choice
        headers = {
            "User-Agent": user_agent,
            "Accept-Language": language,
            "Referer": referer,
            "Keep-Alive": str(random.randint(1, 100)),
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7",
            "X-Requested-With": "XMLHttpRequest",
        }

        proxy = {"http": random.choice(proxies_list)} if proxies_list else None
        status_code = None
        error = None

        try:
            response = requests.get(url_request, headers=headers, proxies=proxy, timeout=10)
            status_code = response.status_code
            print(f"=> {status_code}, {language}, {url_request}, {referer}, {user_agent} <=")
        except Exception as e:
            error = str(e)

        RequestLog.objects.create(
            task=task_status,
            status_code=status_code,
            url=url_request,
            proxy=proxy["http"] if proxy else None,
            referer=referer,
            user_agent=user_agent,
            language=language,
            error=error
        )

        task_status.completed_requests = RequestLog.objects.filter(task=task_status).count()
        task_status.save()


    start_time = time.time()

    with ThreadPoolExecutor(max_workers=min(7, range_request)) as executor:
        futures = [executor.submit(make_request, i) for i in range(range_request)]
        print("---------------")
        for _ in as_completed(futures):
            pass
    end_time = time.time()

    task_status.status = "COMPLETED"
    task_status.duration = int(end_time - start_time)

    task_status.save()
