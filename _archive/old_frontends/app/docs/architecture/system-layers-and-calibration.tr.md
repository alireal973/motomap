[![Language: English](https://img.shields.io/badge/Language-English-1f6feb)](system-layers-and-calibration.md)
[![Language: Turkish](https://img.shields.io/badge/Language-Turkish-c92a2a)](system-layers-and-calibration.tr.md)

# MotoMap Sistem Katmanlari

Bu dokuman, MotoMap'in uctan uca teknik katmanlarini ve kalibrasyon/degerlendirme geri-besleme dongusunu tek yerde ozetler.

## 1) Ana Mimari (Katmanli)

```mermaid
flowchart TB
    subgraph L0[Katman 0 - Harici Veri Kaynaklari]
        OSM[OpenStreetMap yol agi]
        ELEV[Google Elevation API / OpenTopo]
        TRAFIK[Canli trafik kaynagi]
        OBS[GPS izleri / benchmark verisi]
    end

    subgraph L1[Katman 1 - Veri Alma ve Dayaniklilik]
        DL[data_loader.py\nload_graph]
        OV[osm_validator.py\nfilter_motorcycle_edges]
        EL[elevation.py\nadd_elevation + fallback]
    end

    subgraph L2[Katman 2 - Ozellik Uretimi]
        GR[elevation.py\nadd_grade]
        CL[data_cleaner.py\nclean_graph]
        CR[curve_risk.py\ncurve + risk metrikleri]
    end

    subgraph L3[Katman 3 - Maliyet ve Rota Cekirdegi]
        TT[router.py\nadd_travel_time_to_graph]
        MW[router.py\nmode-specific weight]
        RT[router.py\nucret_opsiyonlu_rota_hesapla]
    end

    subgraph L4[Katman 4 - Orkestrasyon ve Sunum]
        PUB[motomap.__init__.py\nmotomap_graf_olustur]
        API[REST API / servis katmani]
        APP[Web/Mobil istemci]
        OUT[Script ciktilari\nmap/pdf/png/npz]
    end

    subgraph L5[Katman 5 - Degerlendirme ve Kalibrasyon]
        MET[Metric hesaplari\nETA, risk, rota farki]
        EVA[Eval setleri\nmode/baseline karsilastirma]
        TUNE[Parametre ayari\nspeed factor, delay, ceza agirliklari]
    end

    OSM --> DL
    ELEV --> EL
    TRAFIK --> TT
    OBS --> EVA

    DL --> OV --> EL --> GR --> CL --> CR
    CL --> TT
    CR --> MW
    TT --> MW --> RT

    RT --> API --> APP
    RT --> OUT
    RT --> MET --> EVA --> TUNE --> TT
    TUNE --> MW

    PUB --> DL
    PUB --> OV
    PUB --> EL
    PUB --> GR
    PUB --> CL

    style L0 fill:#fef3c7,stroke:#d97706
    style L1 fill:#dbeafe,stroke:#1d4ed8
    style L2 fill:#dcfce7,stroke:#15803d
    style L3 fill:#ede9fe,stroke:#6d28d9
    style L4 fill:#fee2e2,stroke:#b91c1c
    style L5 fill:#e0f2fe,stroke:#0369a1
```

## 2) Katman Bazli Ne / Neden

| Katman | Ne yapar? | Neden gerekli? | Baslica bilesenler |
|---|---|---|---|
| 0. Harici veri | Yol, yukseklik, trafik ve gozlem verisini saglar. | Rota motoru dogru model icin gercek dunya girdisine baglidir. | OSM, Google/OpenTopo, trafik feed, GPS izleri |
| 1. Veri alma | Grafin cekilmesi, motosiklete uygun olmayan kenarlarin elenmesi, elevation fallback. | Kirli/eksik veri dogrudan rota hatasina donusur; dayaniklilik gerekir. | `data_loader.py`, `osm_validator.py`, `elevation.py` |
| 2. Ozellik uretimi | Egim, serit/speed/surface tamamlama, viraj ve risk metrikleri. | Ham OSM etiketi tek basina rota maliyetini aciklamaz. | `add_grade`, `clean_graph`, `add_curve_and_risk_metrics` |
| 3. Cekirdek rota | Sure tabanli temel maliyet + mod bazli agirlik + ucretli/ucretsiz secim. | Kullanici tercihini (standart/guvenli/viraj keyfi) sayisal optimizasyona cevirir. | `router.py` |
| 4. Sunum | Pipeline orkestrasyonu, API entegrasyonu, istemciye sonuc sunumu. | Cekirdek algoritmayi urun arayuzu ile birlestirir. | `motomap_graf_olustur`, servis katmani, script ciktilari |
| 5. Eval+kalibrasyon | KPI olcumu, baseline karsilastirmasi, parametre geri beslemesi. | Modeli sahadaki davranisa yaklastirir ve regresyonu sinirlar. | metric/eval scriptleri, parametre tuning |

## 3) Kalibrasyon / Degerlendirme Dongusu (Flow)

```mermaid
flowchart LR
    A[1. Senaryo ve gozlem verisi hazirla\nOD seti + GPS/baseline] -->
    B[2. Mevcut parametrelerle rota uret\nstandart/guvenli/viraj_keyfi]

    B --> C[3. Metrikleri hesapla\nETA MAE/MAPE, risk skoru, rota benzerligi]
    C --> D{4. Kabul esikleri saglandi mi?}

    D -- Evet --> E[5. Parametre setini sabitle\nrelease + dokumantasyon]
    D -- Hayir --> F[6. Parametreleri guncelle\nMOTOMAP_SPEED_FACTOR\nMOTOMAP_SEGMENT_DELAY_S\nroad/curve/grade cezalari]

    F --> G[7. Regresyon testlerini calistir\nunit + senaryo eval]
    G --> B

    E --> H[8. Uretim izleme\nlatency, pass-rate, mod ayrisimi]
    H --> A
```

Kisa not:
- Dongu tek seferlik degil, surekli calisan bir kalite kontrol mekanizmasidir.
- Ozellikle `speed_factor` ve `segment_delay` ETA kalibrasyonunda ilk oynanan parametrelerdir.

## 4) Kisa Sozluk

| Terim | Kisa aciklama |
|---|---|
| OD (Origin-Destination) | Baslangic-varis nokta cifti. |
| Edge | Yol grafindaki yonlu baglanti (yol parcasi). |
| Grade | Yolun egim orani (pozitif: tirmanis, negatif: inis). |
| Curvature | Yolun virajlilik seviyesi (aci/sekil degisimi). |
| Baseline | Karsilastirma icin referans sistem veya rota sonucu. |
| Calibration | Parametreleri gozleme gore ayarlama sureci. |
| Evaluation | KPI metrikleriyle performans olcumu. |
| KPI | Kaliteyi takip etmek icin secilen ana olcum gostergesi. |
