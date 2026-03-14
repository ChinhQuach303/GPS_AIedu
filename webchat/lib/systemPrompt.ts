import { readFileSync } from "node:fs";
import { join } from "node:path";

let cachedPrompt: string | null = null;

export function getSystemPrompt(): string {
  if (cachedPrompt) return cachedPrompt;
  const promptPath = join(process.cwd(), "prompts", "system_prompt.md");
  cachedPrompt = readFileSync(promptPath, "utf-8");
  return cachedPrompt;
}

