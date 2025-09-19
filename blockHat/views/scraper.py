import random
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..models import Proxy

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
]

languages = ["en-US", "en-CA", "es-ES"]

referrers = [
    # "https://www.google.com/",
    "https://www.facebook.com/",
    # "https://www.youtube.com/",
    # "https://twitter.com/",
    # "https://www.instagram.com/"
]


class ScraperApiView(APIView):

    def get(self, request):
        url_request = request.query_params.get("url")
        range_request = request.query_params.get("range")

        if not url_request:
            return Response({"error": "URL is required"}, status=400)

        try:
            num_requests = int(range_request) if range_request else 1
        except ValueError:
            return Response({"error": "Invalid range value"}, status=400)

        proxies_list = list(Proxy.objects.values_list("proxy_test", flat=True))

        def make_request():
            Referer = random.choice(referrers)
            UserAgent = random.choice(user_agents)
            headers = {
                "User-Agent": UserAgent,
                "Accept-Language": random.choice(languages),
                "Referer": Referer,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "DNT": "1",
                "Cache-Control": "no-cache",
                "kwords": "python, django, SEO, web scraping",
                "X-Robots-Tag": "index, follow"
            }

            proxies = {"http": random.choice(proxies_list)} if proxies_list else None

            try:
                response = requests.get(url_request, headers=headers, timeout=10, proxies=proxies)
                return {
                    "status": response.status_code,
                    "url": response.url,
                    "proxies": proxies,
                    "Referer": Referer,
                    "User-Agent": UserAgent,
                }
            except requests.RequestException as e:
                return {
                    "error": str(e),
                    "proxies": proxies,
                    "Referer": Referer,
                    "User-Agent": UserAgent,
                }

        results = []
        with ThreadPoolExecutor(max_workers=min(20, num_requests)) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            for future in as_completed(futures):
                results.append(future.result())

        return Response(results)
