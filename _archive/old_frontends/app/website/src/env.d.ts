/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_GOOGLE_MAPS_API_KEY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare namespace google.maps {
  class Map {
    constructor(element: HTMLElement, options: MapOptions);
  }

  class Polyline {
    constructor(options: PolylineOptions);
    setMap(map: Map | null): void;
  }

  class Circle {
    constructor(options: CircleOptions);
    setMap(map: Map | null): void;
  }

  interface MapOptions {
    center: LatLngLiteral;
    zoom: number;
    styles?: MapTypeStyle[];
    mapTypeControl?: boolean;
    streetViewControl?: boolean;
  }

  interface LatLngLiteral {
    lat: number;
    lng: number;
  }

  interface PolylineOptions {
    path?: LatLngLiteral[];
    strokeColor?: string;
    strokeWeight?: number;
    strokeOpacity?: number;
    map?: Map;
  }

  interface CircleOptions {
    center: LatLngLiteral;
    radius: number;
    fillColor?: string;
    fillOpacity?: number;
    strokeColor?: string;
    strokeOpacity?: number;
    strokeWeight?: number;
    map?: Map;
  }

  interface MapTypeStyle {
    elementType?: string;
    featureType?: string;
    stylers: { [key: string]: string }[];
  }
}
