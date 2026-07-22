import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    // Non-Next.js parts of this repo (Python CLI/content workflow, IaC,
    // generated tooling output) that live alongside the site at the
    // project root and shouldn't be linted as JS/TS.
    ".venv/**",
    ".pycache/**",
    ".pytest_cache/**",
    "app/**",
    "content/**",
    "scripts/**",
    "shelly/**",
    "templates/**",
    "prompts/**",
    "tests/**",
    "terraform/**",
    "wycliffepeart_profile.egg-info/**",
  ]),
]);

export default eslintConfig;
