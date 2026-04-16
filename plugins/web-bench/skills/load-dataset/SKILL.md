---
name: load-dataset
description: >
  Download and prepare the Halluminate/WebBench dataset from HuggingFace for benchmarking. Triggers: "load dataset", "download WebBench", "prepare benchmark data", "fetch tasks". Downloads the CSV dataset via curl, converts to JSONL with Node.js, applies optional filters (category, sample size, website allowlist/blocklist), and writes web-bench-tasks.jsonl to the working directory. Zero Python dependencies — uses only curl and Node.js. Does NOT execute tasks — use execute-task for that.
allowed-tools: Bash Read Write Edit Glob
---

# Load WebBench Dataset

Download the Halluminate/WebBench dataset from HuggingFace and prepare it for benchmark execution.

## Dataset Source

- **HuggingFace:** `Halluminate/WebBench`
- **Source file:** `webbenchfinal.csv` (CSV format)
- **Size:** ~2,454 tasks across 452 websites
- **Fields per row:** `ID` (int), `Starting_URL` (string), `Category` (enum), `Task` (string)

## Pre-check: Skip Download if Dataset Exists

Before downloading, check if `web-bench-tasks.jsonl` already exists in the working directory:

```bash
if [ -f web-bench-tasks.jsonl ]; then
  echo "Dataset already exists: $(wc -l < web-bench-tasks.jsonl) tasks"
  head -1 web-bench-tasks.jsonl
fi
```

**If `web-bench-tasks.jsonl` exists and is non-empty, skip the download and conversion entirely.** Jump straight to [Applying Filters](#applying-filters) if filters need to be applied, or reuse the existing dataset.

Only proceed with download if the file does not exist or is empty.

## Download Method

Download the CSV directly with `curl`, then convert to JSONL with Node.js. No Python dependencies required.

### Step 1: Download the CSV

```bash
curl -fSL -o web-bench-dataset.csv \
  "https://huggingface.co/datasets/Halluminate/WebBench/resolve/main/webbenchfinal.csv"
```

If the above URL fails (HuggingFace sometimes changes paths), try:

```bash
curl -fSL -o web-bench-dataset.csv \
  "https://huggingface.co/datasets/Halluminate/WebBench/raw/main/webbenchfinal.csv"
```

### Step 2: Convert CSV to JSONL

```bash
node -e "
const fs = require('fs');
const csv = fs.readFileSync('web-bench-dataset.csv', 'utf-8');
const lines = csv.split('\n');
const header = lines[0].split(',').map(h => h.trim().replace(/^\"|\"$/g, ''));

// Find column indices
const idIdx = header.findIndex(h => h === 'ID');
const urlIdx = header.findIndex(h => h === 'Starting_URL');
const catIdx = header.findIndex(h => h === 'Category');
const taskIdx = header.findIndex(h => h === 'Task');

const out = fs.createWriteStream('web-bench-tasks.jsonl');
let count = 0;

for (let i = 1; i < lines.length; i++) {
  const line = lines[i].trim();
  if (!line) continue;

  // Parse CSV line respecting quoted fields
  const fields = [];
  let field = '';
  let inQuotes = false;
  for (let j = 0; j < line.length; j++) {
    const ch = line[j];
    if (ch === '\"') {
      inQuotes = !inQuotes;
    } else if (ch === ',' && !inQuotes) {
      fields.push(field.trim());
      field = '';
    } else {
      field += ch;
    }
  }
  fields.push(field.trim());

  if (fields.length > taskIdx) {
    out.write(JSON.stringify({
      id: parseInt(fields[idIdx], 10),
      url: fields[urlIdx],
      category: fields[catIdx],
      task: fields[taskIdx]
    }) + '\n');
    count++;
  }
}

out.end();
console.log('Wrote ' + count + ' tasks to web-bench-tasks.jsonl');
"
```

### Step 3: Verify the output

```bash
wc -l web-bench-tasks.jsonl
head -1 web-bench-tasks.jsonl
node -e "
const fs = require('fs');
const tasks = fs.readFileSync('web-bench-tasks.jsonl','utf-8').trim().split('\n').map(JSON.parse);
const cats = {};
const sites = new Set();
for (const t of tasks) {
  cats[t.category] = (cats[t.category] || 0) + 1;
  sites.add(t.url);
}
for (const [c, n] of Object.entries(cats).sort()) console.log('  ' + c + ': ' + n);
console.log('Total: ' + tasks.length + ' tasks across ' + sites.size + ' websites');
"
```

## Applying Filters

After downloading, apply filters based on the requested benchmark configuration. All filters use Node.js.

### Category Filter

If the requested configuration specifies a category filter (e.g., `READ`, `CREATE`):

```bash
node -e "
const fs = require('fs');
const category = process.argv[1];
const tasks = fs.readFileSync('web-bench-tasks.jsonl','utf-8').trim().split('\n').map(JSON.parse);
const filtered = tasks.filter(t => t.category === category);
fs.writeFileSync('web-bench-tasks.jsonl', filtered.map(JSON.stringify).join('\n') + '\n');
console.log('Filtered to ' + filtered.length + ' ' + category + ' tasks');
" "READ"
```

### Sample Size

If the requested configuration specifies a sample size (e.g., `--sample 50`):

```bash
node -e "
const fs = require('fs');
const n = parseInt(process.argv[1], 10);
const tasks = fs.readFileSync('web-bench-tasks.jsonl','utf-8').trim().split('\n').map(JSON.parse);

// Deterministic shuffle (seed-based) for reproducibility
function seededShuffle(arr, seed) {
  const a = [...arr];
  let s = seed;
  for (let i = a.length - 1; i > 0; i--) {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    const j = ((s >>> 0) % (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const sample = seededShuffle(tasks, 42).slice(0, Math.min(n, tasks.length));
fs.writeFileSync('web-bench-tasks.jsonl', sample.map(JSON.stringify).join('\n') + '\n');
console.log('Sampled ' + sample.length + ' tasks');
" "50"
```

### Website Blocklist

```bash
node -e "
const fs = require('fs');
const blocklist = new Set(process.argv[1] ? process.argv[1].split(',') : []);
const tasks = fs.readFileSync('web-bench-tasks.jsonl','utf-8').trim().split('\n').map(JSON.parse);
const filtered = tasks.filter(t => !blocklist.has(t.url));
fs.writeFileSync('web-bench-tasks.jsonl', filtered.map(JSON.stringify).join('\n') + '\n');
console.log(filtered.length + ' tasks after blocklist filter');
" ""
```

## Output

- **File:** `web-bench-tasks.jsonl` in working directory
- **Intermediate file:** `web-bench-dataset.csv` (can be deleted after conversion)
- **Format:** One JSON object per line
- **Schema:**
  ```json
  {"id": 42, "url": "https://acehardware.com", "category": "READ", "task": "Navigate to..."}
  ```

## Cleanup

After successful conversion, remove the intermediate CSV:

```bash
rm -f web-bench-dataset.csv
```

Report the total count and category breakdown in your result.
