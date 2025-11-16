// .eleventy.js
module.exports = function (eleventyConfig) {
  return {
    dir: {
      input: "site", // テンプレート置き場
      includes: "_includes",
      data: "_data",
      output: "_site", // 出力先
    },
  };
};
