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

# 처음 실행시 설치 필요
# nltk.download('punkt')
# nltk.download('stopwords')

def preprocess_text(text):
    # 소문자 변환
    lower_text = text.lower()
    # NLTK 토큰화
    tokenized_text = word_tokenize(lower_text)
    # 불용어 제거
    stop_words = set(stopwords.words('english'))
    filtered_text = [word for word in tokenized_text if word not in stop_words and word not in string.punctuation]
    return filtered_text

def mergeDoc2VecAndMetadata_tSNE(model, papers_info, top_n=50):
    # 문서 벡터 추출
    doc_ids = list(range(min(top_n, len(model.dv))))
    doc_vectors = np.array([model.dv[i] for i in doc_ids])

    # t-SNE 모델 적용하여 2차원 벡터 생성
    tsne = TSNE(n_components=2, random_state=0, perplexity=40)
    doc_vectors_2d = tsne.fit_transform(doc_vectors)

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

def tSNE_visualize(model, top_n=50):
    # 상위 N개의 단어와 해당 벡터 추출
    # model.wv.index_to_key : 빈도 수에따라 정렬된 모델의 단어 리스트
    words = model.wv.index_to_key[:top_n]   
     # model.wv[word] : 주어진 `word`에 해당하는 임베딩 벡터 반환
    word_vectors = np.array([model.wv[word] for word in words])    

    # t-SNE 모델 적용하여 2차원 벡터 생성
    tsne = TSNE(n_components=2, random_state=0)
    word_vectors_2d = tsne.fit_transform(word_vectors)

    # DBSCAN 클러스터링 수행
    clustering = DBSCAN(eps=0.5, min_samples=2).fit(word_vectors_2d)
    
    # 시각화
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(word_vectors_2d[:, 0], word_vectors_2d[:, 1], c=clustering.labels_)
    legend1 = plt.legend(*scatter.legend_elements(), title="Clusters")
    plt.gca().add_artist(legend1)

    for i, word in enumerate(words):
        plt.annotate(word, xy=(word_vectors_2d[i, 0], word_vectors_2d[i, 1]), xytext=(5, 2),
                     textcoords='offset points', ha='right', va='bottom')
    
    plt.show()

def tSNE_visualize_doc2vec(model, labels=None, top_n=50):
    # 문서 벡터 추출
    doc_ids = list(range(min(top_n, len(model.dv))))
    doc_vectors = np.array([model.dv[i] for i in doc_ids])

    # t-SNE 모델 적용하여 2차원 벡터 생성
    tsne = TSNE(n_components=2, random_state=0, perplexity=40)
    doc_vectors_2d = tsne.fit_transform(doc_vectors)

    # 시각화
    plt.figure(figsize=(12, 8))
    for i, doc_id in enumerate(doc_ids):
        plt.scatter(doc_vectors_2d[i, 0], doc_vectors_2d[i, 1])
        plt.annotate(labels[i] if labels else f'Doc {doc_id}', xy=(doc_vectors_2d[i, 0], doc_vectors_2d[i, 1]),
                     xytext=(5, 2), textcoords='offset points', ha='right', va='bottom')
    
    plt.show()

def tSNE_visualize_doc2vec_DBSCAN(model, labels=None, top_n=50):
    # 문서 벡터 추출
    doc_ids = list(range(min(top_n, len(model.dv))))
    doc_vectors = np.array([model.dv[i] for i in doc_ids])

    # t-SNE 모델 적용하여 2차원 벡터 생성
    tsne = TSNE(n_components=2, random_state=0, perplexity=20)
    doc_vectors_2d = tsne.fit_transform(doc_vectors)

    # DBSCAN 클러스터링 수행
    clustering = DBSCAN(eps=0.5, min_samples=2).fit(doc_vectors_2d)

    # 시각화
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(doc_vectors_2d[:, 0], doc_vectors_2d[:, 1], c=clustering.labels_)
    legend1 = plt.legend(*scatter.legend_elements(), title="Clusters")
    plt.gca().add_artist(legend1)

    for i, doc_id in enumerate(doc_ids):
        plt.annotate(labels[i] if labels else f'Doc {doc_id}', xy=(doc_vectors_2d[i, 0], doc_vectors_2d[i, 1]),
                     xytext=(5, 2), textcoords='offset points', ha='right', va='bottom')
    
    plt.show()


