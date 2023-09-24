import sys
import requests
import numpy as np
from konlpy.tag import Mecab
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


def text_classification(comment):
    r = requests.get("https://data.hossam.kr/korean_stopwords.txt")
    r.encoding = 'utf-8'
    stopwords = r.text.split("\n")

    vocab_size = 19204
    max_word_count = 512
    category = ['IT,과학', '경제', '사회', '생활,문화', '세계', '정치']

    checkpoint_path = "D:/tensorflowcheckpoint/cp-0002-ckpt"
    restore_model = load_model(checkpoint_path)

    # 형태소 분석 엔진
    if sys.platform == 'win32':
        mecab = Mecab(dicpath="C:/mecab/mecab-ko-dic")
    else:
        mecab = Mecab()

    # 형태소 분석
    morphs = mecab.morphs(comment)

    # 불용어 제거
    tmp_word = []
    for j in morphs:
        if j not in stopwords:
            tmp_word.append(j)

    # 입력 데이터의 차원을 맞추기 위해 리스트로 감쌈
    word_set = [tmp_word]

    # 자주 등장하는 단어를 제외한 나머지 단어를 OOV로 처리하여 최종 토큰화 수행
    tokenizer = Tokenizer(vocab_size, oov_token = 'OOV')
    tokenizer.fit_on_texts(word_set)
    token_set = tokenizer.texts_to_sequences(word_set)

    # 최대 길이에 맞춰서 패딩 처리
    pad_token_set = pad_sequences(token_set, maxlen=max_word_count)

    # 전처리가 완료된 말뭉치를 학습모델에 적용하여 예측하기
    result = restore_model.predict(pad_token_set)

    # 결과 분석
    arg_result = np.argmax(result, axis=-1)
    v = arg_result[0]

    return category[v]


# 터미널을 통해 직접 실행하는 경우만 구동되는 구문
if __name__ == "__main__": 
    args = sys.argv[1:]
    comment = " ".join(args)
    
    category = text_classification(comment)
    
    print("입력한 문장의 카테고리는 {}입니다.".format(category))
    print("\n여기까지가 이전에 수행한 모델의 결과입니다.\n")
    print("27~29까지가 checkpoint를 사용한 모델 결과 확인입니다.")