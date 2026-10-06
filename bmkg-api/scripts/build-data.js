import { readFileSync, writeFileSync } from "fs";
import path from "path";

const CSV_PATH = path.join(process.cwd(), "base.csv");
const JSON_PATH = path.join(process.cwd(), "base.json");

function detectLevel(code) {
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

function parseCsv(raw) {
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

const raw = readFileSync(CSV_PATH, "utf8");
const regions = parseCsv(raw);
writeFileSync(JSON_PATH, JSON.stringify(regions));
console.log(`Generated base.json with ${regions.length} entries.`);
