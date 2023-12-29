import express from "express";
import ctrl from "./paper.ctrl";

const router = express.Router();

router.get("", ctrl.getPaper);

export default router;
