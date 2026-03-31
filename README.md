# recover-claude-code

This repository contains the full TypeScript source of **`@anthropic-ai/claude-code` v2.1.88**, extracted directly from Anthropic's own npm package (see [`src/`](./src)), along with the script used to reproduce the extraction.

> **Just want to read the code?** Browse [`src/`](./src) directly.
> **Want to verify the source yourself?** Follow the steps below to extract independently from npm and compare byte-for-byte.

---

## Reproduce the extraction

```bash
# 1. Download the npm tarball directly from the registry
curl -L https://registry.npmjs.org/@anthropic-ai/claude-code/-/claude-code-2.1.88.tgz \
     -o claude-code-2.1.88.tgz

# 2. Restore all source files
python3 recover.py

# 3. Or restore only Anthropic's own TypeScript (src/) — skips node_modules
python3 recover.py --only-anthropic
```

Recovered files appear in `recovered/` and will be identical to `src/` in this repo.

---

## Why npm is the only trustworthy first-hand source

When a story breaks about a "leaked" codebase, GitHub mirrors appear within hours.
Those mirrors are **second-hand**: someone else extracted the files, committed them, and you're trusting that person didn't modify anything.

The **npm registry** is different:

| Property | npm registry | GitHub mirror |
|---|---|---|
| Publisher | Anthropic themselves (authenticated push) | Unknown third party |
| Chain of custody | Unbroken: Anthropic → registry → you | Broken: Anthropic → registry → mirror author → you |
| Integrity check | `npm pack` / sha512 in `package-lock.json` | None (git history is mutable) |
| Availability | Registry CDN, globally cached | Repo may be taken down at any time |
| Verifiability | Compare checksum against registry metadata | Cannot verify |

The tarball URL is deterministic and permanent:

```
https://registry.npmjs.org/@anthropic-ai/claude-code/-/claude-code-{VERSION}.tgz
```

You can verify the download against the registry's own integrity hash:

```bash
# Fetch the published shasum from the registry manifest
curl -s https://registry.npmjs.org/@anthropic-ai/claude-code/2.1.88 \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['dist']['integrity'])"

# Compare against your local file
openssl dgst -sha512 -binary claude-code-2.1.88.tgz | openssl base64 -A | sed 's/^/sha512-/'
```

If those two strings match, your copy is byte-for-byte identical to what Anthropic published.
No GitHub mirror can offer this guarantee.

---

## How the source code ended up inside the tarball

Claude Code is a Node.js CLI bundled with **esbuild**.
esbuild can emit a *source map* alongside the compiled bundle:

```
package/
├── cli.js          ← minified bundle (the actual CLI)
└── cli.js.map      ← source map  ← should NOT have been here
```

A source map (spec: [Source Map v3](https://sourcemaps.info/spec.html)) contains two key arrays:

- **`sources`** — original file paths (e.g. `../src/utils/log.ts`)
- **`sourcesContent`** — the **full text of every source file**, embedded verbatim

This feature exists so that browser / Node devtools can show you readable stack traces from minified code.  In production npm packages it is almost always disabled or the `.map` file is excluded from the published bundle.

Version **2.1.88** shipped with both:

1. `cli.js.map` included in the `package/` directory inside the tarball, **and**
2. `sourcesContent` populated (not stripped).

The result: a single 57 MB JSON file that contains the complete original TypeScript source of every module compiled into the CLI — **4 756 source files, 1 906 of which are Anthropic's own code**.

This script simply reads that JSON and writes each `sourcesContent[i]` to `sources[i]`.

---

## Why version 2.1.88 is still downloadable

npm's **unpublish policy** (effective since 2020) prevents authors from removing a version once it has been available for **more than 72 hours**, unless:

- The version was published less than 72 hours ago, **or**
- The package has zero dependents and the author contacts npm Support.

`@anthropic-ai/claude-code` has a large number of dependents (anyone who has run `npm install -g @anthropic-ai/claude-code`), so the 72-hour window has long since closed and the version cannot be unpublished unilaterally.

Additionally, even if a package is unpublished from the registry, popular CDNs and mirrors (Cloudflare R2, Fastly, regional caches) often retain the tarball.  The sha512 integrity hash embedded in every `package-lock.json` that ever referenced this version means the content is permanently pinned.

Reference: [npm unpublish policy](https://docs.npmjs.com/policies/unpublish)

---

## Repository structure

```
recover-claude-code/
├── recover.py         ← extraction script
├── README.md
├── README_CN.md
└── src/               ← Anthropic's own TypeScript source (1,902 files)
    ├── utils/
    ├── services/
    ├── bootstrap/
    ├── tools/
    ├── commands/
    ├── ink/           ← terminal UI components (React/Ink)
    └── ...
```

`src/` was extracted directly from the npm source map without modification.
Run `python3 recover.py --only-anthropic` to reproduce the extraction independently and verify it matches.

---

## Script options

```
usage: recover.py [-h] [--tarball PATH] [--mapfile PATH] [--outdir DIR] [--only-anthropic]

  --tarball PATH      Path to the npm tarball (default: claude-code-2.1.88.tgz)
  --mapfile PATH      Use an already-extracted cli.js.map instead of the tarball
  --outdir DIR        Output directory (default: recovered/)
  --only-anthropic    Only restore src/ files (skip node_modules)
```

---

## Requirements

Python 3.6+, standard library only — no third-party packages needed.

---

## Legal

The `src/` directory contains source code extracted from a tarball published by Anthropic to the public npm registry with no access restrictions.
Reading `sourcesContent` from a source map is standard browser/Node tooling used daily by millions of developers — it is not decompilation or reverse engineering.
This repository exists to document a publicly accessible fact and to provide a reproducible, verifiable method for anyone to confirm the source independently.
