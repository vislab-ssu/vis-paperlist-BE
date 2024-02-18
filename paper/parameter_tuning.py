import sys
import json
import numpy as np
import string
import nltk
import matplotlib.pyplot as plt
# 데이터 전처리
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
# Doc2Vec
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
# tSNE
from sklearn.manifold import TSNE
# PaCMAP
import pacmap
# DBSCAN
from sklearn.cluster import DBSCAN
# Grid-Search
from sklearn.model_selection import ParameterGrid


# 데이터 전처리 함수
def preprocess_text(text):
    lower_text = text.lower()
    tokenized_text = word_tokenize(lower_text)
    stop_words = set(stopwords.words('english'))
    filtered_text = [word for word in tokenized_text if word not in stop_words and word not in string.punctuation]
    return filtered_text

# Grid-Search 실행 및 시각화 함수
def run_grid_search_visualization(input_data):
    param_grid = {
        'vector_size': [100, 200],
        'window': [5, 10],
        'min_count': [1, 2],
        'epochs': [20, 40],
        # 'perplexity': [20, 30, 40, 50],
        'n_neighbors': [20, 30, 40, 50]
    }
    
    # 파라미터 조합의 수를 계산하여 subplot의 행과 열 결정
    num_combinations = len(list(ParameterGrid(param_grid)))
    num_rows = int(np.ceil(np.sqrt(num_combinations)))
    num_cols = int(np.ceil(num_combinations / num_rows))
    
    # 전체 결과를 보여줄 큰 그림 생성
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(num_cols*3, num_rows*3))
    
    # 각 파라미터 조합에 대해 모델 학습 및 시각화
    for i, params in enumerate(ParameterGrid(param_grid)):
        ax = axes[i // num_cols, i % num_cols] if num_rows > 1 else axes[i]
        
        model = Doc2Vec(vector_size=params['vector_size'], window=params['window'],
                        min_count=params['min_count'], workers=4, epochs=params['epochs'])
        tagged_data = [TaggedDocument(words=preprocess_text(doc['abstract']), tags=[i]) for i, doc in enumerate(input_data)]
        model.build_vocab(tagged_data)
        model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)
        
        doc_vectors = np.array([model.dv[i] for i in range(len(tagged_data))])
        # tsne = TSNE(n_components=2, random_state=0, perplexity=params['perplexity'])
        # doc_vectors_2d = tsne.fit_transform(doc_vectors)
        PaCMAP = pacmap.PaCMAP(n_components=2, n_neighbors=params['n_neighbors'], MN_ratio=0.5, FP_ratio=2.0)
        doc_vectors_2d = PaCMAP.fit_transform(doc_vectors)
        clustering = DBSCAN(eps=0.2, min_samples=5).fit(doc_vectors_2d)
        
        ax.axis('off')
        ax.scatter(doc_vectors_2d[:, 0], doc_vectors_2d[:, 1], alpha=0.5, c=clustering.labels_)
        # ax.set_title(f"VecSize: {params['vector_size']}, Window: {params['window']},\nMinCount: {params['min_count']}, Epochs: {params['epochs']}, perplexity: {params['perplexity']}", fontsize=5)
        ax.set_title(f"VecSize: {params['vector_size']}, Window: {params['window']},\nMinCount: {params['min_count']}, Epochs: {params['epochs']}, neighbors: {params['n_neighbors']}", fontsize=5)

    # 사용되지 않는 subplot 숨기기
    for j in range(i + 1, num_rows * num_cols):
        fig.delaxes(axes.flatten()[j])

    # 간격 조정 및 전체 레이아웃 조정
    plt.tight_layout()
    plt.show()

# 메인 함수
def main():
    input_data = json.loads(sys.stdin.read())
    run_grid_search_visualization(input_data)

if __name__ == "__main__":
    main()