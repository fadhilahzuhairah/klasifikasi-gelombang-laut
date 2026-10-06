#!/usr/bin/env node
import { BASE_CSV_PATH, loadRegions } from "./data";
import { fetchForecast, printForecast } from "./forecast";
import { malangSnapshot } from "./malang";
import { printRegions, searchRegions } from "./search";
import {
    fetchAlertDetail,
    fetchAlertFeed,
    printAlertDetail,
    printAlertFeed,
    extractCodeFromLink,
} from "./alerts";
import {
    fetchLatestQuake,
    fetchStrongQuakes,
    fetchFeltQuakes,
    printQuake,
    printQuakeList,
} from "./quake";

const DEFAULT_QUERY = "malang";

async function main() {
    const args = process.argv.slice(2);
    const regions = loadRegions(BASE_CSV_PATH);
    const index = new Map(regions.map((r) => [r.code, r]));

    const cmd = args[0];

    if (cmd === "search") {
        const query = args[1] ?? DEFAULT_QUERY;
        const limitArg = args.find((v) => v.startsWith("--limit="));
        const limit = limitArg ? Number(limitArg.split("=")[1]) : 25;
        console.log(`Hasil pencarian untuk "${query}" (maks ${limit}):`);
        const matches = searchRegions(regions, query, limit);
        printRegions(matches, index);
        return;
    }

    if (cmd === "fetch") {
        const adm4 = args[1];
        if (!adm4) {
            console.error("Gunakan: bmkg fetch <adm4>");
            process.exit(1);
        }
        console.log(`Mengambil prakiraan BMKG untuk ${adm4}...`);
        const { lokasi, forecasts } = await fetchForecast(adm4);
        console.log(
            `${lokasi?.desa ?? "-"}, ${lokasi?.kecamatan ?? "-"}, ${lokasi?.kotkab ?? "-"}, ${lokasi?.provinsi ?? "-"}`,
        );
        printForecast(adm4, forecasts);
        console.log("Sumber data: BMKG (api.bmkg.go.id)");
        return;
    }

    if (cmd === "alerts") {
        const langArg = args[1] === "en" ? "en" : "id";
        console.log(`Memuat RSS peringatan dini BMKG (${langArg})...`);
        const items = await fetchAlertFeed(langArg);
        printAlertFeed(items);
        return;
    }

    if (cmd === "alert") {
        const code = args[1];
        const langArg = args[2] === "en" ? "en" : "id";
        if (!code) {
            console.error("Gunakan: bmkg alert <kode> [id|en]");
            process.exit(1);
        }
        console.log(`Mengambil detail CAP ${code} (${langArg})...`);
        const detail = await fetchAlertDetail(code, langArg);
        printAlertDetail(detail);
        console.log("Sumber data: BMKG (bmkg.go.id/alerts/nowcast)");
        return;
    }

    if (cmd === "alerts-latest") {
        // shortcut: show feed and auto-fetch first detail if available
        const langArg = args[1] === "en" ? "en" : "id";
        console.log(`Memuat RSS peringatan dini BMKG (${langArg})...`);
        const items = await fetchAlertFeed(langArg);
        printAlertFeed(items.slice(0, 5));
        const code = extractCodeFromLink(items[0]?.link);
        if (code) {
            console.log(`\nDetail CAP pertama (${code}):`);
            const detail = await fetchAlertDetail(code, langArg);
            printAlertDetail(detail);
        }
        console.log("Sumber data: BMKG (bmkg.go.id/alerts/nowcast)");
        return;
    }

    if (cmd === "gempa" || cmd === "quake") {
        const sub = args[1] ?? "latest";
        if (sub === "latest") {
            console.log("Memuat gempabumi terbaru (autogempa)...");
            const data = await fetchLatestQuake();
            printQuake(data);
            console.log("Sumber data: BMKG (data.bmkg.go.id/DataMKG/TEWS)");
            return;
        }
        if (sub === "strong") {
            console.log("Daftar 15 gempabumi M5+ (gempaterkini)...");
            const list = await fetchStrongQuakes();
            printQuakeList(list, "Gempabumi M5+");
            console.log("Sumber data: BMKG (data.bmkg.go.id/DataMKG/TEWS)");
            return;
        }
        if (sub === "felt") {
            console.log("Daftar 15 gempabumi dirasakan (MMI)...");
            const list = await fetchFeltQuakes();
            printQuakeList(list, "Gempabumi Dirasakan");
            console.log("Sumber data: BMKG (data.bmkg.go.id/DataMKG/TEWS)");
            return;
        }
        console.error("Gunakan: bmkg gempa [latest|strong|felt]");
        process.exit(1);
    }

    if (cmd === "malang") {
        malangSnapshot(regions, index);
        return;
    }

    console.log(
        `Tidak ada perintah, menampilkan fokus Malang dan pencarian default "${DEFAULT_QUERY}".`,
    );
    malangSnapshot(regions, index);
    console.log("\nPencarian cepat:");
    const matches = searchRegions(regions, DEFAULT_QUERY, 40);
    printRegions(matches, index);
}

main().catch((err) => {
    console.error(err);
    process.exit(1);
});
