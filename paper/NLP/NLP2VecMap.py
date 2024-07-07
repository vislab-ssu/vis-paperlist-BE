import sys
import json
import nltk
import gensim
import string
# 데이터 전처리
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
# Word2Vec
from gensim.models import Word2Vec
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
# 시각화
import numpy as np
import matplotlib.pyplot as plt
# t-SNE
from sklearn.manifold import TSNE
import base64
from io import BytesIO
# PaCMAP
import pacmap
# DBSCAN
from sklearn.cluster import DBSCAN

## 머신러닝 워크플로우 ##
# 1.수집 - 2.점검및탐색 - 3.전처리및정제 - 4.모델링및훈련 - .....

###################################
####### 3. 전처리 및 정제 #########
###################################
    
# calculate_Doc2Vec에서 모델에 도입하기 이전에 전처리 적용
def preprocess_text(text):
    # 소문자 변환
    lower_text = text.lower()
    # NLTK 토큰화
    tokenized_text = word_tokenize(lower_text)
    # 불용어 제거
    stop_words = set(stopwords.words('english'))
    filtered_text = [word for word in tokenized_text if word not in stop_words and word not in string.punctuation]
    return filtered_text


###################################
####### 4. 모델링 및 훈련 #########
###################################

# Doc2Vec 모델에 적용.
# 인공신경망을 기반으로 하여 대량의 텍스트의 데이터로부터 단어 또는 문서의 벡터 표현을 학습한 모델을 활용
# Doc2Vec에서는 논문 하나를 백차원의 벡터로 표현

def calculate_Doc2Vec(input_data):
        
    tagged_data = [TaggedDocument(words=preprocess_text(doc['abstract']), tags=[i]) for i, doc in enumerate(input_data)]

    # Doc2Vec 모델 초기화 및 학습
    model = Doc2Vec(vector_size=300, window=5, min_count=10, workers=4, sample=1e-5, negative=5, epochs=400)
    model.build_vocab(tagged_data)
    model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)

    return model

###################################
####### 5. 차원축소 기법  #########
###################################

def mergeDoc2VecAndMetadata_PaCMAP(model, papers_info, top_n=50):
    # 문서 벡터 추출
    doc_ids = list(range(min(top_n, len(model.dv))))
    doc_vectors = np.array([model.dv[i] for i in doc_ids])

    # PaCMAP 적용하여 2차원 벡터 생성
    PaCMAP = pacmap.PaCMAP(n_components=2, n_neighbors=40, MN_ratio=0.5, FP_ratio=2.0)
    doc_vectors_2d = PaCMAP.fit_transform(doc_vectors, init="pca")

    visualize_Data = []
    
    for i in doc_ids:
        visualize_Data.append({ 'title': papers_info[i]["title"], 
                               'author': papers_info[i]["author"], 
                               'citation': papers_info[i]["citation"], 
                               'doi': papers_info[i]["DOI"],
                              'vector_x': doc_vectors_2d[i][0], 
                              'vector_y': doc_vectors_2d[i][1] })
        
    def float32_to_float(obj):
        if isinstance(obj, np.float32):
            return float(obj)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    # 예제 호출
    try:
        # ensure_ascii: 기본값 True / 비ASCII문자를 유니코드 이스케이프 시퀀스로 변환할지, 그대로 둘지를 결정
        print(json.dumps(visualize_Data, default=float32_to_float, ensure_ascii=False))
    except TypeError as e:
        print(e)

###################################
########   main  code    ##########
###################################

def main():
    # 입력 데이터를 JSON 형식으로 받음
    input_data = json.loads(sys.stdin.read())

    # 메타데이터 준비 (임시로 수정한 상태. original 파일과 비교하면 됨)
    papers_info = [{"title": doc['title'], 
                    "author": doc.get('authors', ['No Author']),  # 'authors' 키가 없을 때 기본값 설정
                    "abstract": doc['abstract'],
                    "citation": doc['citation'], 
                    "DOI": doc['DOI']} for doc in input_data]
    
    # # Doc2Vec 모델 학습
    model_Doc2Vec = calculate_Doc2Vec(input_data)

    mergeDoc2VecAndMetadata_PaCMAP(model_Doc2Vec, papers_info)

if __name__ == "__main__":
    main()