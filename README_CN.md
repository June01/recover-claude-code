# recover-claude-code

本仓库包含从 **`@anthropic-ai/claude-code` v2.1.88** npm 包中提取的完整 TypeScript 源码（见 [`src/`](./src)），以及用于独立复现提取过程的脚本。

> **想直接读代码？** 浏览 [`src/`](./src) 目录即可。
> **想自己验证来源？** 按下方步骤从 npm 独立提取，与本仓库逐字节比对。

**唯一可信的一手来源是 npm 包本身**，其他 GitHub 镜像都是二手。

---

## 信任链

```
npm registry (官方)
  └── @anthropic-ai/claude-code@2.1.88
        └── cli.js.map (59.8MB，一手来源)
              └── 各路 GitHub 镜像 (二手，可能被篡改)
```

---

## 自己提取才是最可靠的

源头是 npm 官方发布包，从 tarball 里直接解压就能拿到原始 `.map` 文件：

```bash
# 下载官方包
npm pack @anthropic-ai/claude-code@2.1.88

# 解压
tar -xzf anthropic-ai-claude-code-2.1.88.tgz
cd package

# cli.js.map 就在里面，然后用 recover.py 提取源码
python3 ../recover.py --mapfile cli.js.map --only-anthropic
```

还原结果与本仓库 `src/` 内容完全一致。

---

## 各 GitHub 镜像的可信度

| 仓库 | 情况 |
|------|------|
| `nirholas/claude-code` | 声称是未修改的原始泄露备份，保存在 backup 分支 |
| `chatgptprojects/claude-code` | 注明是从 npm tarball 解包提取，提供了复现命令 |
| `sanbuphy/claude-code-source-code` | 有详细分析报告，中英双语，但侧重分析而非保真存档 |
| `Kuberwastaken/claude-code` | 主要是解读文章，不是原始源码 |

以上镜像的共同问题：信任链断裂，git 历史可被改写，随时可能被 DMCA 下架。

---

## 值得注意的背景

这其实不是第一次——2025 年 2 月 Claude Code 首发当天就带了 source map，Anthropic 两小时内删包修复，但已经有人提取并发到了 GitHub（`dnakov/claude-code`）。这次是时隔 13 个月后的重犯。

所以如果你想要真实可靠的版本：**直接从 npm 拿 2.1.88 的 tarball**，自己解包验证，任何镜像都不如原包可信。

---

## 为什么 npm 是唯一可信的一手来源

| 属性 | npm registry | GitHub 镜像 |
|---|---|---|
| 发布方 | Anthropic 本人（经过 npm 账号认证） | 不知名第三方 |
| 信任链 | 完整：Anthropic → registry → 你 | 断裂：Anthropic → registry → 镜像作者 → 你 |
| 完整性校验 | sha512 哈希固化在 registry 元数据中 | 无法验证，git 历史可被改写 |
| 可用性 | registry CDN 全球缓存，永久可达 | 随时可能被 DMCA 下架 |

用 registry 自己的元数据验证 tarball 完整性：

```bash
# 从 registry 获取官方 sha512
curl -s https://registry.npmjs.org/@anthropic-ai/claude-code/2.1.88 \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['dist']['integrity'])"

# 计算本地文件的 sha512
openssl dgst -sha512 -binary anthropic-ai-claude-code-2.1.88.tgz \
  | openssl base64 -A \
  | sed 's/^/sha512-/'
```

两串哈希完全一致，说明你拿到的文件与 Anthropic 发布时**逐字节相同**。没有任何 GitHub 镜像能提供这种保证。

---

## 源码为什么会在 npm 包里

Claude Code 是一个用 **esbuild** 打包的 Node.js CLI 工具。esbuild 支持在构建产物旁边生成 *source map*：

```
package/
├── cli.js          ← 压缩后的最终产物（真正的 CLI）
└── cli.js.map      ← source map  ← 不应该出现在这里
```

Source map 遵循 [Source Map v3 规范](https://sourcemaps.info/spec.html)，其中有两个关键字段：

- **`sources`** — 原始文件路径列表（如 `../src/utils/log.ts`）
- **`sourcesContent`** — **每个源文件的完整文本**，逐字嵌入

**2.1.88 版本同时犯了两个错误：**

1. `cli.js.map` 被包含在了 tarball 的 `package/` 目录中
2. `sourcesContent` 字段没有被清空

结果：一个 57 MB 的 JSON 文件里藏着整个 CLI 的完整 TypeScript 源码——**4756 个源文件，其中 1906 个是 Anthropic 自己写的代码**。

本脚本所做的全部工作，就是读取这个 JSON，把 `sourcesContent[i]` 写到 `sources[i]` 对应的路径。

---

## 为什么 2.1.88 至今仍可下载

npm 的 **unpublish 策略**（2020 年起生效）规定：一个版本发布超过 **72 小时**后，作者无法单方面将其撤销，除非该包零依赖且作者主动联系 npm Support 申请删除。

`@anthropic-ai/claude-code` 拥有大量用户，72 小时窗口期早已关闭，版本无法被撤回。即便 registry 端删除了某个版本，Cloudflare、Fastly 等 CDN 节点以及全球各地的私有 registry 镜像往往已经缓存了该 tarball。

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

---

## 脚本参数

```
用法: recover.py [-h] [--tarball PATH] [--mapfile PATH] [--outdir DIR] [--only-anthropic]

  --tarball PATH      npm tarball 路径（默认：claude-code-2.1.88.tgz）
  --mapfile PATH      直接指定已解压的 cli.js.map，跳过 tarball 解析
  --outdir DIR        输出目录（默认：recovered/）
  --only-anthropic    只还原 src/ 下的文件，跳过 node_modules
```

Python 3.6+，仅使用标准库，无需安装任何第三方包。

---

## 法律说明

本仓库的 `src/` 目录包含从 Anthropic 公开发布的 npm tarball 中提取的源码。该 tarball 由 Anthropic 官方账号发布至公开 npm registry，任何人均可下载，未设访问限制。从 source map 的 `sourcesContent` 字段中读取源码，是数百万开发者每天都在使用的标准工具链操作，并非破解或逆向工程。本仓库的目的是记录这一公开可及的事实，并提供可独立复现的验证方法。
