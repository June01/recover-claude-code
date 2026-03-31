# recover-claude-code

本仓库包含从 **`@anthropic-ai/claude-code` v2.1.88** npm 包中提取的完整 TypeScript 源码（见 [`src/`](./src)），以及用于独立复现提取过程的脚本。

> **想直接读代码？** 浏览 [`src/`](./src) 目录即可。
> **想自己验证来源？** 按下方步骤从 npm 独立提取，与本仓库逐字节比对。

---

## 自行提取（可验证）

```bash
# 1. 直接从 npm registry 下载 tarball
curl -L https://registry.npmjs.org/@anthropic-ai/claude-code/-/claude-code-2.1.88.tgz \
     -o claude-code-2.1.88.tgz

# 2. 还原所有源文件
python3 recover.py

# 3. 只还原 Anthropic 自己的 TypeScript（跳过 node_modules）
python3 recover.py --only-anthropic
```

还原结果输出到 `recovered/` 目录，与本仓库 `src/` 内容完全一致。

---

## 为什么 npm 是唯一可信的一手来源

每当一个"源码泄漏"事件发酵，GitHub 上的镜像仓库往往在几小时内涌现。
这些镜像是**二手资料**：某个人从某处提取了文件、提交到 git，你信任的是那个人，而不是 Anthropic。

**npm registry 不同：**

| 属性 | npm registry | GitHub 镜像 |
|---|---|---|
| 发布方 | Anthropic 本人（经过 npm 账号认证） | 不知名第三方 |
| 信任链 | 完整：Anthropic → registry → 你 | 断裂：Anthropic → registry → 镜像作者 → 你 |
| 完整性校验 | sha512 哈希固化在 registry 元数据中 | 无法验证，git 历史可被改写 |
| 可用性 | registry CDN 全球缓存，永久可达 | 随时可能被 DMCA 下架 |

tarball 的下载 URL 是**确定性**的：

```
https://registry.npmjs.org/@anthropic-ai/claude-code/-/claude-code-{VERSION}.tgz
```

你可以用 registry 自己的元数据来验证下载内容的完整性：

```bash
# 从 registry 获取官方 sha512
curl -s https://registry.npmjs.org/@anthropic-ai/claude-code/2.1.88 \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['dist']['integrity'])"

# 计算本地文件的 sha512
openssl dgst -sha512 -binary claude-code-2.1.88.tgz \
  | openssl base64 -A \
  | sed 's/^/sha512-/'
```

两串哈希完全一致，说明你拿到的文件与 Anthropic 发布时**逐字节相同**。
没有任何 GitHub 镜像能提供这种保证。

---

## 源码为什么会在 npm 包里

Claude Code 是一个用 **esbuild** 打包的 Node.js CLI 工具。
esbuild 支持在构建产物旁边生成 *source map*：

```
package/
├── cli.js          ← 压缩后的最终产物（真正的 CLI）
└── cli.js.map      ← source map  ← 不应该出现在这里
```

Source map 遵循 [Source Map v3 规范](https://sourcemaps.info/spec.html)，其中有两个关键字段：

- **`sources`** — 原始文件路径列表（如 `../src/utils/log.ts`）
- **`sourcesContent`** — **每个源文件的完整文本**，逐字嵌入

这个功能本是为了让浏览器 / Node.js 的开发者工具在压缩代码中显示可读的调用栈。
生产环境的 npm 包通常会关闭这个选项，或通过 `.npmignore` / `files` 字段把 `.map` 文件排除在外。

**2.1.88 版本同时犯了两个错误：**

1. `cli.js.map` 被包含在了 tarball 的 `package/` 目录中
2. `sourcesContent` 字段没有被清空

结果：一个 57 MB 的 JSON 文件里藏着整个 CLI 的完整 TypeScript 源码——
**4756 个源文件，其中 1906 个是 Anthropic 自己写的代码**。

本脚本所做的全部工作，就是读取这个 JSON，把 `sourcesContent[i]` 写到 `sources[i]` 对应的路径。

---

## 为什么 2.1.88 至今仍可下载

npm 的 **unpublish 策略**（2020 年起生效）规定：一个版本发布超过 **72 小时**后，作者无法单方面将其撤销，除非：

- 该包**零依赖**（没有任何其他包依赖它），**且**
- 作者主动联系 npm Support 申请删除

`@anthropic-ai/claude-code` 拥有大量用户，72 小时窗口期早已关闭，版本无法被撤回。

此外，即便 registry 端删除了某个版本，Cloudflare、Fastly 等 CDN 节点以及全球各地的私有 registry 镜像（Verdaccio、Artifactory、GitHub Packages）往往已经缓存了该 tarball。
每一个曾经安装过这个版本的项目，其 `package-lock.json` 里都固化了 sha512 哈希，这意味着内容被永久"锁住"。

参考：[npm unpublish 政策](https://docs.npmjs.com/policies/unpublish)

---

## 仓库目录结构

```
recover-claude-code/
├── recover.py         ← 提取脚本
├── README.md
├── README_CN.md
└── src/               ← 已提取的 Anthropic TypeScript 源码（1902 个文件）
    ├── utils/
    ├── services/
    ├── bootstrap/
    ├── tools/
    ├── commands/
    ├── ink/           ← 终端 UI 组件（基于 React/Ink）
    └── ...
```

`src/` 直接从 npm tarball 的 source map 中提取，未经任何修改。
使用 `--only-anthropic` 参数自行运行脚本可独立验证内容一致性。

---

## 脚本参数

```
用法: recover.py [-h] [--tarball PATH] [--mapfile PATH] [--outdir DIR] [--only-anthropic]

  --tarball PATH      npm tarball 路径（默认：claude-code-2.1.88.tgz）
  --mapfile PATH      直接指定已解压的 cli.js.map，跳过 tarball 解析
  --outdir DIR        输出目录（默认：recovered/）
  --only-anthropic    只还原 src/ 下的文件，跳过 node_modules
```

---

## 依赖

Python 3.6+，仅使用标准库，无需安装任何第三方包。

---

## 法律说明

本仓库的 `src/` 目录包含从 Anthropic 公开发布的 npm tarball 中提取的源码。
该 tarball 由 Anthropic 官方账号发布至公开 npm registry，任何人均可下载，未设访问限制。
从 source map 的 `sourcesContent` 字段中读取源码，是数百万开发者每天都在使用的标准浏览器 / Node.js 工具链操作，并非破解或逆向工程。
本仓库的目的是记录这一公开可及的事实，并提供可独立复现的验证方法。
