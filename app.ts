import express, { Request, Response } from "express";
import paper from "./paper";
require("dotenv").config();
const { PORT } = process.env;

const app = express();
const port = PORT || 3000;

app.use(require("cors")());
// HTTP body 파싱 관련
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use("/paper", paper);

app.get("/", (req: Request, res: Response) => {
  return res.status(200).send();
});

app.listen(port, () => {
  console.log(`Backend is listening on ${port}`);
});
