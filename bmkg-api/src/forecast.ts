import type { ForecastEntry, ForecastResponse } from "./types";

export async function fetchForecast(adm4: string): Promise<ForecastResponse> {
    const url = `https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=${adm4}`;
    const res = await fetch(url);
    if (!res.ok) {
        throw new Error(`Gagal mengambil data (${res.status})`);
    }
    const json = await res.json();
    const lokasi =
        json?.lokasi || json?.data?.[0]?.lokasi || { adm4, provinsi: "Unknown" };

    const forecasts: ForecastEntry[] = [];
    const cuacaGroups = json?.data?.[0]?.cuaca;
    if (Array.isArray(cuacaGroups)) {
        for (const group of cuacaGroups) {
            if (Array.isArray(group)) {
                for (const entry of group) {
                    forecasts.push({
                        local_datetime: entry.local_datetime,
                        utc_datetime: entry.utc_datetime,
                        weather_desc: entry.weather_desc,
                        t: entry.t,
                        hu: entry.hu,
                        ws: entry.ws,
                        vs_text: entry.vs_text,
                    });
                }
            }
        }
    }

    return { lokasi, forecasts };
}

export function printForecast(adm4: string, forecasts: ForecastEntry[]) {
    const upcoming = forecasts.filter((f) => f.local_datetime).slice(0, 10);

    if (!upcoming.length) {
        console.log(`Tidak ada data prakiraan untuk ${adm4}`);
        return;
    }

    for (const f of upcoming) {
        const temp = typeof f.t === "number" ? `${f.t}°C` : "-";
        const rh = typeof f.hu === "number" ? `${f.hu}%` : "-";
        const wind = typeof f.ws === "number" ? `${f.ws} km/j` : "-";
        const vis = f.vs_text ?? "-";
        console.log(
            `${f.local_datetime} | ${temp} | RH ${rh} | ${wind} | ${f.weather_desc ?? "-"} | Vis ${vis}`,
        );
    }
}
