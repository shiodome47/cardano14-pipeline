// .eleventy.js
module.exports = function (eleventyConfig) {
  // styles フォルダをそのまま _site/styles にコピー
  eleventyConfig.addPassthroughCopy("site/styles");

  return {
    dir: {
      input: "site",
      output: "_site",
    },
  };
};
