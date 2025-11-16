// site/_data/f14.js
const path = require("path");
const fs = require("fs");

const jsonPath = path.join(
  __dirname,
  "..",
  "..",
  "data",
  "f14_proposals_ja.json"
);
// もし clean 版を使うなら ↑ を "f14_proposals_ja_clean.json" に変えてOK

const raw = fs.readFileSync(jsonPath, "utf-8");
const data = JSON.parse(raw);

// このモジュールの名前 f14 が、そのままテンプレートの変数名になる
module.exports = data;
