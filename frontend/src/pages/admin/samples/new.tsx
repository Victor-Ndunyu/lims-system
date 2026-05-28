import { useEffect, useRef, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/router";

import { AdminLayout, Alert, Button, StatusBadge } from "../../../components/ui";
import { MapPicker } from "../../../components/map-picker";
import { createSample, fetchStaffLookups, uploadFile, createLocation, reverseGeocode, createSampleType } from "../../../lib/api";
import { AttachmentInput, LookupItem, SampleFormData } from "../../../types/sample";

const initialState: SampleFormData = {
  sample_code: "",
  sample_type_id: "",
  collection_date: new Date().toISOString().slice(0, 10),
  collector_id: "",
  location_id: "",
  description: "",
  remarks: "",
  status: "Draft",
  attachments: [],
};

function findNearbyLocation(locations: LookupItem[], lat: number, lng: number, threshold = 0.01): LookupItem | undefined {
  return locations.find((loc) => {
    if (loc.latitude == null || loc.longitude == null) return false;
    return Math.abs(loc.latitude - lat) < threshold && Math.abs(loc.longitude - lng) < threshold;
  });
}

export default function NewSampleEntry() {
  const [form, setForm] = useState<SampleFormData>(initialState);
  const [lookups, setLookups] = useState<{ sample_types: LookupItem[]; locations: LookupItem[]; collectors: LookupItem[] }>({
    sample_types: [],
    locations: [],
    collectors: [],
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [mapLat, setMapLat] = useState<number | null>(null);
  const [mapLng, setMapLng] = useState<number | null>(null);
  const [manualLat, setManualLat] = useState("");
  const [manualLng, setManualLng] = useState("");
  const [pickedLocation, setPickedLocation] = useState<{ country: string; county: string; subcounty: string; site_name: string } | null>(null);
  const [savingLocation, setSavingLocation] = useState(false);
  const [geocodeError, setGeocodeError] = useState(false);
  const [customSampleType, setCustomSampleType] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const geocodeTimer = useRef<ReturnType<typeof setTimeout>>();
  const router = useRouter();

  const isOtherType = form.sample_type_id === "other";

  useEffect(() => {
    fetchStaffLookups()
      .then((data) => setLookups(data))
      .catch((err) => setError(err.message));
  }, []);

  const selectedLocation = lookups.locations.find((loc) => loc.id === form.location_id);

  const handleChange = (field: keyof SampleFormData, value: string | AttachmentInput[]) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleFilePick = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    setUploading(true);
    setError(null);
    try {
      for (let i = 0; i < files.length; i++) {
        const result = await uploadFile(files[i]);
        setForm((current) => ({
          ...current,
          attachments: [...current.attachments, result],
        }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const removeAttachment = (index: number) => {
    setForm((current) => ({
      ...current,
      attachments: current.attachments.filter((_, i) => i !== index),
    }));
  };

  const openAttachment = (url: string) => {
    window.open(url, "_blank", "noopener");
  };

  const applyManualCoords = () => {
    const lat = parseFloat(manualLat);
    const lng = parseFloat(manualLng);
    if (isNaN(lat) || isNaN(lng)) { setError("Enter valid latitude and longitude"); return; }
    setMapLat(lat);
    setMapLng(lng);
    setError(null);
    doGeocode(lat, lng);
  };

  const doGeocode = useCallback(async (lat: number, lng: number) => {
    const existing = findNearbyLocation(lookups.locations, lat, lng);
    if (existing) {
      setForm((current) => ({ ...current, location_id: existing.id }));
      setPickedLocation({ country: existing.country || "", county: existing.county || "", subcounty: existing.subcounty || "", site_name: existing.site_name || "" });
      setGeocodeError(false);
      return;
    }

    try {
      const result = await reverseGeocode(lat, lng);
      setPickedLocation({
        country: result.country || "",
        county: result.county || "",
        subcounty: result.subcounty || "",
        site_name: result.site_name || "",
      });
      setGeocodeError(!result.country && !result.county);
    } catch {
      setGeocodeError(true);
      setPickedLocation(null);
    }
  }, [lookups.locations]);

  const handleMapClick = useCallback(async (lat: number, lng: number) => {
    setMapLat(lat);
    setMapLng(lng);
    setManualLat(String(lat));
    setManualLng(String(lng));
    if (geocodeTimer.current) clearTimeout(geocodeTimer.current);
    geocodeTimer.current = setTimeout(() => doGeocode(lat, lng), 400);
  }, [doGeocode]);

  const handleSaveLocation = async () => {
    if (mapLat == null || mapLng == null) return;
    setSavingLocation(true);
    setError(null);
    try {
      const loc = await createLocation({
        country: pickedLocation?.country || manualLat,
        county: pickedLocation?.county || undefined,
        subcounty: pickedLocation?.subcounty || undefined,
        site_name: pickedLocation?.site_name || undefined,
        latitude: mapLat,
        longitude: mapLng,
      });
      setLookups((prev) => ({ ...prev, locations: [...prev.locations, loc] }));
      setForm((current) => ({ ...current, location_id: loc.id }));
      setPickedLocation(null);
      setSuccess("Location saved");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save location");
    }
    setSavingLocation(false);
  };

  const handleClearLocation = () => {
    setForm((current) => ({ ...current, location_id: "" }));
    setMapLat(null);
    setMapLng(null);
    setPickedLocation(null);
    setManualLat("");
    setManualLng("");
    setGeocodeError(false);
  };

  const validate = () => {
    if (!form.sample_code.trim()) return "Sample code is required.";
    if (!form.sample_type_id) return "Sample type is required.";
    if (isOtherType && !customSampleType.trim()) return "Enter a custom sample type name.";
    if (!form.collection_date) return "Collection date is required.";
    if (!form.collector_id) return "Collector is required.";
    if (!form.location_id) return "Location is required.";
    return null;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    let sampleTypeId = form.sample_type_id;
    if (isOtherType && customSampleType.trim()) {
      try {
        const newType = await createSampleType(customSampleType.trim());
        sampleTypeId = newType.id;
        setLookups((prev) => ({ ...prev, sample_types: [...prev.sample_types, newType] }));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to create sample type");
        return;
      }
    }

    try {
      await createSample({ ...form, sample_type_id: sampleTypeId });
      setSuccess("Sample saved successfully.");
      router.push("/admin/samples");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Sample could not be saved.");
    }
  };

  return (
    <AdminLayout active="new">
      <section className="page-title">
        <div>
          <p className="eyebrow">Field entry</p>
          <h1>New sample record</h1>
          <p>Capture collection metadata, sample context, and supporting files for scientific review.</p>
        </div>
        <StatusBadge status={form.status} />
      </section>

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <form onSubmit={handleSubmit} className="section form-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">Sample metadata</p>
            <h2>Collection details</h2>
          </div>
          <Link className="button button-secondary" href="/admin/samples">
            Back to records
          </Link>
        </div>

        <div className="form-grid">
          <div className="field">
            <label htmlFor="sample_code">Sample code *</label>
            <input id="sample_code" value={form.sample_code} onChange={(event) => handleChange("sample_code", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="status">Status</label>
            <select id="status" value={form.status} onChange={(event) => handleChange("status", event.target.value)}>
              <option value="Draft">Draft</option>
              <option value="Submitted">Submitted</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="sample_type">Sample type *</label>
            <select id="sample_type" value={form.sample_type_id} onChange={(event) => handleChange("sample_type_id", event.target.value)}>
              <option value="">Select type</option>
              {lookups.sample_types.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
              <option value="other">Other (type custom name)</option>
            </select>
            {isOtherType && (
              <input
                style={{ marginTop: "var(--space-2)" }}
                placeholder="Enter sample type name"
                value={customSampleType}
                onChange={(e) => setCustomSampleType(e.target.value)}
              />
            )}
          </div>
          <div className="field">
            <label htmlFor="collection_date">Collection date *</label>
            <input id="collection_date" type="date" value={form.collection_date} onChange={(event) => handleChange("collection_date", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="collector">Collector *</label>
            <select id="collector" value={form.collector_id} onChange={(event) => handleChange("collector_id", event.target.value)}>
              <option value="">Select collector</option>
              {lookups.collectors.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.full_name}
                </option>
              ))}
            </select>
          </div>
          <div className="field field-full">
            <label>Location *</label>
            {selectedLocation ? (
              <div className="selected-location-banner">
                <div className="selected-location-info">
                  <strong>{selectedLocation.site_name || `${selectedLocation.country} / ${selectedLocation.county || selectedLocation.subcounty || ""}`}</strong>
                  {selectedLocation.latitude != null && selectedLocation.longitude != null && (
                    <span className="muted">{selectedLocation.latitude.toFixed(4)}, {selectedLocation.longitude.toFixed(4)}</span>
                  )}
                </div>
                <Button tone="ghost" type="button" onClick={handleClearLocation}>Change</Button>
              </div>
            ) : (
              <>
                <p className="muted" style={{ marginBottom: "var(--space-3)" }}>Enter coordinates manually or click on the map.</p>
                <div className="coord-inputs">
                  <input type="number" step="any" placeholder="Latitude" value={manualLat} onChange={(e) => setManualLat(e.target.value)} />
                  <input type="number" step="any" placeholder="Longitude" value={manualLng} onChange={(e) => setManualLng(e.target.value)} />
                  <Button tone="secondary" type="button" onClick={applyManualCoords}>Apply</Button>
                </div>
                <div style={{ height: 8 }} />
              </>
            )}
            {!selectedLocation && (
              <MapPicker
                latitude={mapLat}
                longitude={mapLng}
                onChange={handleMapClick}
              />
            )}
            {pickedLocation && !selectedLocation && (
              <div className="picked-location-card">
                <div className="picked-location-details">
                  <div className="field"><label>Country</label><span>{pickedLocation.country || "—"}</span></div>
                  <div className="field"><label>County</label><span>{pickedLocation.county || "—"}</span></div>
                  <div className="field"><label>Subcounty / Area</label><span>{pickedLocation.subcounty || "—"}</span></div>
                  <div className="field"><label>Site</label><span>{pickedLocation.site_name || "—"}</span></div>
                </div>
                {geocodeError && <p className="muted" style={{ fontSize: "0.8rem", marginBottom: "var(--space-3)" }}>Geocoding unavailable — you can still save this location.</p>}
                <Button type="button" onClick={handleSaveLocation} disabled={savingLocation}>
                  {savingLocation ? "Saving…" : "Use this location"}
                </Button>
              </div>
            )}
          </div>
          <div className="field field-full">
            <label htmlFor="description">Description</label>
            <textarea id="description" value={form.description} onChange={(event) => handleChange("description", event.target.value)} />
          </div>
          <div className="field field-full">
            <label htmlFor="remarks">Remarks</label>
            <textarea id="remarks" value={form.remarks} onChange={(event) => handleChange("remarks", event.target.value)} />
          </div>
        </div>

        <section className="section">
          <div className="section-header">
            <div>
              <p className="eyebrow">Evidence files</p>
              <h2>Attachments</h2>
            </div>
            <div className="action-row">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.csv,.txt"
                onChange={handleFilePick}
                style={{ display: "none" }}
              />
              <Button tone="secondary" type="button" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
                {uploading ? "Uploading…" : "Upload files"}
              </Button>
            </div>
          </div>
          {form.attachments.length > 0 ? (
            <div className="attachment-grid">
              {form.attachments.map((attachment, index) => (
                <div className="attachment-card" key={index}>
                  <div className="attachment-icon">{attachment.file_type?.startsWith("image/") ? "🖼" : "📄"}</div>
                  <div className="attachment-info">
                    <span className="attachment-name">{attachment.file_name}</span>
                    <span className="attachment-type">{attachment.file_type}</span>
                  </div>
                  <div className="attachment-actions">
                    <Button tone="ghost" type="button" onClick={() => openAttachment(attachment.file_url)}>View</Button>
                    <Button tone="ghost" type="button" onClick={() => removeAttachment(index)}>Remove</Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="muted" style={{ padding: "var(--space-4) 0" }}>No files attached yet. Click &quot;Upload files&quot; to add photos, PDFs, or documents.</p>
          )}
        </section>

        <div className="action-row" style={{ marginTop: 28 }}>
          <Button type="submit">Save sample</Button>
          <Link className="button button-ghost" href="/admin/samples">
            Cancel
          </Link>
        </div>
      </form>
    </AdminLayout>
  );
}
