from gensim.summarization import bm25
import jieba

class BM25Model:
    def __init__(self, data_list):
        self.data_list = data_list
        self.corpus = self.load_corpus()

    def bm25_similarity(self, query, num_best=1):
        query = jieba.lcut(query)  # 分词
        bm = bm25.BM25(self.corpus)
        scores = bm.get_scores(query)
        id_score = [(i, score) for i, score in enumerate(scores)]
        id_score.sort(key=lambda e: e[1], reverse=True)
        return id_score[0: num_best]

    def load_corpus(self):
        corpus = [jieba.lcut(data) for data in self.data_list]
        return corpus


