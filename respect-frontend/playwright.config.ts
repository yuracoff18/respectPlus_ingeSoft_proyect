import { defineConfig } from "@playwright/test";

// Start the API and frontend first; E2E_BASE_URL can select an isolated instance.
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  workers: 1,
  timeout: 45000,
  expect: { timeout: 10000 },
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://127.0.0.1:3000",
    channel: process.platform === "win32" ? "chrome" : undefined,
    headless: true,
    viewport: { width: 1440, height: 1000 },
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
});
