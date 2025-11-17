/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./site/**/*.{njk,html,js}"],
  theme: {
    extend: {
      colors: {
        carda: {
          bg: "#E4ECFF", // ペールブルー背景
          surface: "#F9FBFF", // カード用の白寄り
          primary: "#315CFF", // 見出し・リンク
          primarySoft: "#7C9DFF",
          textMain: "#0F172A", // 文字色（ほぼ slate-900）
          textSub: "#6B7280",
        },
      },
    },
  },
  plugins: [],
};
