import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(path.join(root, "respect-frontend/package.json"));
const { chromium, request } = require("@playwright/test");
const values = Object.fromEntries(fs.readFileSync(path.join(root, "Docker/.env"), "utf8").split(/\r?\n/).filter(line => line.includes("=") && !line.trimStart().startsWith("#")).map(line => { const index = line.indexOf("="); return [line.slice(0, index), line.slice(index + 1)]; }));
const api = await request.newContext({ baseURL: "http://127.0.0.1:3000" });
let browser;
try {
  const login = await api.post("/api/auth/login", { data: { identifier: values.BOOTSTRAP_ADMIN_USERNAME, password: values.BOOTSTRAP_ADMIN_PASSWORD } });
  if (!login.ok()) throw new Error(`Administrator login failed: HTTP ${login.status()}`);
  const summary = await (await api.get("/api/admin/summary")).json();
  if (summary.admins !== 1 || summary.players !== 0 || summary.teams !== 0 || summary.sponsors !== 0 || summary.pending_cases !== 0) throw new Error("The installation is not in the requested clean state");
  for (const route of ["/api/posts", "/api/tournaments", "/api/users", "/api/admin/cases?status=history"]) {
    const rows = await (await api.get(route)).json();
    if (!Array.isArray(rows) || rows.length) throw new Error(`Unexpected remaining application data on ${route}`);
  }
  const health = await (await api.get("/api/health")).json();
  if (health.database !== "mongodb") throw new Error("Expected MongoDB persistence");
  browser = await chromium.launch({ channel: process.platform === "win32" ? "chrome" : undefined, headless: true });
  const context = await browser.newContext({ storageState: await api.storageState(), viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const pageErrors = [];
  page.on("pageerror", error => pageErrors.push(error.message));
  await page.goto("http://127.0.0.1:3000/admin");
  await page.getByRole("heading", { name: "Perfiles con más de 5 reportes", exact: true }).waitFor();
  await page.getByText("No hay casos en esta bandeja.", { exact: true }).waitFor();
  await page.screenshot({ path: path.join(root, "tmp/qa/admin-clean.png"), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1)) throw new Error("Administrative page overflows on mobile");
  if (pageErrors.length) throw new Error("Browser runtime error");
  console.log(JSON.stringify({ database: health.database, admins: summary.admins, players: summary.players, teams: summary.teams, sponsors: summary.sponsors, pending_cases: summary.pending_cases, browser: "desktop and mobile OK" }));
} finally {
  await api.post("/api/auth/logout");
  await api.dispose();
  if (browser) await browser.close();
}
