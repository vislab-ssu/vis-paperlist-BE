import { Request, Response } from "express";
import { db } from "../database";
import { processPapers } from "./tokenizerModule";
import { processWordCloud } from "./NLP/TF_IDF_wordCloud";
import ieeeData_2008 from "../crawling/IEEEVIS_WEEK/Result/IEEE_2008.json";
import ieeeData_2009 from "../crawling/IEEEVIS_WEEK/Result/IEEE_2009.json";
import ieeeData_2010 from "../crawling/IEEEVIS_WEEK/Result/IEEE_2010.json";

type SearchType = {
  search: "title" | "author" | "abstract";
  query: string;
};

const { spawn } = require("child_process");

async function getTfidfForAbstracts(abstracts: string[]) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python3", ["./paper/NLP/TF_IDF.py"]);

    // Python 스크립트에 데이터 전송
    pythonProcess.stdin.write(JSON.stringify(abstracts));
    pythonProcess.stdin.end();

    // 결과 수집 (python 프로세스의 표준 출력에서 데이터 읽어옴: stdout)
    let data = "";
    pythonProcess.stdout.on("data", (chunk) => {
      data += chunk;
    });

    // 처리 완료
    pythonProcess.stdout.on("end", () => {
      // resolve(JSON.parse(data));
      const tfidfData = JSON.parse(data);
      resolve(tfidfData);
    });

    // 에러 처리
    pythonProcess.stderr.on("data", (data) => {
      console.error(`stderr: ${data}`);
      reject(data);
    });
  });
}

async function getVecMapReduceForAbstracts(papers: string[]) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python3", ["./paper/NLP/NLP2VecMap.py"]);

    // Python 스크립트에 데이터 전송
    pythonProcess.stdin.write(JSON.stringify(papers));
    pythonProcess.stdin.end();

    // 결과 수집을 위한 변수 초기화
    let rawData = "";

    // 데이터 수집 (python 프로세스의 표준 출력에서 데이터 읽어옴: stdout)
    pythonProcess.stdout.on("data", (chunk) => {
      // 비동기적으로 데이터를 수신하고 처리하는 과정에서 데이터가 여러 청크로 나누어져 도착할 수 있음
      rawData += chunk;
    });

    // 처리 완료
    pythonProcess.stdout.on("end", () => {
      try {
        const processedData = JSON.parse(rawData); // 전체 데이터를 여기서 파싱
        // console.log(processedData);
        resolve(processedData);
      } catch (error) {
        console.error("JSON parsing error:", error);
        reject(error);
      }
    });

    // 에러 처리
    pythonProcess.stderr.on("data", (data) => {
      console.error(`stderr: ${data}`);
      reject(data);
    });
  });
}

async function getPaper(req: Request, res: Response) {
  try {
    console.log("GetPaper");
    let { search, query } = req.query as SearchType;
    if (!["title", "author", "abstract"].includes(search))
      return res.status(400).send();
    if (query.length < 3) return res.status(400).send();

    let connection = await db.getConnection();

    let [papers, fields] = await connection
      // .query(
      //   `SELECT * FROM papers p\
      //   JOIN journals j ON p.conference_session_id=j.id\
      //   WHERE ${search} LIKE "%"?"%"\
      //   `,
      //   [query]
      // )
      .query(
        `SELECT p.id AS pid, p.abstract, p.title, p.author, p.conference_session_id, p.date, p.DOI, p.citation,\
        j.id, j.name, j.upper_category_id, j.year, jo.name AS joname FROM papers p\
        JOIN journals j ON p.conference_session_id=j.id\
        LEFT JOIN journals jo ON j.upper_category_id=jo.id\
        WHERE ${search} LIKE "%"?"%"\
        `,
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

    ///////////////////////////
    //////// NLP 처리 /////////
    ///////////////////////////

    // 키워드 빈도 처리//
    const { papers: processedPapers, totalKeywordCount: tokenizedResultCount } =
      processPapers(papers);
    // const { myWords } = processWordCloud(tokenizedResultCount);

    const abstracts = papers.map((paper: any) => paper.abstract);

    // TF-IDF 방식
    const tfidfResults = await getTfidfForAbstracts(abstracts);
    const { myWords } = processWordCloud(tfidfResults);

    // Word2Vec 방식
    const Word2VecResults = await getVecMapReduceForAbstracts(papers);
    console.log(Word2VecResults);

    //////// 데이터 반환 /////////
    // return res.status(200).send(papers);
    return res.status(200).send({
      papers: processedPapers,
      myWords: myWords,
      embeddingData: Word2VecResults,
    });
  } catch (err) {
    console.log(err);
    return res.status(400).send();
  }
}

export = {
  getPaper,
};
