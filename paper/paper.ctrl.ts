import { Request, Response } from "express";
import { db } from "../database";

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
      .query(`SELECT * FROM paper WHERE ${search} LIKE "%"?"%" LIMIT 50`, [
        query,
      ])
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
    return res.status(200).send(papers);
  } catch (err) {
    console.log(err);
    return res.status(400).send();
  }
}

export = {
  getPaper,
};
