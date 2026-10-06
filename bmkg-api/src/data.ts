import { readFileSync, existsSync } from "fs";
import { fileURLToPath } from "url";
import path from "path";
import type { Level, Region } from "./types";

const BASE_CSV_URL = new URL("../base.csv", import.meta.url);
export const BASE_CSV_PATH = fileURLToPath(BASE_CSV_URL);
const BASE_JSON_URL = new URL("../base.json", import.meta.url);
export const BASE_JSON_PATH = fileURLToPath(BASE_JSON_URL);

export function detectLevel(code: string): Level {
    const segments = code.split(".");
    switch (segments.length) {
        case 1:
            return "provinsi";
        case 2:
            return "kotkab";
        case 3:
            return "kecamatan";
        case 4:
            return "desa";
        default:
            return "unknown";
    }
}

function parseCsv(raw: string): Region[] {
    return raw
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean)
        .map((line) => {
            const [code, ...rest] = line.split(",");
            const name = rest.join(",").trim();
            const cleanCode = code.trim();
            return { code: cleanCode, name, level: detectLevel(cleanCode) };
        });
}

export function loadRegions(filePath?: string): Region[] {
    // Prefer JSON if available (faster parse for repeated use), fallback to CSV.
    const candidates = filePath ? [filePath] : [BASE_JSON_PATH, BASE_CSV_PATH];
    for (const candidate of candidates) {
        const resolved = path.isAbsolute(candidate)
            ? candidate
            : path.join(process.cwd(), candidate);
        if (!existsSync(resolved)) continue;
        const raw = readFileSync(resolved, "utf8");
        if (resolved.endsWith(".json")) {
            const parsed = JSON.parse(raw) as Region[];
            return parsed.map((r) => ({
                ...r,
                level: r.level ?? detectLevel(r.code),
            }));
        }
        return parseCsv(raw);
    }
    // If nothing found, throw to signal missing data.
    throw new Error("Data wilayah (base.csv/json) tidak ditemukan.");
}
