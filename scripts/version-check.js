#!/usr/bin/env node

/**
 * Validates that package.json versions match their corresponding
 * plugin.json and marketplace.json entries.
 */

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
let errors = 0;

function readJSON(filePath) {
  return JSON.parse(fs.readFileSync(path.join(root, filePath), "utf8"));
}

function check(label, expected, actual, source) {
  if (expected !== actual) {
    console.error(
      `MISMATCH ${label}: package.json=${expected}, ${source}=${actual}`
    );
    errors++;
  }
}

// Plugin checks
const pluginMarketplace = readJSON(".claude-plugin/marketplace.json");
for (const plugin of pluginMarketplace.plugins) {
  const pkgPath = `${plugin.source}/package.json`;
  const pluginJsonPath = `${plugin.source}/.claude-plugin/plugin.json`;

  if (!fs.existsSync(path.join(root, pkgPath))) {
    console.warn(`WARNING: ${pkgPath} not found for plugin "${plugin.name}", skipping`);
    continue;
  }

  const pkg = readJSON(pkgPath);
  const pluginJson = readJSON(pluginJsonPath);

  check(plugin.name, pkg.version, pluginJson.version, "plugin.json");

  if (plugin.version !== "latest") {
    check(plugin.name, pkg.version, plugin.version, "marketplace.json");
  }
}

// Workflow checks
const workflowMarketplace = readJSON(".athena-workflow/marketplace.json");
for (const workflow of workflowMarketplace.workflows) {
  const workflowDir = path.dirname(workflow.source);
  const pkgPath = `${workflowDir}/package.json`;

  if (!fs.existsSync(path.join(root, pkgPath))) {
    console.warn(`WARNING: ${pkgPath} not found for workflow "${workflow.name}", skipping`);
    continue;
  }

  const pkg = readJSON(pkgPath);

  if (workflow.version && workflow.version !== "latest") {
    check(workflow.name, pkg.version, workflow.version, "marketplace.json");
  }
}

if (errors > 0) {
  console.error(`\n${errors} version mismatch(es) found.`);
  process.exit(1);
} else {
  console.log("All versions in sync.");
}