def PaCMAP_visualize(model, top_n=50):
    # 상위 N개의 단어와 해당 벡터 추출
    words = model.wv.index_to_key[:top_n]
    word_vectors = np.array([model.wv[word] for word in words])

    # PaCMAP 적용하여 2차원 벡터 생성
    embedding = pacmap.PaCMAP(n_components=2, n_neighbors=None, MN_ratio=0.5, FP_ratio=2.0)
    word_vectors_2d = embedding.fit_transform(word_vectors, init="pca")

    # 시각화
    plt.figure(figsize=(12, 8))
    for i, word in enumerate(words):
        plt.scatter(word_vectors_2d[i, 0], word_vectors_2d[i, 1])
        plt.annotate(word, xy=(word_vectors_2d[i, 0], word_vectors_2d[i, 1]), xytext=(5, 2),
                     textcoords='offset points', ha='right', va='bottom')
    
    plt.show()

def PaCMAP_visualize_doc2Vec(model, labels=None, top_n=50):
    doc_ids = list(range(min(top_n, len(model.dv))))
    doc_vectors = np.array([model.dv[i] for i in doc_ids])

    # PaCMAP 적용하여 2차원 벡터 생성
    embedding = pacmap.PaCMAP(n_components=2, n_neighbors=None, MN_ratio=0.5, FP_ratio=2.0)
    doc_vectors_2d = embedding.fit_transform(doc_vectors, init="pca")

    # 시각화
    plt.figure(figsize=(12, 8))
    for i, doc_id in enumerate(doc_ids):
        plt.scatter(doc_vectors_2d[i, 0], doc_vectors_2d[i, 1])
        plt.annotate(labels[i] if labels else f'Doc {doc_id}', xy=(doc_vectors_2d[i, 0], doc_vectors_2d[i, 1]), 
                     xytext=(5, 2), textcoords='offset points', ha='right', va='bottom')
    
    plt.show()
    
###################################
######### create model ############
###################################
    
def calculate_Word2Vec(input_data):
    tokenized_data = []

    # 모든 논문 abstract을 하나의 데이터 세트로 결합
    for abstract in input_data:
        sentences = sent_tokenize(abstract)
        for sentence in sentences:
            tokenized_data.append(preprocess_text(sentence))

    # 모든 데이터에 대한 하나의 Word2Vec 모델 학습
    model = Word2Vec(tokenized_data, vector_size=100, window=5, min_count=1, workers=4)

    return model


def calculate_Doc2Vec(input_data):
        
    tagged_data = [TaggedDocument(words=preprocess_text(doc['abstract']), tags=[i]) for i, doc in enumerate(input_data)]

    # Doc2Vec 모델 초기화 및 학습
    model = Doc2Vec(vector_size=100, window=5, min_count=1, workers=4, epochs=40)
    model.build_vocab(tagged_data)
    model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)

    return model

    
def main():
    # 입력 데이터를 JSON 형식으로 받음
    input_data = json.loads(sys.stdin.read())

    # 메타데이터 준비
    papers_info = [{"title": doc['title'], "author": doc['author'], "citation": doc['citation'], 
                    "DOI": doc['DOI']} for doc in input_data]
    
    # Word2Vec 모델 생성
    # model_Word2Vec = calculate_Word2Vec(input_data2)

    # Doc2Vec 모델 학습
    model_Doc2Vec = calculate_Doc2Vec(input_data)
    mergeDoc2VecAndMetadata_tSNE(model_Doc2Vec, papers_info)
    
    # t-SNE 시각화 실행
    # tSNE_visualize(model_Word2Vec)
    tSNE_visualize_doc2vec(model_Doc2Vec)
    tSNE_visualize_doc2vec_DBSCAN(model_Doc2Vec)

    # PaCMAP 시각화 실행
    # PaCMAP_visualize(model_Word2Vec)
    # PaCMAP_visualize_doc2Vec(model_Doc2Vec)


if __name__ == "__main__":
    main()