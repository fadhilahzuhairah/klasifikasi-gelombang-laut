import { XMLParser } from "fast-xml-parser";
import type { AlertDetail, AlertFeedItem } from "./types";

const FEED_BASE = "https://www.bmkg.go.id/alerts/nowcast";

const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: "",
    parseAttributeValue: true,
});

export async function fetchAlertFeed(lang: "id" | "en" = "id"): Promise<AlertFeedItem[]> {
    const url = `${FEED_BASE}/${lang}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Gagal mengambil RSS nowcast (${res.status})`);
    const xml = await res.text();
    const rss = parser.parse(xml);
    const items = rss?.rss?.channel?.item ?? [];
    if (!Array.isArray(items)) return [];
    return items.map((item: any) => ({
        title: item.title,
        link: item.link,
        description: item.description,
        author: item.author,
        pubDate: item.pubDate,
        lastBuildDate: rss?.rss?.channel?.lastBuildDate,
    }));
}

export async function fetchAlertDetail(code: string, lang: "id" | "en" = "id"): Promise<AlertDetail> {
    const url = `${FEED_BASE}/${lang}/${code}_alert.xml`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Gagal mengambil CAP detail (${res.status})`);
    const xml = await res.text();
    const cap = parser.parse(xml);
    const alert = cap?.alert;
    const info = Array.isArray(alert?.info) ? alert.info[0] : alert?.info ?? {};
    const area = Array.isArray(info?.area) ? info.area : info?.area ? [info.area] : [];
    const normalizeArea = area.map((a: any) => ({
        areaDesc: a?.areaDesc,
        polygon: Array.isArray(a?.polygon) ? a.polygon : a?.polygon ? [a.polygon] : [],
        geocode: Array.isArray(a?.geocode) ? a.geocode : a?.geocode ? [a.geocode] : [],
    }));

    return {
        identifier: alert?.identifier,
        sender: alert?.sender,
        sent: alert?.sent,
        status: alert?.status,
        msgType: alert?.msgType,
        scope: alert?.scope,
        code: alert?.code,
        references: alert?.references,
        info: {
            language: info?.language,
            category: Array.isArray(info?.category)
                ? info.category
                : info?.category
                    ? [info.category]
                    : [],
            event: info?.event,
            urgency: info?.urgency,
            severity: info?.severity,
            certainty: info?.certainty,
            effective: info?.effective,
            expires: info?.expires,
            senderName: info?.senderName,
            headline: info?.headline,
            description: info?.description,
            web: info?.web,
            area: normalizeArea,
        },
    };
}

export function printAlertFeed(items: AlertFeedItem[]) {
    if (!items.length) {
        console.log("Tidak ada peringatan aktif.");
        return;
    }
    items.forEach((item, idx) => {
        const code = extractCodeFromLink(item.link);
        console.log(
            `${idx + 1}. ${item.title} | pub: ${item.pubDate ?? "-"} | code: ${code ?? "-"}`
        );
        if (item.description) console.log(`   ${item.description}`);
        if (item.link) console.log(`   ${item.link}`);
    });
}

export function printAlertDetail(detail: AlertDetail) {
    const info = detail.info || {};
    console.log(`Headline   : ${info.headline ?? "-"}`);
    console.log(`Event      : ${info.event ?? "-"}`);
    console.log(`Urgency    : ${info.urgency ?? "-"}`);
    console.log(`Severity   : ${info.severity ?? "-"}`);
    console.log(`Certainty  : ${info.certainty ?? "-"}`);
    console.log(`Effective  : ${info.effective ?? "-"}`);
    console.log(`Expires    : ${info.expires ?? "-"}`);
    console.log(`Sender     : ${info.senderName ?? detail.sender ?? "-"}`);
    if (info.description) console.log(`Deskripsi  : ${info.description}`);
    if (info.web) console.log(`Web        : ${info.web}`);

    if (info.area?.length) {
        console.log("Wilayah terdampak:");
        info.area.slice(0, 10).forEach((a, i) => {
            console.log(` ${i + 1}. ${a.areaDesc ?? "-"}`);
            if (a.polygon?.length) console.log(`    polygon: ${a.polygon[0]}`);
        });
        if (info.area.length > 10) {
            console.log(` (+${info.area.length - 10} area lainnya)`);
        }
    }
}

export function extractCodeFromLink(link: string | undefined): string | undefined {
    if (!link) return undefined;
    const match = link.match(/([A-Za-z0-9_-]+)_alert\.xml/);
    return match?.[1];
}
