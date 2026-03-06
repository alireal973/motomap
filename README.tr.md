[![Language: English](https://img.shields.io/badge/Language-English-1f6feb)](README.md)
[![Language: Turkish](https://img.shields.io/badge/Language-Turkish-c92a2a)](README.tr.md)

<div align="center">

<img src="logo/logo.svg" alt="MotoMap transparent logo" width="420" />

# MOTOMAP

### Motosikletçiler Için Akilli Rota Optimizasyon Motoru

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://python.org)
[![Status](https://img.shields.io/badge/Status-Gelistiriliyor-orange.svg)]()

*Standart navigasyon uygulamalari arabalara göre rota çizerken,*
*MOTOMAP motosikletlerin fiziksel avantajlarini ve kisitlamalarini matematiksel olarak modelleyerek*
*bireysellestirilmis rotalar üretir.*

</div>

---

## Içindekiler

- [Neden MOTOMAP?](#neden-motomap)
- [Temel Özellikler](#temel-özellikler)
- [Teknik Mimari](#teknik-mimari)
- [Veri Kaynaklari](#veri-kaynaklari)
- [Teknoloji Yigini](#teknoloji-yigini)
- [Kurulum](#kurulum)
- [Hizli Baslangiç](#hizli-baslangiç)
- [DEM/API Çiktilari](#demapi-çiktilari)
- [Uygulama Plani (Implementation Plan)](#uygulama-plani-implementation-plan)
- [Proje Durumu](#proje-durumu)
- [Algoritma Parametreleri Özet Tablosu](#algoritma-parametreleri-özet-tablosu)
- [Lisans](#lisans)
- [Yazar](#yazar)

---

## Neden MOTOMAP?

Mevcut navigasyon uygulamalari (Google Maps, Yandex, Apple Maps) tüm araçlara ayni rotayi sunar. Ancak motosikletler trafikte temelden farkli hareket eder:

> Sikisik bir E-5 trafiginde arabalar **duragan** haldeyken, motosikletler serit aralarindan siyrilarak ilerleyebilir. Google Maps "45 dakika" gösterirken, bir motosikletçi ayni mesafeyi **15 dakikada** katedebilir.

MOTOMAP bu farki algoritmik olarak modelleyen **ilk açik kaynak navigasyon motorudur.**

---

## Temel Özellikler

### 1. Serit Filtreleme (Lane Filtering)

Sikisik trafikte motosikletlerin serit aralarindan geçebilme avantajini modelleyen dinamik hiz hesaplamasi. Motosiklet hizi, gidis yönündeki serit sayisina ve anlik trafik durumuna bagli olarak hesaplanir:

$$
V_{moto} = \begin{cases}
V_{araba} + 5 & \text{if } n_{serit} = 1 \\
\max(V_{araba} + 15,\ 25) & \text{if } n_{serit} = 2 \\
\max(V_{araba} + 20,\ 35) & \text{if } n_{serit} \geq 3
\end{cases}
$$

Burada:
- $V_{moto}$ : Motosikletin tahmini hizi (km/s)
- $V_{araba}$ : Arabalarin anlik ortalama hizi (km/s)
- $n_{serit}$ : Gidis yönündeki serit sayisi

| Senaryo | Serit (Gidis) | Araba Hizi | Motor Hizi | Açiklama |
|:---:|:---:|:---:|:---:|:---|
| Tek seritli yol | 1 | 10 km/s | 10 km/s | Manevra alani dar, sinirli avantaj |
| Çift seritli cadde | 2 | 10 km/s | 25 km/s | Serit arasi filtreleme mümkün |
| Genis bulvar / otoyol | 3+ | 5 km/s | 35 km/s | Çoklu kaçis yolu, rahat geçis |

> **Not:** Trafik akici ise ($V_{araba} \geq V_{max} - 10$), filtrelemeye gerek yoktur ve motor arabalarla ayni hizda gider.

---

### 2. Motor Hacmine Göre Bireysel Rota (CC Bazli Optimizasyon)

#### Otoban Kisitlamasi

50cc ve alti motosikletler yasal olarak otobana çikamazlar. Bu kisitlama sonsuz maliyet ile modellenir:

$$
C_{otoban}(e) = \begin{cases}
\infty & \text{if } CC \leq 50 \text{ and } e \in \{motorway, trunk\} \\
1.0 & \text{otherwise}
\end{cases}
$$

#### Egim Cezasi

Düsük hacimli motorlar dik yokuslarda zorlanir. Egim cezasi çarpani:

$$
C_{egim}(\alpha, CC) = \begin{cases}
10.0 & \text{if } CC \leq 50 \text{ and } |\alpha| > 12\% \\
3.0 & \text{if } CC \leq 50 \text{ and } 8\% < |\alpha| \leq 12\% \\
1.5 & \text{if } CC \leq 50 \text{ and } 5\% < |\alpha| \leq 8\% \\
1.0 & \text{otherwise}
\end{cases}
$$

Burada $\alpha$ yolun egim yüzdesidir ve DEM (Digital Elevation Model) verisinden hesaplanir.

| CC Sinifi | Otoban Erisimi | %5-8 Egim | %8-12 Egim | %12+ Egim |
|:---:|:---:|:---:|:---:|:---:|
| $\leq$ 50cc | $\infty$ (engel) | 1.5x | 3.0x | 10.0x |
| 51-249cc | Serbest | 1.0x | 1.2x | 1.5x |
| $\geq$ 250cc | Serbest | 1.0x | 1.0x | 1.0x |

---

### 3. Çift Modlu Sürücü Deneyimi

```mermaid
flowchart TD
    A["Kullanici Uygulamaya Girer"]
    B{"Sürüs Amaci?"}
    C["IS IÇIN"]
    D["GEZI IÇIN"]

    C1["Baslangiç & Bitis Noktasi"]
    C2{"Ücretli Yol Tercihi?"}
    C3["ucretli_serbest: Ücretli + Ücretsiz Adaylar"]
    C4["ucretsiz: Ücretli Kenarlar Dislanir"]
    C5["Maliyet Minimizasyonu & Rota Seçimi"]
    C6["Lane Filtering Aktif"]

    D1["Yüzey Tercihi"]
    D2["Viraj Seviyesi"]
    D3["Manzara Tercihi"]
    D4["Keyif Rotasi"]

    A --> B
    B -->|"Hizli Ulasim"| C
    B -->|"Kesfet & Gez"| D

    C --> C1 --> C2
    C2 --> C3 --> C5 --> C6
    C2 --> C4 --> C5

    D --> D1 & D2 & D3
    D1 & D2 & D3 --> D4

    style C fill:#2563eb,color:#fff
    style D fill:#16a34a,color:#fff
    style C6 fill:#1d4ed8,color:#fff
    style D4 fill:#15803d,color:#fff
```

#### Mod 1 — Is Için: Zaman Minimizasyonu

Hedef fonksiyon:

$$
\min_{P \in \mathcal{P}} \sum_{e \in P} T_{moto}(e)
$$

$\mathcal{P}$: Tüm mümkün rotalar kümesi, $T_{moto}(e)$: Kenar $e$ üzerinde motosiklet geçis süresi.

Ücretli/ücretsiz tercih için iki aday rota birlikte degerlendirilir:

$$
P_{serbest}=\arg\min_{P}\sum_{e\in P}C_0(e),\qquad
P_{ucretsiz}=\arg\min_{P:U(e)=0\ \forall e\in P}\sum_{e\in P}C_0(e)
$$

- `ucretli_serbest`: ücretli + ücretsiz adaylar birlikte optimize edilir.
- `ucretsiz`: ücretli kenarlar hard constraint ile dislanir.

#### Mod 2 — Gezi Için: Keyif Maksimizasyonu

Gezi modunda her kenara ceza/ödül çarpanlari uygulanir:

**Yüzey Tipi Çarpani:**

$$
C_{yüzey}(e) = \begin{cases}
0.5 & \text{if } surface(e) = \text{tercih edilen} \\
1.0 & \text{if } surface(e) = \text{nötr} \\
50.0 & \text{if } surface(e) = \text{istenmeyen}
\end{cases}
$$

**Viraj Skoru (Sinuosity Index):**

Bir yol segmentinin ne kadar virajli oldugu su oranla ölçülür:

$$
S(e) = \frac{L_{gerçek}(e)}{L_{kus\ uçusu}(e)}
$$

- $S = 1.0$ ise yol düz, $S > 1.2$ ise virajli.

**Viraj Ödül Çarpani:**

$$
C_{viraj}(e) = \begin{cases}
0.3 & \text{if } S(e) > 1.2 \text{ (virajli yol ödüllendirilir)} \\
1.5 & \text{if } S(e) \approx 1.0 \text{ (düz yol cezalandirilir)}
\end{cases}
$$

---

## Teknik Mimari

### Sistem Mimarisi

```mermaid
graph LR
    subgraph "Veri Katmani"
        OSM["OpenStreetMap<br/>Yol Agi"]
        DEM["NASA SRTM DEM<br/>Yükseklik Verisi"]
        IBB["IBB API<br/>Canli Trafik"]
    end

    subgraph "Islem Katmani"
        GRAF["Graf Olusturucu<br/>(osmnx + networkx)"]
        SIM["Trafik Simülatörü<br/>(numpy + random)"]
        COST["Maliyet Hesaplayici<br/>(Lane Filter + CC + Egim)"]
        DIJKSTRA["Rota Çözücü<br/>(Dijkstra / A*)"]
    end

    subgraph "Sunum Katmani"
        FOLIUM["Folium Harita<br/>(HTML Çiktisi)"]
        API["REST API<br/>(Flask / FastAPI)"]
        MOBILE["Mobil Uygulama<br/>(Flutter)"]
    end

    OSM --> GRAF
    DEM --> GRAF
    IBB --> SIM
    GRAF --> COST
    SIM --> COST
    COST --> DIJKSTRA
    DIJKSTRA --> FOLIUM
    DIJKSTRA --> API --> MOBILE

    style OSM fill:#0ea5e9,color:#fff
    style DEM fill:#0ea5e9,color:#fff
    style IBB fill:#0ea5e9,color:#fff
    style DIJKSTRA fill:#7c3aed,color:#fff
    style MOBILE fill:#f59e0b,color:#000
```

### Nihai Maliyet Fonksiyonu

Dijkstra algoritmasi su bilesik agirlik degerini minimize eder:

$$
W(e) = T_{moto}(e) \times C_{otoban}(e) \times C_{egim}(e) \times C_{mod}(e)
$$

| Bilesen | Formül | Açiklama |
|:---|:---:|:---|
| $T_{moto}(e)$ | $\dfrac{d(e)}{V_{moto}(e) / 3.6}$ | Kenar uzunlugu / motosiklet hizi (saniye) |
| $C_{otoban}(e)$ | $1.0$ veya $\infty$ | CC bazli yasal otoban kisitlamasi |
| $C_{egim}(e)$ | $1.0 - 10.0$ | Yokus yukari egim ceza çarpani |
| $C_{mod}(e)$ | $0.3 - 50.0$ | Gezi modunda yüzey + viraj çarpani |

### Gidis Yönündeki Serit Sayisi

OSM verisi genellikle toplam serit sayisini verir. Gidis yönündeki serit:

$$
n_{serit}^{gidis} = \begin{cases}
n_{toplam} & \text{if } oneway = true \\
\max\left(1,\ \left\lfloor \dfrac{n_{toplam}}{2} \right\rfloor\right) & \text{if } oneway = false
\end{cases}
$$

### Veri Akis Diyagrami

```mermaid
sequenceDiagram
    participant U as Kullanici
    participant APP as MOTOMAP App
    participant GRAF as Graf Motoru
    participant OSM as OpenStreetMap
    participant DEM as DEM Dosyasi
    participant API as Trafik API

    U->>APP: Kayit (CC bilgisi)
    U->>APP: A noktasi, B noktasi, Mod seçimi
    APP->>GRAF: Rota talebi
    GRAF->>OSM: Bölge yol agi çek
    OSM-->>GRAF: MultiDiGraph
    GRAF->>DEM: Rakim verisi oku (.tif)
    DEM-->>GRAF: Node elevations
    GRAF->>GRAF: Egim hesapla (grade)
    GRAF->>API: Anlik trafik verisi
    API-->>GRAF: Araba hizlari
    GRAF->>GRAF: Lane filtering hiz hesabi
    GRAF->>GRAF: Maliyet fonksiyonu hesapla
    GRAF->>GRAF: Dijkstra çalistir
    GRAF-->>APP: Optimal rota + ETA
    APP-->>U: Harita + Uyarilar
```

---

## Veri Kaynaklari

| Veri | Kaynak | Format | Kullanim |
|:---|:---|:---:|:---|
| Yol agi (sokak grafi) | OpenStreetMap | `MultiDiGraph` | Topoloji, yol sinifi, serit, hiz limiti |
| Yükseklik / egim | NASA SRTM DEM | `.tif` (GeoTIFF) | Rakim farkindan egim hesabi |
| Anlik trafik | IBB API / Simülasyon | JSON | Araba hizlari (ileride gerçek veri) |
| Yüzey, köprü, tünel | OSM etiketleri | Edge attributes | Gezi modu tercihleri, uyarilar |

### Kullanilan OSM Etiketleri

| Etiket | Örnek Deger | Algoritmadaki Rolü |
|:---|:---|:---|
| `highway` | `motorway`, `primary`, `residential` | Yol sinifi ? otoban kisitlamasi, varsayilan hizlar |
| `lanes` | `2`, `4`, `6` | Lane filtering hiz hesabi |
| `oneway` | `yes`, `no` | Gidis yönündeki serit sayisini bulma |
| `maxspeed` | `50`, `120` | Akici trafikte referans hiz |
| `surface` | `asphalt`, `gravel`, `dirt` | Gezi modu yüzey filtresi |
| `bridge` / `tunnel` | `yes` | GPS kaybi, buzlanma uyarilari |
| `incline` | `10%`, `up` | Egim dogrulamasi |

---

## Teknoloji Yigini

```mermaid
graph TD
    subgraph "Python Backend"
        A[osmnx] --> B[networkx]
        C[rasterio] --> A
        B --> D[Dijkstra / A*]
        E[numpy] --> F[Trafik Simülasyonu]
        G[pandas / geopandas] --> A
        D --> H[folium]
    end

    subgraph "Mobil Frontend — Planlanan"
        I[Flutter / React Native]
        J[REST API — FastAPI]
    end

    D --> J --> I

    style A fill:#3b82f6,color:#fff
    style B fill:#8b5cf6,color:#fff
    style D fill:#7c3aed,color:#fff
    style H fill:#10b981,color:#fff
    style I fill:#f59e0b,color:#000
```

| Kütüphane | Versiyon | Amaç |
|:---|:---:|:---|
| `osmnx` | 1.9+ | OSM'den yol agi indirme, DEM'den rakim ekleme |
| `networkx` | 3.0+ | Graf islemleri, Dijkstra / A* algoritmalari |
| `pandas` | 2.0+ | Veri temizligi, eksik deger doldurma |
| `geopandas` | 0.14+ | Mekânsal veri islemleri |
| `numpy` | 1.24+ | Istatistiksel simülasyon veri üretimi |
| `rasterio` | 1.3+ | DEM GeoTIFF dosyasi okuma |
| `folium` | 0.15+ | Etkilesimli Leaflet harita çiktisi |

---

## Kurulum

```bash
# Sanal ortam olustur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bagimliliklari kur
pip install osmnx networkx pandas geopandas numpy folium rasterio
```

### DEM Verisi Indirme

Istanbul bölgesi için 30m çözünürlüklü SRTM verisini asagidaki kaynaklardan `.tif` formatinda indirin:

- [USGS EarthExplorer](https://earthexplorer.usgs.gov/)
- [Copernicus DEM](https://spacedata.copernicus.eu/)
- [CGIAR-CSI SRTM](https://srtm.csi.cgiar.org/)

Indirilen dosyayi proje kök dizinine `istanbul_dem.tif` olarak kaydedin.

---

## Hizli Baslangiç

```python
from motomap import motomap_graf_olustur, maliyetleri_hesapla_ve_grafa_ekle, rota_ciz

# 1. Graf olustur (pilot bölge: Kadiköy)
G = motomap_graf_olustur("Kadiköy, Istanbul, Turkey", "istanbul_dem.tif")

# 2. Maliyetleri hesapla (50cc motor, is modu)
G = maliyetleri_hesapla_ve_grafa_ekle(G, motor_cc=50, surus_amaci="is_icin")

# 3. Rota bul ve görsellestir
rota_ciz(G, baslangic_node, bitis_node)
# Çikti: motomap_test_rotasi.html
```

---

## DEM/API Çiktilari

Asagidaki artefaktlar OSM + Elevation API çagrilari ile üretilmistir:

- `outputs/dem_api/moda_kadikoy_dem_api_map.npz`
- `outputs/dem_api/moda_kadikoy_dem_api_map.pdf`
- `outputs/dem_api/moda_kadikoy_dem_api_map.svg`
- `outputs/dem_api/moda_kadikoy_elevation_3d.pdf`
- `outputs/dem_api/moda_kadikoy_elevation_3d.png`

### Bilimsel Harita (SVG)

![DEM API Science Map](outputs/dem_api/moda_kadikoy_dem_api_map.svg)

### Yükselti 3D Plot (Python)

![Elevation 3D Plot](outputs/dem_api/moda_kadikoy_elevation_3d.png)

Üretim komutlari:

```bash
python -m scripts.dem_api_map_export --place "Moda, Kadikoy, Istanbul, Turkey" --output-dir outputs/dem_api --basename moda_kadikoy_dem_api_map
python -m scripts.elevation_3d_plot --npz outputs/dem_api/moda_kadikoy_dem_api_map.npz --png-output outputs/dem_api/moda_kadikoy_elevation_3d.png --pdf-output outputs/dem_api/moda_kadikoy_elevation_3d.pdf
```

---

## Uygulama Plani (Implementation Plan)

### Faz Diyagrami

```mermaid
gantt
    title MOTOMAP Uygulama Plani
    dateFormat  YYYY-MM-DD
    axisFormat  %d %b

    section Faz 1 — Altyapi
    Proje iskeleti ve bagimliliklar         :f1a, 2026-03-01, 3d
    OSM veri çekme modülü                   :f1b, after f1a, 5d
    DEM entegrasyonu ve egim hesaplama      :f1c, after f1a, 5d
    Veri temizleme fonksiyonlari             :f1d, after f1b, 3d

    section Faz 2 — Çekirdek Algoritma
    Lane filtering hiz fonksiyonu           :f2a, after f1d, 4d
    CC bazli kisitlama sistemi              :f2b, after f1d, 3d
    Egim ceza çarpani                       :f2c, after f1c, 3d
    Maliyet fonksiyonu birlestirme          :f2d, after f2a, 4d
    Dijkstra rota çözücü                    :f2e, after f2d, 3d

    section Faz 3 — Gezi Modu
    Yüzey tipi filtresi                     :f3a, after f2e, 3d
    Sinuosity indeksi hesaplama             :f3b, after f2e, 4d
    Keyif maliyet fonksiyonu                :f3c, after f3a, 3d

    section Faz 4 — Simülasyon ve Test
    Akilli trafik simülatörü               :f4a, after f2e, 5d
    Folium görsellestirme                   :f4b, after f2e, 4d
    Uçtan uca test senaryolari              :f4c, after f4a, 5d

    section Faz 5 — Üretime Hazirlik
    REST API sunucusu                       :f5a, after f4c, 7d
    IBB API entegrasyonu                    :f5b, after f5a, 7d
    Mobil uygulama MVP                      :f5c, after f5a, 21d
```

### Detayli Faz Açiklamalari

#### Faz 1 — Veri Altyapisi

| Görev | Girdi | Çikti | Sorumlu |
|:---|:---|:---|:---:|
| Proje iskeleti olustur | — | `motomap/` paket yapisi, `requirements.txt` | — |
| `data_loader.py` : OSM veri çekme | Bölge adi (str) | `NetworkX MultiDiGraph` | — |
| `elevation.py` : DEM entegrasyonu | `.tif` dosya yolu | Graf + `elevation`, `grade`, `grade_abs` | — |
| `data_cleaner.py` : Eksik veri doldurma | Ham graf | Temiz graf (lanes, maxspeed, surface) | — |

#### Faz 2 — Çekirdek Algoritma

| Görev | Girdi | Çikti | Formül |
|:---|:---|:---|:---:|
| `lane_filter.py` : Hiz hesabi | $V_{araba}$, $n_{serit}$, $V_{max}$ | $V_{moto}$ | Serit bazli fonksiyon |
| `cc_constraint.py` : Otoban engeli | CC, yol tipi | $C_{otoban}$ | $\infty$ veya $1.0$ |
| `grade_penalty.py` : Egim cezasi | $\alpha$, CC | $C_{egim}$ | Derecelendirilmis çarpan |
| `cost_engine.py` : Bilesik maliyet | Tüm çarpanlar | $W(e)$ | $T \times C_o \times C_e \times C_m$ |
| `router.py` : Rota çözücü | Graf, A, B, weight | Node listesi + ETA | Dijkstra |

#### Faz 3 — Gezi Modu

| Görev | Girdi | Çikti | Formül |
|:---|:---|:---|:---:|
| `surface_filter.py` | Tercih, `surface` tag | $C_{yüzey}$ | Ceza / nötr / ödül |
| `sinuosity.py` | Edge geometri | $S(e)$ | $L_{gerçek} / L_{kus\ uçusu}$ |
| `joy_cost.py` | Tüm tercih çarpanlari | `keyif_maliyeti` | $d \times C_y \times C_v$ |

#### Faz 4 — Simülasyon ve Test

| Görev | Girdi | Çikti |
|:---|:---|:---|
| `traffic_sim.py` : Trafik üreteci | Yol tipi, saat dilimi | Simüle araba hizlari |
| `visualizer.py` : Folium harita | Rota node listesi | `.html` etkilesimli harita |
| `test_scenarios.py` : E2E testler | A/B noktalari, CC, mod | Beklenen vs gerçek rota |

#### Faz 5 — Üretime Hazirlik

| Görev | Açiklama |
|:---|:---|
| REST API (`FastAPI`) | Mobil uygulamanin rota taleplerini alacak backend sunucu |
| IBB API entegrasyonu | Gerçek zamanli trafik verisini simülasyon yerine baglama |
| Mobil MVP (`Flutter`) | Kayit ekrani (CC girisi), mod seçimi, harita görünümü |

### Modül Bagimliliklari

```mermaid
graph TD
    DL["data_loader.py"] --> DC["data_cleaner.py"]
    EL["elevation.py"] --> DC
    DC --> LF["lane_filter.py"]
    DC --> CC["cc_constraint.py"]
    DC --> GP["grade_penalty.py"]
    LF --> CE["cost_engine.py"]
    CC --> CE
    GP --> CE
    DC --> SF["surface_filter.py"]
    DC --> SN["sinuosity.py"]
    SF --> JC["joy_cost.py"]
    SN --> JC
    CE --> RT["router.py"]
    JC --> RT
    RT --> VZ["visualizer.py"]
    TS["traffic_sim.py"] --> CE

    style CE fill:#7c3aed,color:#fff
    style RT fill:#2563eb,color:#fff
    style VZ fill:#10b981,color:#fff
```

---

## Proje Durumu

- [x] Algoritma tasarimi ve matematiksel modelleme
- [x] README ve dokümantasyon
- [ ] Proje dosya yapisi ve paketleme
- [ ] OSM veri çekme ve graf olusturma
- [ ] DEM entegrasyonu ve egim hesaplama
- [ ] Veri temizleme (lanes, maxspeed, surface)
- [ ] Lane filtering hiz fonksiyonu
- [ ] CC bazli kisitlama sistemi
- [ ] Egim ceza çarpani
- [ ] Bilesik maliyet fonksiyonu
- [ ] Dijkstra rota çözücü
- [ ] Gezi modu: yüzey filtresi
- [ ] Gezi modu: sinuosity indeksi
- [ ] Akilli trafik simülasyonu
- [ ] Folium görsellestirme
- [ ] Uçtan uca test senaryolari
- [ ] REST API sunucusu (FastAPI)
- [ ] IBB API entegrasyonu
- [ ] Mobil uygulama MVP (Flutter)

---

## Algoritma Parametreleri Özet Tablosu

| Parametre | Sembol | Veri Kaynagi | Algoritmaya Etkisi |
|:---|:---:|:---:|:---|
| Motosiklet Hacmi | $CC$ | Kullanici | $\leq 50$: otoban $= \infty$, egim cezalari aktif |
| Serit Sayisi | $n_{serit}$ | OSM `lanes` | Arttikça $V_{moto}$ yükselir |
| Yol Egimi | $\alpha$ | DEM `.tif` | $> 5\%$: maliyet $1.5\times - 10\times$ artar |
| Yüzey Tipi | $surface$ | OSM `surface` | Gezi modunda istenmeyen $= 50\times$ ceza |
| Sürüs Amaci | $mod$ | Kullanici | Is: $\min T$, Gezi: $\min (d \times C_y \times C_v)$ |
| Anlik Trafik | $V_{araba}$ | IBB / Sim | Lane filtering tetikleyicisi |
| Hiz Siniri | $V_{max}$ | OSM `maxspeed` | Akici trafikte tavan hiz |
| Tek Yön | $oneway$ | OSM `oneway` | $n_{serit}^{gidis}$ hesabi |

---

## Lisans

Bu proje [MIT License](LICENSE) altinda lisanslanmistir.

## Yazar

**Ali Özuysal**
**Muhammet Yagcioglu**

---

<div align="center">

*MOTOMAP — Çünkü motosikletçilerin rotasi arabalara göre çizilemez.*

</div>
