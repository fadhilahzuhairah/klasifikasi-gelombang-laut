# BMKG API (Wilayah, Prakiraan, Peringatan Dini, Gempabumi) – `bmkg-api`

CLI dan utilitas JS/TS untuk:
- Cari kode wilayah administrasi (adm1–adm4).
- Ambil prakiraan cuaca (3 hari, per 3 jam) per adm4.
- Ambil peringatan dini cuaca (nowcast) CAP BMKG (RSS + detail CAP).

Dibuat ringan untuk backend, CLI, atau dijembatani ke frontend.

## Instalasi

```bash
npm install bmkg-api
# atau
pnpm add bmkg-api
# atau
bun add bmkg-api

# jika dari sumber / pengembangan:
bun install
bun run build
```

## Pemakaian CLI

```bash
# fokus Malang + pencarian cepat "malang"
bmkg

# ringkasan wilayah Malang (kab/kota, kecamatan, contoh adm4)
bmkg malang

# cari wilayah
bmkg search "<nama>" [--limit=N]
bmkg search "Banyuwangi" --limit=20

# ambil prakiraan cuaca (adm4)
bmkg fetch 35.07.01.2001

# daftar RSS peringatan dini (id/en)
bmkg alerts         # default id
bmkg alerts en

# detail CAP per kode (id/en)
bmkg alert <kode_cap> [id|en]
# contoh: bmkg alert 6oyh5RjJk5sqpZGQyM5ULqVXFfkqCk id

# cepat: feed + detail pertama
bmkg alerts-latest [id|en]

# gempabumi: terbaru, M5+, dirasakan
bmkg gempa            # terbaru (autogempa)
bmkg gempa latest     # sama seperti di atas
bmkg gempa strong     # daftar 15 M5+ (gempaterkini)
bmkg gempa felt       # daftar 15 gempa dirasakan (gempadirasakan)
```

Output fetch menampilkan 10 slot waktu terdekat (3 harian, per 3 jam). Sumber data: BMKG (api.bmkg.go.id). Batas akses API: 60 permintaan/menit/IP.
RSS/CAP nowcast: bmkg.go.id/alerts/nowcast (CAP, valid CAP Validator).
Gempabumi: data.bmkg.go.id/DataMKG/TEWS (autogempa, gempaterkini, gempadirasakan, shakemap).

### Detail Peringatan Dini (CAP)

- Feed RSS: `bmkg alerts [id|en]` menampilkan daftar provinsi/kode CAP aktif.
- Kode CAP bisa diambil dari link feed (mis. `.../CJI20251205003_alert.xml` → `CJI20251205003`).
- Detail CAP: `bmkg alert <kode> [id|en]` menampilkan headline, event, urgency, severity, certainty, waktu effective/expire, deskripsi, web, dan daftar area terdampak (dibatasi 10 pertama untuk ringkas).
- `bmkg alerts-latest` menampilkan ringkasan feed (5 teratas) dan otomatis memuat detail CAP pertama.
- Standar CAP, format XML, sumber: BMKG (bmkg.go.id/alerts/nowcast). Batas: 60 permintaan/menit/IP.

## API Library

Import dari package (ESM):

```ts
import {
  loadRegions,
  searchRegions,
  fetchForecast,
  fetchAlertFeed,
  fetchAlertDetail,
  extractCodeFromLink,
  fetchLatestQuake,
  fetchStrongQuakes,
  fetchFeltQuakes,
  BASE_CSV_PATH,
  type Region,
  type ForecastEntry,
  type AlertFeedItem,
  type AlertDetail,
  type QuakeEntry,
} from "bmkg-api";

const regions: Region[] = loadRegions(); // default pakai base.csv terbundle
const matches = searchRegions(regions, "Malang", 10);

const adm4 = matches[0]?.code;
if (adm4) {
  const { forecasts } = await fetchForecast(adm4);
  forecasts.slice(0, 5).forEach((f: ForecastEntry) => {
    console.log(f.local_datetime, f.weather_desc, f.t, f.hu);
  });
}

const feed: AlertFeedItem[] = await fetchAlertFeed("id");
const code = extractCodeFromLink(feed[0]?.link);
if (code) {
  const detail: AlertDetail = await fetchAlertDetail(code, "id");
  console.log(detail.info.headline, detail.info.event);
}
```

Fungsi utama:
- `loadRegions(path?)` memuat base.csv (kode wilayah adm1–adm4).
- `searchRegions(regions, query, limit?)` mencari nama/kode, memprioritaskan Malang jika relevan.
- `fetchForecast(adm4)` mengambil prakiraan 3 hari (3 jam sekali) dari BMKG.
- `fetchAlertFeed(lang)` mengambil RSS peringatan dini (id/en).
- `fetchAlertDetail(code, lang)` mengambil CAP detail per kode.
- `extractCodeFromLink(link)` mengekstrak kode CAP dari link RSS.
- `fetchLatestQuake()` gempabumi terbaru (autogempa).
- `fetchStrongQuakes(limit?)` daftar M5+ (gempaterkini).
- `fetchFeltQuakes(limit?)` daftar gempa dirasakan (gempadirasakan).
- `printQuake`, `printQuakeList` untuk output terminal.
- `BASE_CSV_PATH` menunjuk file CSV terbundle (berguna saat dijalankan dari luar repo).
- `BASE_JSON_PATH` menunjuk file JSON terbundle (lebih cepat dibaca jika tersedia).

## Integrasi Frontend

- Library ini memakai `fs` untuk memuat `base.csv`, jadi untuk browser:
  1. Sajikan `base.csv` sebagai aset statik (misal `/base.csv`).
  2. Ambil dengan `fetch("/base.csv")` lalu parsing client-side, atau gunakan endpoint backend yang sudah memanggil `loadRegions`.
- Panggilan API prakiraan tetap langsung ke `https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=...` (ingat batas 60/min/IP). Tambahkan cache di backend jika memerlukan.

## Pengembangan & Publikasi

- `bun run dev` menjalankan CLI dari sumber (TS).
- `bun run build` menghasilkan bundle ESM di `dist/` dan menyalin `base.csv`.
- Untuk publikasi npm: pastikan versi di `package.json`, lalu `npm publish --access public` (atau `pnpm/npm publish` sesuai registry).

## Catatan & Kepatuhan

- Cantumkan BMKG sebagai sumber data pada aplikasi Anda.
- Hormati batas laju 60 permintaan per menit per IP.
- Data wilayah berasal dari `base.csv` (kode wilayah administrasi tingkat IV, Kemendagri 100.1.1-6117/2022).
- Peringatan dini (nowcast) menggunakan RSS + CAP dari bmkg.go.id/alerts/nowcast; valid CAP.
- Data gempabumi dari data.bmkg.go.id/DataMKG/TEWS (autogempa, gempaterkini, gempadirasakan, shakemap).
