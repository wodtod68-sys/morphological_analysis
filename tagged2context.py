#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import get_morphs_tags as mf

# 색인 대상 품사 집합
INDEX_POS = {'NNG', 'NNP', 'NR', 'NNB', 'SL', 'SH', 'SN'}

# 단일어 색인 대상 품사 (SL은 복합어에 속하지 않을 때만 단일어 색인)
SINGLE_POS = {'NNG', 'NNP', 'SH', 'SL'}

###############################################################################
# 명사, 복합명사 추출
def get_index_terms(mt_list):
    """
    (형태소, 품사) 튜플 리스트에서 색인어(단일어 + 복합어)를 추출한다.

    색인 대상 품사: NNG, NNP, NR, NNB, SL, SH, SN

    단일어 규칙:
      - NNG, NNP, SH: 항상 단일어로 색인
      - SL: 복합어에 속하지 않는 경우에만 단일어로 색인
      - NR, NNB, SN: 단일어 색인 안함

    복합어 규칙:
      - 어절 내 연속된 색인 대상 형태소가 2개 이상이면 복합어 추출
      - 연속 형태소가 3개 이상이면 가장 긴 복합어(전체 결합형)만 출력
        (중간 길이의 복합어는 출력하지 않음)

    출력 순서: 단일어들을 먼저 출력한 후 복합어 출력
    """
    nouns = []

    # 어절 내 형태소들을 연속된 색인 대상 그룹으로 나눔
    # 그룹: 연속된 (형태소, 품사) 쌍의 리스트
    groups = []
    current_group = []

    for morph, pos in mt_list:
        if pos in INDEX_POS:
            current_group.append((morph, pos))
        else:
            if current_group:
                groups.append(current_group)
                current_group = []

    if current_group:
        groups.append(current_group)

    # 각 그룹에서 단일어와 복합어 추출
    for group in groups:
        singles = []
        in_compound = len(group) >= 2  # 이 그룹이 복합어를 이룸

        for morph, pos in group:
            if pos in SINGLE_POS:
                # SL은 복합어에 속하지 않는 경우에만 단일어
                if pos == 'SL' and in_compound:
                    pass  # SL이 복합어에 속하면 단일어 색인 안함
                else:
                    singles.append(morph)
            # NR, NNB, SN은 단일어 색인 안함

        # 복합어 처리
        if len(group) >= 2:
            compound = ''.join(morph for morph, pos in group)

            if len(group) == 2:
                # 2개 연속: 단일어 + 복합어
                nouns.extend(singles)
                nouns.append(compound)
            else:
                # 3개 이상 연속: 단일어 + 가장 긴 복합어만
                nouns.extend(singles)
                nouns.append(compound)
        else:
            # 단독 형태소: 단일어만
            nouns.extend(singles)

    return nouns

###############################################################################
# Converting POS tagged corpus to a context file
def tagged2context( input_file, output_file):

    with open( input_file, "r", encoding='utf-8') as fin, open( output_file, "w", encoding='utf-8') as fout:

        for line in fin:

            # 빈 라인 (문장 경계)
            if line[0] == '\n':
                print(file=fout)
                continue

            try:
                ej, tagged = line.split(sep='\t')
            except:
                print(line, file=sys.stderr)
                continue

            # 형태소, 품사 추출
            # result : list of tuples
            result = mf.get_morphs_tags(tagged.rstrip())

            # 색인어 추출
            terms = get_index_terms(result)

            # 색인어 출력
            for term in terms:
                print(term, end=" ", file=fout)

###############################################################################
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print( f"[Usage] {sys.argv[0]} file(s)", file=sys.stderr)
        sys.exit()

    for input_file in sys.argv[1:]:
        output_file = input_file + ".context"
        print( f"processing {input_file} -> {output_file}", file=sys.stderr)

        # 형태소 분석 파일 -> 문맥 파일
        tagged2context( input_file, output_file)
