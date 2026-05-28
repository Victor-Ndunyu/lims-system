import { useEffect, useRef, useState } from "react";

function loadLeaflet(): Promise<void> {
  return new Promise((resolve) => {
    if ((window as any).L) { resolve(); return; }
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
    document.head.appendChild(link);
    const script = document.createElement("script");
    script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    script.onload = () => resolve();
    document.head.appendChild(script);
  });
}

export function MapPicker({
  latitude,
  longitude,
  onChange,
}: {
  latitude: number | null;
  longitude: number | null;
  onChange: (lat: number, lng: number) => void;
}) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<any>(null);
  const markerRef = useRef<any>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    loadLeaflet().then(() => setReady(true));
  }, []);

  useEffect(() => {
    if (!ready || !mapRef.current || mapInstance.current) return;

    const L = (window as any).L;
    const map = L.map(mapRef.current, {
      center: [latitude ?? -1.2921, longitude ?? 36.8219],
      zoom: latitude && longitude ? 12 : 8,
      attributionControl: false,
    });
    mapInstance.current = map;

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
    }).addTo(map);

    if (latitude && longitude) {
      markerRef.current = L.marker([latitude, longitude], { draggable: true }).addTo(map);
      markerRef.current.on("dragend", () => {
        const pos = markerRef.current.getLatLng();
        onChange(pos.lat, pos.lng);
      });
    }

    map.on("click", (e: any) => {
      const { lat, lng } = e.latlng;
      placeMarker(lat, lng);
      onChange(lat, lng);
    });

    return () => {
      map.remove();
      mapInstance.current = null;
      markerRef.current = null;
    };
  }, [ready]);

  function placeMarker(lat: number, lng: number) {
    const L = (window as any).L;
    const map = mapInstance.current;
    if (!map) return;
    if (markerRef.current) {
      markerRef.current.setLatLng([lat, lng]);
    } else {
      const marker = L.marker([lat, lng], { draggable: true }).addTo(map);
      marker.on("dragend", () => {
        const pos = marker.getLatLng();
        onChange(pos.lat, pos.lng);
      });
      markerRef.current = marker;
    }
  }

  useEffect(() => {
    if (!mapInstance.current || !latitude || !longitude) return;
    const map = mapInstance.current;
    const L = (window as any).L;

    if (markerRef.current) {
      markerRef.current.setLatLng([latitude, longitude]);
    } else {
      const marker = L.marker([latitude, longitude], { draggable: true }).addTo(map);
      marker.on("dragend", () => {
        const pos = marker.getLatLng();
        onChange(pos.lat, pos.lng);
      });
      markerRef.current = marker;
    }
    map.setView([latitude, longitude], map.getZoom());
  }, [latitude, longitude]);

  return <div ref={mapRef} className="map-picker" />;
}
