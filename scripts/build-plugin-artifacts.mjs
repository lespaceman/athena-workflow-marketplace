#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

function findRepoRoot(startDir) {
  let current = path.resolve(startDir);
  for (;;) {
    const manifest = path.join(current, '.agents', 'plugins', 'marketplace.json');
    if (fs.existsSync(manifest)) return current;
    const parent = path.dirname(current);
    if (parent === current) {
      throw new Error('Could not locate repo root from plugin directory');
    }
    current = parent;
  }
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function ensureCleanDir(dir) {
  fs.rmSync(dir, {recursive: true, force: true});
  fs.mkdirSync(dir, {recursive: true});
}

function copyPluginTree(sourceDir, targetDir, excludedTopLevelName) {
  ensureCleanDir(targetDir);
  for (const entry of fs.readdirSync(sourceDir, {withFileTypes: true})) {
    if (entry.name === 'dist' || entry.name === excludedTopLevelName) {
      continue;
    }
    const sourcePath = path.join(sourceDir, entry.name);
    const targetPath = path.join(targetDir, entry.name);
    fs.cpSync(sourcePath, targetPath, {recursive: true});
  }
}

function buildReleaseJson({pluginName, marketplaceName, version}) {
  return {
    schemaVersion: 1,
    pluginRef: `${pluginName}@${marketplaceName}`,
    pluginName,
    marketplaceName,
    version,
    artifacts: {
      claude: {
        type: 'directory',
        path: './claude/plugin',
      },
      codex: {
        type: 'marketplace',
        marketplacePath: './codex/marketplace.json',
        pluginPath: './codex/plugin',
      },
    },
  };
}

function buildCodexMarketplaceJson({pluginName, marketplaceName, version}) {
  return {
    schemaVersion: 1,
    name: marketplaceName,
    plugins: [
      {
        name: pluginName,
        version,
        source: {
          source: 'local',
          path: './plugin',
        },
      },
    ],
  };
}

function main() {
  const pluginArg = process.argv[2] ?? '.';
  const pluginDir = path.resolve(pluginArg);
  const repoRoot = findRepoRoot(pluginDir);
  const pluginName = path.basename(pluginDir);

  const claudeManifestPath = path.join(pluginDir, '.claude-plugin', 'plugin.json');
  const codexManifestPath = path.join(pluginDir, '.codex-plugin', 'plugin.json');
  const marketplaceManifestPath = path.join(repoRoot, '.agents', 'plugins', 'marketplace.json');

  if (!fs.existsSync(claudeManifestPath)) {
    throw new Error(`Missing Claude plugin manifest: ${claudeManifestPath}`);
  }
  if (!fs.existsSync(codexManifestPath)) {
    throw new Error(`Missing Codex plugin manifest: ${codexManifestPath}`);
  }

  const claudeManifest = readJson(claudeManifestPath);
  const codexManifest = readJson(codexManifestPath);
  const marketplaceManifest = readJson(marketplaceManifestPath);
  const marketplaceName = marketplaceManifest.name;
  const version = codexManifest.version ?? claudeManifest.version;

  if (typeof marketplaceName !== 'string' || marketplaceName.length === 0) {
    throw new Error('Marketplace manifest is missing a valid name');
  }
  if (typeof version !== 'string' || version.length === 0) {
    throw new Error(`Plugin ${pluginName} is missing a valid version`);
  }

  const versionRoot = path.join(pluginDir, 'dist', version);
  const claudeTarget = path.join(versionRoot, 'claude', 'plugin');
  const codexTarget = path.join(versionRoot, 'codex', 'plugin');
  ensureCleanDir(versionRoot);
  copyPluginTree(pluginDir, claudeTarget, '.codex-plugin');
  copyPluginTree(pluginDir, codexTarget, '.claude-plugin');

  fs.writeFileSync(
    path.join(versionRoot, 'release.json'),
    JSON.stringify(buildReleaseJson({pluginName, marketplaceName, version}), null, 2) + '\n',
  );
  fs.mkdirSync(path.join(versionRoot, 'codex'), {recursive: true});
  fs.writeFileSync(
    path.join(versionRoot, 'codex', 'marketplace.json'),
    JSON.stringify(buildCodexMarketplaceJson({pluginName, marketplaceName, version}), null, 2) + '\n',
  );

  console.log(`Built runtime artifacts for ${pluginName}@${version} in ${path.relative(repoRoot, versionRoot)}`);
}

main();
