import { Request, Response } from "express";
import { db } from "../database";
import { stop_words } from "../assets/stop_word";

type SearchType = {
  search: "title" | "author" | "abstract";
  query: string;
};

async function getPaper(req: Request, res: Response) {
  try {
    console.log("GetPaper");
    let { search, query } = req.query as SearchType;
    if (!["title", "author", "abstract"].includes(search))
      return res.status(400).send();
    if (query.length < 3) return res.status(400).send();

    let connection = await db.getConnection();

    let [papers, fields] = await connection
      .query(
        `SELECT * FROM papers p\
        JOIN journals j ON p.conference_session_id=j.id\
        WHERE ${search} LIKE "%"?"%"\
        LIMIT 50`,
        [query]
      )
      .then(
        (res: any) => {
          return res;
        },
        (err: any) => {
          console.log(err);
          return err;
        }
      );
    await connection.release(); // connection이 이루어진 후에는 반드시 release 해야함

    //////////////////
    // 키워드 처리 코드 //
    //////////////////

    // abstract tokenize
    const tokenizer = require("wink-tokenizer");
    const myTokenizer = tokenizer();
    let tokenizedResult = papers.map((row: any) => {
      return myTokenizer.tokenize(row.abstract.toLowerCase());
    });
    // tokenize 결과에서...word_list 정제 과정
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

    // 검색 결과 paper의 모든 word 발생 빈도를 합하고 그 중
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

    /////////////////////////////////////////////////////////////////
    // 객체를 배열로 변환하고 값에 따라 정렬
    var items = Object.keys(totalKeywordCount).map(function (key) {
      return { word: key, size: totalKeywordCount[key] };
    });
    items.sort(function (a, b) {
      return b.size - a.size;
    });
    // 상위 10개 요소 추출
    var topItems = items.slice(0, 10);
    // wordcloud에 사용할 수 있는 형식으로 변환
    var myWords = topItems.map(function (item) {
      return { word: item.word, size: item.size * 10 }; // size를 조정하여 wordcloud에 적합하게 만들기
    });

    console.log(myWords);
    ////////////////////////////////////////////////////////////////

    // return res.status(200).send(papers);
    return res.status(200).send({ papers: papers, myWords: myWords });
  } catch (err) {
    console.log(err);
    return res.status(400).send();
  }
}

export = {
  getPaper,
};
