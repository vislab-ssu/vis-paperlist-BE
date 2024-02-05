# OC_api_test.py
from requests import get

# API 호출 설정
API_CALL = "https://opencitations.net/index/api/v1/references/10.1186/1756-8722-6-59"
HTTP_HEADERS = {"authorization": "089eb33b-2ab6-4679-9425-9ab03157d3e0"}

# API 호출
response = get(API_CALL, headers=HTTP_HEADERS)

# 응답 상태 코드 확인
print("Status Code:", response.status_code)

# 응답 내용 출력
if response.status_code == 200:
    print("Response Content:", response.text)
else:
    print("Failed to fetch data")
