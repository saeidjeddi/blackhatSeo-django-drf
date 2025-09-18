import random
from rest_framework.views import APIView
from rest_framework.response import Response
import requests

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

class ListTextApi(APIView):

    def get(self, request):
        url_request = request.query_params.get("url")
        if not url_request:
            return Response({"error": "URL is required"}, status=400)

        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": random.choice(languages),
            "Referer": random.choice(referrers),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "DNT": "1",
            "Cache-Control": "no-cache",
            "kwords": "python, django, SEO, web scraping", 
            "X-Robots-Tag": "index, follow"
        }


        try:
            response = requests.get(url_request, headers=headers, timeout=10)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=500)

        return Response({
            "status": response.status_code,
            "length": len(response.content),
            "headers": dict(response.headers)
        })
