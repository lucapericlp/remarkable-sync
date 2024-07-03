from requests import Session
from pathlib import Path

import json


cookie_header = {
    'rmMetaV2-user_id': 'anonymous_93b21580-a5b6-4545-ad4b-578a967ed1aa',
    'rmMetaV2-device_id': '5e596176-2e3b-48c9-a1d7-d69adf55cc05',
    'rmMetaV2-myrm_user_parameters': json.dumps({
        'subscription_type': 'free connect',
        'subscription_status': 'active',
        'subscription_payment_interval': 'none'
    }),
    '__stripe_mid': '76d85b47-4d3d-48d7-a739-b6c80f9c9e5c15c228',
    'rmMetaV2-session_id': '1720039901488',
    'rmMetaV2-utm_parameters': json.dumps({
        'utm_source': 'none',
        'utm_campaign': 'none',
        'utm_content': 'none',
        'utm_medium': 'none',
        'utm_id': 'none',
        'utm_term': 'none',
        'utm_variant': 'none'
    }),
    'rmMetaV2-myrm_utm_parameters': json.dumps({
        'myrm_utm_source': 'none',
        'myrm_utm_campaign': 'none',
        'myrm_utm_content': 'none',
        'myrm_utm_medium': 'none',
        'myrm_utm_id': 'none',
        'myrm_utm_term': 'none',
        'myrm_utm_variant': 'none'
    }),
    'rmMetaV2-gclid': 'none',
    'rmMetaV2-fbc': 'none',
    'rmMetaV2-affiliate_id': 'none',
    'rmMetaV2-rm_country': 'none'
}

url = "https://internal.cloud.remarkable.com/doc/v2/files"
headers = {
    "accept": "*/*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    'accept-encoding': 'gzip, deflate, br, zstd',
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6IjEiLCJ0eXAiOiJKV1QifQ.eyJhdXRoMC1wcm9maWxlIjp7IlVzZXJJRCI6ImF1dGgwfDYwMGFkZTE2ZTU0YjQzMDA3MTJmNzMyYyIsIklzU29jaWFsIjpmYWxzZSwiQ29ubmVjdGlvbiI6IlVzZXJuYW1lLVBhc3N3b3JkLUF1dGhlbnRpY2F0aW9uIiwiTmFtZSI6Imx1Y2FwZXJpYy5scEBnbWFpbC5jb20iLCJOaWNrbmFtZSI6Imx1Y2FwZXJpYy5scCIsIkdpdmVuTmFtZSI6IiIsIkZhbWlseU5hbWUiOiIiLCJFbWFpbCI6Imx1Y2FwZXJpYy5scEBnbWFpbC5jb20iLCJFbWFpbFZlcmlmaWVkIjp0cnVlLCJDcmVhdGVkQXQiOiIyMDIxLTAxLTIyVDE0OjE1OjUwLjUwMloiLCJVcGRhdGVkQXQiOiIyMDI0LTA2LTEyVDIwOjQ1OjU4LjgxNVoifSwiZGV2aWNlLWRlc2MiOiJicm93c2VyLWNocm9tZSIsImRldmljZS1pZCI6ImM2MmRlMjQxLTQ5NTMtNGJkNC1hODc4LWEwNmFjZDBmNGIyOCIsImV4cCI6MTcyMDA1ODE2OSwiaWF0IjoxNzIwMDQ3MzY5LCJpc3MiOiJyTSBXZWJBcHAiLCJqdGkiOiJjazB0ZlZVYmlWOD0iLCJsZXZlbCI6ImNvbm5lY3QiLCJuYmYiOjE3MjAwNDczNjksInNjb3BlcyI6ImludGdyIGh3Y21haWw6LTEgc3luYzp0b3J0b2lzZSBkb2NlZGl0IHNjcmVlbnNoYXJlIG1haWw6LTEiLCJzdWIiOiJhdXRoMHw2MDBhZGUxNmU1NGI0MzAwNzEyZjczMmMifQ.RmfaZuKxXmXHlBtyDw8AwyFju-lLNyH6sFVp1O-aT0U",
    "rm-meta": "eyJmaWxlX25hbWUiOiJQcm9hY3RpdmUgRGV0ZWN0aW9uIG9mIFZvaWNlIENsb25pbmcgd2l0aCBMb2NhbGl6ZWQgV2F0ZXJtYXJraW5nIn0=",
    "rm-source": "RoR-Browser",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "none",
    "origin": "chrome-extension://bfhkfdnddlhfippjbflipboognpdpoeh",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    #  "content-type": "application/epub+zip",
    "referrerPolicy": "strict-origin-when-cross-origin",
    "content-type": "application/pdf"
}

session = Session()

# Path to your PDF file
pdf_file_path = '2401.17264v2.pdf'

#  with open(pdf_file_path, 'rb') as pdf_file:
#  body = Path("body.txt").read_text().encode("utf-8")
body = Path(pdf_file_path).read_bytes()
response = session.post(url, data=body, headers=headers, cookies=cookie_header)

print(response.status_code)
print(response.text)
