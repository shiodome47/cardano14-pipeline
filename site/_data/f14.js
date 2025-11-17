// site/_data/f14.js
const path = require("path");
const fs = require("fs");

// data ディレクトリ
const dataDir = path.join(__dirname, "..", "..", "data");

// 日本語・英語それぞれの JSON を読む
const jaPath = path.join(dataDir, "f14_proposals_ja.json");
const enPath = path.join(dataDir, "f14_proposals_en.json");

const ja = JSON.parse(fs.readFileSync(jaPath, "utf-8"));
const en = JSON.parse(fs.readFileSync(enPath, "utf-8"));

// Challenge 名の表示用マップ
const CHALLENGE_LABELS = {
  "Cardano Use Cases Partners & Pr": "Cardano Use Cases: Partners & Products",
  "Cardano Use Cases Concept": "Cardano Use Cases: Concept",
  "Cardano Open Developers": "Cardano Open: Developers",
  "Cardano Open Ecosystem": "Cardano Open: Ecosystem",
  "Sponsored by leftovers": "Sponsored by leftovers",
  Withdrawn: "Withdrawn",
};

// EN を proposal_id で引けるようにしておく
const enById = new Map(en.map((p) => [p.proposal_id, p]));

// JA をベースに EN 情報をマージし、最後に challenge ラベルを整形
const merged = ja.map((jp) => {
  const baseEn = enById.get(jp.proposal_id) || {};
  const mergedOne = {
    // まず EN 全部（problem_en / solution_en / about_en / team_en など）
    ...baseEn,
    // その上から JA 側を上書き（title_ja / summary_ja など）
    ...jp,
  };

  return {
    ...mergedOne,
    challenge: CHALLENGE_LABELS[mergedOne.challenge] || mergedOne.challenge,
  };
});

module.exports = merged;
