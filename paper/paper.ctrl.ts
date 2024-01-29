import { Request, Response } from "express";
import { db } from "../database";
import { processPapers } from "./tokenizerModule";
import { processWordCloud } from "./wordCloud";

type SearchType = {
  search: "title" | "author" | "abstract";
  query: string;
};

const { spawn } = require("child_process");

async function getTfidfForAbstracts(abstracts: string[]) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python", ["./paper/TF_IDF.py"]);

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

    // 키워드 빈도 처리//
    const { papers: processedPapers, totalKeywordCount: tokenizedResultCount } =
      processPapers(papers);
    // const { myWords } = processWordCloud(tokenizedResultCount);

    // TF-IDF 방식
    const abstracts = papers.map((paper: any) => paper.abstract);
    const tfidfResults = await getTfidfForAbstracts(abstracts);
    const { myWords } = processWordCloud(tfidfResults);
    console.log(myWords);

    // return res.status(200).send(papers);
    return res.status(200).send({ papers: processedPapers, myWords: myWords });
  } catch (err) {
    console.log(err);
    return res.status(400).send();
  }
}

export = {
  getPaper,
};
