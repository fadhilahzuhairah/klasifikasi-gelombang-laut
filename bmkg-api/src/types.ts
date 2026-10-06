export type Level = "provinsi" | "kotkab" | "kecamatan" | "desa" | "unknown";

export type Region = {
    code: string;
    name: string;
    level: Level;
};

export type ForecastEntry = {
    local_datetime?: string;
    utc_datetime?: string;
    weather_desc?: string;
    t?: number;
    hu?: number;
    ws?: number;
    vs_text?: string;
};

export type ForecastResponse = {
    lokasi: Record<string, unknown>;
    forecasts: ForecastEntry[];
};

export type AlertFeedItem = {
    title: string;
    link: string;
    description?: string;
    author?: string;
    pubDate?: string;
    lastBuildDate?: string;
};

export type AlertDetail = {
    identifier?: string;
    sender?: string;
    sent?: string;
    status?: string;
    msgType?: string;
    scope?: string;
    code?: string;
    references?: string;
    info: {
        language?: string;
        category?: string[];
        event?: string;
        urgency?: string;
        severity?: string;
        certainty?: string;
        effective?: string;
        expires?: string;
        senderName?: string;
        headline?: string;
        description?: string;
        web?: string;
        area?: {
            areaDesc?: string;
            polygon?: string[];
            geocode?: { valueName?: string; value?: string }[];
        }[];
    };
};

export type QuakeEntry = {
    source?: "latest" | "m5" | "felt";
    tanggal?: string;
    jam?: string;
    datetime?: string;
    magnitude?: number;
    kedalaman_km?: number;
    lat?: number;
    lon?: number;
    wilayah?: string;
    potensi?: string;
    dirasakan?: string;
    shakemap?: string;
};
