import mysql from "mysql2";
require("dotenv").config();
const { DB_HOST, DB_USER, DB_PASSWORD, DB_DB, DB_PORT } = process.env;

const pool = mysql.createPool({
  host: DB_HOST,
  user: DB_USER,
  password: DB_PASSWORD,
  database: DB_DB,
  port: Number.parseInt(DB_PORT!),
});

export const db = pool.promise();
