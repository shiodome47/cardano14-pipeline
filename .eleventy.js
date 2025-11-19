// .eleventy.js
module.exports = function (eleventyConfig) {
  // --- markdown フィルタ追加 ---
  const markdownIt = require("markdown-it");

  // HTML をそのまま通す用（既存の markdown フィルタ）
  const md = new markdownIt({
    html: true,
    breaks: true,
    linkify: true,
  });

  // HTML を無効化してサニタイズする用（新しい md_sanitize フィルタ）
  const mdSafe = new markdownIt({
    html: false, // ← ここがポイント：HTMLタグは解釈しない
    breaks: true,
    linkify: true,
  });

  // 既存：生の markdown を HTML に変換（HTML許可）
  eleventyConfig.addFilter("markdown", (content) => {
    if (!content) return "";
    return md.render(content);
  });

  // <hr> で structured HTML をセクションごとに分割するフィルタ
  eleventyConfig.addFilter("split_hr_sections", (content) => {
    if (!content) return [];
    const normalized = String(content).replace(/<hr\s*\/?>/gi, "<hr>");
    return normalized
      .split("<hr>")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
  });

  // 新規：サニタイズ付き markdown フィルタ
  eleventyConfig.addFilter("md_sanitize", (content) => {
    if (!content) return "";
    return mdSafe.render(String(content));
  });
  // --- ここまで markdown フィルタ ---

  // styles フォルダをそのまま _site/styles にコピー
  eleventyConfig.addPassthroughCopy("site/styles");

  return {
    dir: {
      input: "site",
      output: "_site",
    },
  };
};
