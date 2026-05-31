#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

###############################################################################
def get_morphs_tags(tagged):
    """
    형태소 분석 결과 문자열에서 (형태소, 품사) 튜플 리스트를 반환한다.

    형식: morph1/POS1+morph2/POS2+...
    특이 사항:
      - 형태소 자체가 '+'인 경우: 구분자 '+' 다음에 '+/POS' 패턴으로 나타남
        예) BB/SL++/SW  ->  ('BB','SL'), ('+','SW')
      - 형태소 자체가 '/'인 경우: '//POS' 패턴으로 나타남
        예) 강원/NNP+//SP+인제/NNP  ->  ('강원','NNP'), ('/','SP'), ('인제','NNP')
      - 형태소 내부에 '/'가 포함될 수 있음 (마지막 '/'가 품사 구분자)
        예) Supreme/Nike/NNP  ->  ('Supreme/Nike','NNP')
      - 품사 태그는 영문 대문자로만 구성됨
    """
    result = []

    i = 0
    n = len(tagged)

    while i < n:
        found = False
        j = i

        while j < n:
            # 현재 위치 j 이후에서 '/' 찾기
            slash_pos = tagged.find('/', j)

            if slash_pos == -1:
                # '/' 없음: 형태소만 있고 품사 없음 (비정상 케이스)
                result.append((tagged[i:], ''))
                i = n
                found = True
                break

            # '/' 이후 품사 태그(영문 대문자) 스캔
            pos_end = slash_pos + 1
            while pos_end < n and tagged[pos_end].isupper() and tagged[pos_end].isalpha():
                pos_end += 1

            if pos_end > slash_pos + 1:
                # 품사 태그가 하나 이상 있음
                # 이 '/품사' 다음이 '+' (구분자) 또는 문자열 끝이면 -> 현재 유닛 완성
                if pos_end == n or tagged[pos_end] == '+':
                    morph = tagged[i:slash_pos]
                    pos   = tagged[slash_pos + 1:pos_end]
                    result.append((morph, pos))
                    # 구분자 '+' 건너뛰어 다음 유닛 시작
                    i = pos_end + 1 if pos_end < n else n
                    found = True
                    break
                else:
                    # 품사 태그 뒤에 또 다른 문자가 있음
                    # -> 이 '/'는 형태소 내부의 '/'이므로 다음 '/'부터 다시 탐색
                    j = slash_pos + 1
            else:
                # '/' 바로 뒤가 품사 태그가 아님 (형태소 내부 '/')
                j = slash_pos + 1

        if not found:
            break

    return result

###############################################################################
if __name__ == "__main__":

    if len(sys.argv) != 2:
        print( f"[Usage] {sys.argv[0]} in-file", file=sys.stderr)
        sys.exit()

    with open(sys.argv[1], encoding='utf-8') as fin:

        for line in fin:

            # 2 column format
            segments = line.split('\t')

            if len(segments) < 2:
                continue

            # result : list of tuples
            result = get_morphs_tags(segments[1].rstrip())

            for morph, tag in result:
                print(morph, tag, sep='\t')
