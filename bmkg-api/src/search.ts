import type { Level, Region } from "./types";

const DEFAULT_LEVEL_BIAS: Record<Level, number> = {
    kotkab: 0,
    kecamatan: 1,
    provinsi: 1,
    desa: 2,
    unknown: 3,
};

export function searchRegions(
    regions: Region[],
    query: string,
    limit = 25,
    levelBias: Record<Level, number> = DEFAULT_LEVEL_BIAS,
): Region[] {
    const q = query.toLowerCase();
    const matches = regions.filter((r) => {
        const name = r.name.toLowerCase();
        return r.code.includes(query) || name.includes(q);
    });

    const priority =
        q.includes("malang") || query.includes("35.07") || query.includes("35.73")
            ? new Set(["35.07", "35.73"])
            : null;

    const scored = matches
        .map((r) => {
            const name = r.name.toLowerCase();
            let score = 3;
            if (name === q) score = 0;
            else if (name.startsWith(q)) score = 1;
            else if (name.includes(q)) score = 2;
            else if (r.code.includes(query)) score = 3;

            return {
                region: r,
                score: score * 10 + (levelBias[r.level] ?? 5),
            };
        })
        .sort((a, b) => {
            if (priority) {
                const aPriority = priority.has(a.region.code);
                const bPriority = priority.has(b.region.code);
                if (aPriority !== bPriority) return aPriority ? -1 : 1;
            }
            if (a.score !== b.score) return a.score - b.score;
            return a.region.name.localeCompare(b.region.name);
        });

    return scored.slice(0, limit).map((s) => s.region);
}

export function formatHierarchy(region: Region, index: Map<string, Region>): string {
    const parts = region.code.split(".");
    const parentCodes: string[] = [];
    if (parts.length >= 1) parentCodes.push(parts.slice(0, 1).join("."));
    if (parts.length >= 2) parentCodes.push(parts.slice(0, 2).join("."));
    if (parts.length >= 3) parentCodes.push(parts.slice(0, 3).join("."));

    const chain = parentCodes
        .slice(0, parentCodes.length - 1)
        .map((code) => index.get(code)?.name)
        .filter(Boolean);

    if (!chain.length) return region.name;
    return `${region.name} — ${chain.join(" / ")}`;
}

export function printRegions(regions: Region[], index: Map<string, Region>) {
    if (!regions.length) {
        console.log("Tidak ditemukan hasil.");
        return;
    }
    regions.forEach((region) => {
        const info = formatHierarchy(region, index);
        console.log(`${region.code.padEnd(15)} ${info}`);
    });
}
