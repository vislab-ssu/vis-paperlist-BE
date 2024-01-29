import tokenizer from "wink-tokenizer";
// 위 코드는 ES6 Modules(import문)
// import 문은 모던자바스크립트에서 권장
import { stop_words } from "../assets/stop_word";

export function processPapers(papers: any[]) {
  const tokenizer = require("wink-tokenizer");
  // 위 코드는 CommonJS(require문)
  // Node.js에서 널리 사용되는 모듈 시스템
  const myTokenizer = tokenizer();
  let tokenizedResult = papers.map((row: any) => {
    return myTokenizer.tokenize(row.abstract.toLowerCase());
  });

  // tokenize() 결과에서...word_list 정제 과정
  const word_list = tokenizedResult.map((result) =>
    // 불용어(stop_words) && "punctuation" tag인 결과 제거
    result
      .filter((word: any) => {
        return (
          !stop_words.includes(word.value) &&
          !["punctuation"].includes(word.tag)
        );
      })
      // { value: "value", tag: "tag" } 형식에서 tag 삭제
      .map((word: any) => word.value)
  );

  // 정제된 word_list의 word 발생 빈도 카운트를 계산한 keywordCount
  const keywordCount = word_list.map((result: any) =>
    result.reduce((acc: any, cur: any) => {
      const currentCount = acc[cur];
      const count = currentCount || 0;

      return {
        ...acc,
        [cur]: count + 1,
      };
    }, {})
  );

  // 검색 결과 paper의 모든 word 발생 빈도를 합한 totalKeyWordCount
  const totalKeywordCount = keywordCount.reduce((acc, cur) => {
    Object.entries(cur).forEach(([key, value]) => {
      if (!acc[key]) {
        acc[key] = value;
      } else {
        acc[key] += value;
      }
    });
    return acc;
  }, {});

  // keywordCount를 papers 응답결과의 각 paper마다 새로운 요소로 추가
  papers.forEach(
    (paper: any, index: number) => (paper.keywordList = keywordCount[index])
  );

  return { papers, totalKeywordCount };
}
