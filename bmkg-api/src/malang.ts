import type { Region } from "./types";
import { printRegions } from "./search";

export function malangSnapshot(regions: Region[], index: Map<string, Region>) {
    const kabMalang = index.get("35.07");
    const kotaMalang = index.get("35.73");
    console.log("=== Fokus Malang ===");
    if (kabMalang) {
        console.log(`Kabupaten: ${kabMalang.code} ${kabMalang.name}`);
        const kec = regions.filter(
            (r) => r.level === "kecamatan" && r.code.startsWith("35.07."),
        );
        console.log(
            `  Kecamatan (${kec.length}): ${kec
                .map((r) => `${r.code} ${r.name}`)
                .join(", ")}`,
        );
    }
    if (kotaMalang) {
        console.log(`Kota: ${kotaMalang.code} ${kotaMalang.name}`);
        const kec = regions.filter(
            (r) => r.level === "kecamatan" && r.code.startsWith("35.73."),
        );
        console.log(
            `  Kecamatan (${kec.length}): ${kec
                .map((r) => `${r.code} ${r.name}`)
                .join(", ")}`,
        );
    }
    const contohDesa = regions
        .filter(
            (r) =>
                r.level === "desa" &&
                (r.code.startsWith("35.07.") || r.code.startsWith("35.73.")),
        )
        .slice(0, 10);
    if (contohDesa.length) {
        console.log(
            `Contoh desa/kelurahan (${contohDesa.length}): ${contohDesa
                .map((r) => `${r.code} ${r.name}`)
                .join(", ")}`,
        );
        console.log(
            `Gunakan salah satu adm4 di atas, contoh: bmkg fetch ${contohDesa[0].code}`,
        );
    }
}

export function malangSearch(regions: Region[], index: Map<string, Region>) {
    const matches = regions.filter(
        (r) => r.code.startsWith("35.07.") || r.code.startsWith("35.73."),
    );
    printRegions(matches, index);
}
