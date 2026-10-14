import { readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { marked } from 'marked'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
export const documents = [
  'README.md', 'DIY_FIRMWARE.md', 'k151-kit-route/README.md',
  'v1-xl330-route/README.md', 'v0-sg90-route/README.md',
  'scs0009-serial-route/README.md', 'k151-body-route/README.md',
  'hermes-integration/README.md', 'pcb/m5-pantilt-v1.0/manufacture/README.md',
]
const htmlPath = file => file.endsWith('README.md')
  ? file.slice(0, -'README.md'.length) + 'index.html' : file.replace(/\.md$/, '.html')
const outputs = new Map(documents.map(file => [file, htmlPath(file)]))
const escape = text => text.replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
const slug = text => text.toLowerCase().replace(/<[^>]*>/g, '').replace(/[^\p{L}\p{N}\s_-]/gu, '').trim().replace(/\s+/g, '-')
const css = `
*{box-sizing:border-box}body{margin:0;background:#f6f8fa;color:#17202a;font:16px/1.75 system-ui,-apple-system,"PingFang SC",sans-serif}
main{max-width:1120px;margin:32px auto;padding:32px;background:white;border:1px solid #dce3eb;border-radius:12px}
h1,h2,h3{line-height:1.35;scroll-margin-top:20px}h1{font-size:30px}h2{margin-top:36px;border-bottom:1px solid #e4e8ee;padding-bottom:10px}
a{color:#175ca3;overflow-wrap:anywhere}p,li{overflow-wrap:anywhere}blockquote{border-left:4px solid #528abf;padding:8px 18px;margin:16px 0;background:#eef5fc}
pre{overflow:auto;background:#f0f3f7;padding:16px;border-radius:8px;line-height:1.55}code{font:13px/1.55 ui-monospace,monospace}p code,li code,td code{background:#f0f3f7;padding:2px 4px}
.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px;border:1px solid #d6dee8;text-align:left;vertical-align:top}th{background:#eef3f9}
img{display:block;max-width:100%;max-height:540px;object-fit:contain;margin:18px auto}nav,footer{font-size:14px;color:#596a7c}nav{padding-bottom:16px;border-bottom:1px solid #e4e8ee}footer{margin-top:36px;border-top:1px solid #e4e8ee;padding-top:16px}
@media(max-width:640px){main{margin:0;padding:20px;border:0;border-radius:0}h1{font-size:25px}pre{font-size:12px}}
`

for (const file of documents) {
  const source = await readFile(path.join(root, file), 'utf8')
  const seen = new Map()
  const renderer = new marked.Renderer()
  renderer.heading = function ({ tokens, depth }) {
    const content = this.parser.parseInline(tokens)
    const base = slug(tokens.map(token => token.raw).join(''))
    const count = seen.get(base) ?? 0
    seen.set(base, count + 1)
    return `<h${depth} id="${escape(base + (count ? '-' + count : ''))}">${content}</h${depth}>\n`
  }
  let body = marked.parse(source, { renderer, gfm: true })
  body = body.replace(/href="([^"#]+)(#[^"]*)?"/g, (whole, target, fragment = '') => {
    if (/^[a-z]+:/i.test(target) || target.startsWith('/')) return whole
    const normalized = path.posix.normalize(path.posix.join(path.posix.dirname(file), target))
    const output = outputs.get(normalized)
    if (!output) return whole
    const relative = path.posix.relative(path.posix.dirname(htmlPath(file)), output)
    return `href="${escape(relative)}${fragment}"`
  }).replace(/<table>/g, '<div class="table-wrap"><table>').replace(/<\/table>/g, '</table></div>')
  const home = path.posix.relative(path.posix.dirname(htmlPath(file)), 'index.html') || 'index.html'
  const markdown = path.posix.basename(file)
  const title = source.split('\n').find(line => line.startsWith('# ')).slice(2)
  const html = `<!DOCTYPE html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${escape(title)}</title><style>${css}</style></head><body><main><nav><a href="${home}">指南首页</a> · <a href="${markdown}">Markdown 源文档</a></nav>${body}<footer>由 Markdown 自动生成。PDF 保持历史版本，接线与固件以本页面为准。自制路线尚需实物验收。</footer></main></body></html>\n`
  await writeFile(path.join(root, htmlPath(file)), html)
  console.log(htmlPath(file))
}
