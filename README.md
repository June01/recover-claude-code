# recover-claude-code

This repository contains the full TypeScript source of **`@anthropic-ai/claude-code` v2.1.88**, extracted directly from Anthropic's own npm package (see [`src/`](./src)), along with the script used to reproduce the extraction.

> **Just want to read the code?** Browse [`src/`](./src) directly.
> **Want to verify the source yourself?** Follow the steps below to extract independently from npm and compare byte-for-byte.

**The only trustworthy first-hand source is the npm package itself.** Every GitHub mirror is second-hand.

---

## Trust chain

```
npm registry (official)
  └── @anthropic-ai/claude-code@2.1.88
        └── cli.js.map (59.8 MB, first-hand source)
              └── GitHub mirrors (second-hand, potentially modified)
```

---

## Extracting it yourself is the most reliable approach

The source originates from the official npm package. Unpacking the tarball gives you the raw `.map` file directly:

```bash
# Download the official package
npm pack @anthropic-ai/claude-code@2.1.88

# Unpack
tar -xzf anthropic-ai-claude-code-2.1.88.tgz
cd package

# cli.js.map is right there — extract source with recover.py
python3 ../recover.py --mapfile cli.js.map --only-anthropic
```

The recovered files will be identical to `src/` in this repo.

---

## Trustworthiness of known GitHub mirrors

| Repository | Notes |
|------|------|
| `nirholas/claude-code` | Claims to be an unmodified backup of the original leak, stored in a `backup` branch |
| `chatgptprojects/claude-code` | States it was unpacked from the npm tarball and provides a reproduction command |
| `sanbuphy/claude-code-source-code` | Detailed analysis report, bilingual, but focused on analysis rather than archival fidelity |
| `Kuberwastaken/claude-code` | Primarily an explainer article, not the raw source |

The shared problem with all mirrors: broken chain of custody, mutable git history, and they can be taken down via DMCA at any time.

---

## Background worth knowing

This is not the first time. In February 2025, on the day Claude Code first launched, it shipped with a source map. Anthropic pulled the package within two hours, but someone had already extracted and published the source to GitHub (`dnakov/claude-code`). Version 2.1.88 is a repeat of the same mistake, 13 months later.

If you want the authentic, verifiable version: **get the 2.1.88 tarball directly from npm**, unpack it yourself, and verify. No mirror is more trustworthy than the original package.

---

## Why npm is the only trustworthy first-hand source

| Property | npm registry | GitHub mirror |
|---|---|---|
| Publisher | Anthropic themselves (authenticated push) | Unknown third party |
| Chain of custody | Unbroken: Anthropic → registry → you | Broken: Anthropic → registry → mirror author → you |
| Integrity check | sha512 fixed in registry metadata | None — git history is mutable |
| Availability | Registry CDN, globally cached | Can be taken down at any time |
| Verifiability | Compare checksum against registry metadata | Cannot verify |

Verify the tarball against the registry's own integrity hash:

```bash
# Fetch the published sha512 from the registry manifest
curl -s https://registry.npmjs.org/@anthropic-ai/claude-code/2.1.88 \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['dist']['integrity'])"

# Compute the sha512 of your local file
openssl dgst -sha512 -binary anthropic-ai-claude-code-2.1.88.tgz \
  | openssl base64 -A \
  | sed 's/^/sha512-/'
```

If those two strings match, your copy is byte-for-byte identical to what Anthropic published. No GitHub mirror can offer this guarantee.

---

## How the source code ended up inside the tarball

Claude Code is a Node.js CLI bundled with **esbuild**. esbuild can emit a *source map* alongside the compiled bundle:

```
package/
├── cli.js          ← minified bundle (the actual CLI)
└── cli.js.map      ← source map  ← should NOT have been here
```

A source map ([Source Map v3 spec](https://sourcemaps.info/spec.html)) contains two key arrays:

- **`sources`** — original file paths (e.g. `../src/utils/log.ts`)
- **`sourcesContent`** — the **full text of every source file**, embedded verbatim

**Version 2.1.88 made two mistakes simultaneously:**

1. `cli.js.map` was included in the `package/` directory inside the tarball
2. `sourcesContent` was not stripped

The result: a single 57 MB JSON file containing the complete original TypeScript source of every module compiled into the CLI — **4,756 source files, 1,906 of which are Anthropic's own code**.

This script simply reads that JSON and writes each `sourcesContent[i]` to `sources[i]`.

---

## Why version 2.1.88 is still downloadable

npm's **unpublish policy** (effective since 2020) prevents authors from removing a version once it has been available for more than **72 hours**, unless the package has zero dependents and the author contacts npm Support.

`@anthropic-ai/claude-code` has a large number of dependents, so the 72-hour window has long since closed. Even if the registry entry were removed, CDN nodes (Cloudflare, Fastly) and private registry mirrors worldwide have already cached the tarball.

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

---

## Script options

```
usage: recover.py [-h] [--tarball PATH] [--mapfile PATH] [--outdir DIR] [--only-anthropic]

  --tarball PATH      Path to the npm tarball (default: claude-code-2.1.88.tgz)
  --mapfile PATH      Use an already-extracted cli.js.map instead of the tarball
  --outdir DIR        Output directory (default: recovered/)
  --only-anthropic    Only restore src/ files (skip node_modules)
```

Python 3.6+, standard library only — no third-party packages needed.

---

## Legal

The `src/` directory contains source code extracted from a tarball published by Anthropic to the public npm registry with no access restrictions. Reading `sourcesContent` from a source map is standard browser/Node tooling used daily by millions of developers — it is not decompilation or reverse engineering. This repository exists to document a publicly accessible fact and to provide a reproducible, verifiable method for anyone to confirm the source independently.
