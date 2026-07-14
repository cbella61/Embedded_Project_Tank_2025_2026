const fs = require("fs");
const path = require("path");
const { marked } = require("marked");

if (process.argv.length !== 4) {
  console.error("Uso: node render_markdown.js input.md output.html");
  process.exit(1);
}

const inputPath = path.resolve(process.argv[2]);
const outputPath = path.resolve(process.argv[3]);
const cssPath = path.join(__dirname, "print.css");
const markdown = fs.readFileSync(inputPath, "utf8");
const css = fs.readFileSync(cssPath, "utf8");
const titleMatch = markdown.match(/^#\s+(.+)$/m);
const title = titleMatch ? titleMatch[1] : "Documentazione tank";

const html = `<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title}</title>
  <style>${css}</style>
</head>
<body>
${marked.parse(markdown, { gfm: true })}
</body>
</html>
`;

fs.writeFileSync(outputPath, html, "utf8");
