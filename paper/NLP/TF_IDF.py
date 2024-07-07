import sys
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer # 사이킷런

def calculate_tfidf(input_data):
    vectorizer = TfidfVectorizer(stop_words='english')
    # input_data에 대한 TF-IDF 변환 수행
    tfidf_matrix = vectorizer.fit_transform(input_data)

    # tfidf_matrix.toarray() : 각 문장에서의 각 단어의 TF-IDF 점수를 배열 형태로 출력
    tfidf_array = tfidf_matrix.toarray()
    
    # get_feature_namers_out 예시)
    # "I like her brother" && "I hate her sister"
    # => ['brother', 'hate', 'her', 'like', 'sister'] 
    feature_names = vectorizer.get_feature_names_out()

    # 단어별 최대 TF-IDF 값을 계산
    # ex) "apple"이 세 문서에서 각각 0.1, 0.3, 0.2 TF-IDF 값 => apple : 0.3
    # axis=0 : 열별로 최대값을 찾는 것
    max_tfidf = np.max(tfidf_array, axis=0)

    # 단어와 그들의 TF-IDF 값을 매칭
    word_to_tfidf = dict(zip(feature_names, max_tfidf))

    # TF-IDF 값으로 정렬 (내림차순)
    sorted_words = sorted(word_to_tfidf.items(), key=lambda x: x[1], reverse=True)

    # 상위 10개 단어 출력
    top_words = sorted_words[:10]

    top_words_json = json.dumps({word: score for word, score in top_words})
    print(top_words_json)

    
def main():
    # 입력 데이터를 JSON 형식으로 받음
    input_data = json.loads(sys.stdin.read())

    # TF-IDF 계산 함수 호출
    calculate_tfidf(input_data)

# # 결과 출력
# print(json.dumps(tfidf_results))

if __name__ == "__main__":
    main()