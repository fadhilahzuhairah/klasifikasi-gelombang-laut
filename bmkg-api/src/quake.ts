import type { QuakeEntry } from "./types";

const BASE = "https://data.bmkg.go.id/DataMKG/TEWS";

type RawGempa = Record<string, any>;

function parseLat(latRaw?: string): number | undefined {
    if (!latRaw) return undefined;
    const parts = latRaw.split(" ");
    const value = Number(parts[0]);
    const hemi = parts[1]?.toUpperCase();
    if (Number.isNaN(value)) return undefined;
    if (hemi === "LS") return -value;
    return value;
}

function parseLon(lonRaw?: string): number | undefined {
    if (!lonRaw) return undefined;
    const parts = lonRaw.split(" ");
    const value = Number(parts[0]);
    const hemi = parts[1]?.toUpperCase();
    if (Number.isNaN(value)) return undefined;
    if (hemi === "BB" || hemi === "W") return -value;
    return value;
}

function parseDepth(depthRaw?: string): number | undefined {
    if (!depthRaw) return undefined;
    const num = Number(depthRaw.replace(/[^0-9.]/g, ""));
    return Number.isNaN(num) ? undefined : num;
}

function normalizeGempa(g: RawGempa, source: QuakeEntry["source"]): QuakeEntry {
    return {
        source,
        tanggal: g.Tanggal,
        jam: g.Jam,
        datetime: g.DateTime ?? g.DateTimeUTC ?? g.Datetime,
        magnitude: g.Magnitude ? Number(g.Magnitude) : undefined,
        kedalaman_km: parseDepth(g.Kedalaman),
        lat: parseLat(g.Lintang),
        lon: parseLon(g.Bujur),
        wilayah: g.Wilayah,
        potensi: g.Potensi,
        dirasakan: g.Dirasakan,
        shakemap: g.Shakemap,
    };
}

async function fetchJson(path: string) {
    const res = await fetch(`${BASE}/${path}`);
    if (!res.ok) throw new Error(`Gagal mengambil data gempa (${res.status})`);
    return res.json();
}

export async function fetchLatestQuake(): Promise<QuakeEntry | undefined> {
    const data = await fetchJson("autogempa.json");
    const g = data?.Infogempa?.gempa;
    if (!g) return undefined;
    return normalizeGempa(g, "latest");
}

export async function fetchStrongQuakes(limit = 15): Promise<QuakeEntry[]> {
    const data = await fetchJson("gempaterkini.json");
    const list = data?.Infogempa?.gempa;
    if (!Array.isArray(list)) return [];
    return list.slice(0, limit).map((g: RawGempa) => normalizeGempa(g, "m5"));
}

export async function fetchFeltQuakes(limit = 15): Promise<QuakeEntry[]> {
    const data = await fetchJson("gempadirasakan.json");
    const list = data?.Infogempa?.gempa;
    if (!Array.isArray(list)) return [];
    return list.slice(0, limit).map((g: RawGempa) => normalizeGempa(g, "felt"));
}

function fmt(num?: number, suffix = ""): string {
    if (num === undefined) return "-";
    return suffix ? `${num}${suffix}` : `${num}`;
}

function shakemapUrl(code?: string): string | undefined {
    if (!code) return undefined;
    if (code.endsWith(".jpg")) return `https://static.bmkg.go.id/${code}`;
    return `https://static.bmkg.go.id/${code}.jpg`;
}

export function printQuakeList(entries: QuakeEntry[], title?: string) {
    if (title) console.log(title);
    if (!entries.length) {
        console.log("Tidak ada data gempa.");
        return;
    }
    entries.forEach((g, idx) => {
        console.log(
            `${idx + 1}. ${g.datetime ?? `${g.tanggal} ${g.jam ?? ""}`}` +
                ` | M ${fmt(g.magnitude)}` +
                ` | ${fmt(g.kedalaman_km, " km")}` +
                ` | ${g.wilayah ?? "-"}` +
                ` | potensi: ${g.potensi ?? "-"}`,
        );
        if (g.dirasakan) console.log(`    dirasakan: ${g.dirasakan}`);
        const url = shakemapUrl(g.shakemap);
        if (url) console.log(`    shakemap: ${url}`);
    });
}

export function printQuake(entry?: QuakeEntry) {
    if (!entry) {
        console.log("Tidak ada data gempa.");
        return;
    }
    console.log(
        `Waktu     : ${entry.datetime ?? `${entry.tanggal} ${entry.jam ?? ""}`}`,
    );
    console.log(`Magnitude : M ${fmt(entry.magnitude)}`);
    console.log(`Kedalaman : ${fmt(entry.kedalaman_km, " km")}`);
    console.log(`Lokasi    : lat ${fmt(entry.lat)} lon ${fmt(entry.lon)}`);
    console.log(`Wilayah   : ${entry.wilayah ?? "-"}`);
    if (entry.potensi) console.log(`Potensi   : ${entry.potensi}`);
    if (entry.dirasakan) console.log(`Dirasakan : ${entry.dirasakan}`);
    const url = shakemapUrl(entry.shakemap);
    if (url) console.log(`Shakemap  : ${url}`);
}
