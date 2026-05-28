import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/router";

import { AdminLayout, Alert, Button, StatusBadge } from "../../../components/ui";
import { MapPicker } from "../../../components/map-picker";
import { createSample, fetchStaffLookups, uploadFile, createLocation } from "../../../lib/api";
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
  const [showNewLocation, setShowNewLocation] = useState(false);
  const [newLocation, setNewLocation] = useState({ country: "", county: "", subcounty: "", site_name: "", latitude: "", longitude: "" });
  const [mapLat, setMapLat] = useState<number | null>(null);
  const [mapLng, setMapLng] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

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

  const validate = () => {
    if (!form.sample_code.trim()) return "Sample code is required.";
    if (!form.sample_type_id) return "Sample type is required.";
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

    try {
      await createSample(form);
      setSuccess("Sample saved successfully.");
      router.push("/admin/samples");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Sample could not be saved.");
    }
  };

  const handleCreateLocation = async () => {
    if (!newLocation.country.trim()) { setError("Country is required"); return; }
    try {
      setError(null);
      const lat = newLocation.latitude ? parseFloat(newLocation.latitude) : mapLat ?? undefined;
      const lng = newLocation.longitude ? parseFloat(newLocation.longitude) : mapLng ?? undefined;
      const loc = await createLocation({
        country: newLocation.country,
        county: newLocation.county || undefined,
        subcounty: newLocation.subcounty || undefined,
        site_name: newLocation.site_name || undefined,
        latitude: lat,
        longitude: lng,
      });
      setLookups((prev) => ({ ...prev, locations: [...prev.locations, loc] }));
      setForm((current) => ({ ...current, location_id: loc.id }));
      setShowNewLocation(false);
      setNewLocation({ country: "", county: "", subcounty: "", site_name: "", latitude: "", longitude: "" });
      setMapLat(null);
      setMapLng(null);
      setSuccess("Location created");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create location");
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
            </select>
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
          <div className="field">
            <label htmlFor="location">Location *</label>
            <div className="location-select-row">
              <select id="location" value={form.location_id} onChange={(event) => handleChange("location_id", event.target.value)}>
                <option value="">Select location</option>
                {lookups.locations.map((location) => (
                  <option key={location.id} value={location.id}>
                    {location.site_name || `${location.country} / ${location.county || location.subcounty || ""}`}
                  </option>
                ))}
              </select>
              <Button tone="ghost" type="button" onClick={() => setShowNewLocation(true)}>+ New</Button>
            </div>
            {selectedLocation && (selectedLocation.latitude || selectedLocation.longitude) && (
              <div className="location-coords">
                <span>{selectedLocation.latitude?.toFixed(4)}, {selectedLocation.longitude?.toFixed(4)}</span>
                {selectedLocation.latitude && selectedLocation.longitude && (
                  <iframe
                    title="Location map"
                    className="map-thumb"
                    src={`https://www.openstreetmap.org/export/embed.html?bbox=${selectedLocation.longitude - 0.02},${selectedLocation.latitude - 0.02},${selectedLocation.longitude + 0.02},${selectedLocation.latitude + 0.02}&amp;layer=mapnik&amp;marker=${selectedLocation.latitude},${selectedLocation.longitude}`}
                    loading="lazy"
                  />
                )}
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

        {showNewLocation && (
          <section className="section form-card add-location-form">
            <div className="section-header">
              <div>
                <p className="eyebrow">New location</p>
                <h3>Collection site</h3>
              </div>
              <Button tone="ghost" type="button" onClick={() => setShowNewLocation(false)}>Cancel</Button>
            </div>
            <div className="form-grid">
              <div className="field">
                <label>Country *</label>
                <input value={newLocation.country} onChange={(e) => setNewLocation((prev) => ({ ...prev, country: e.target.value }))} />
              </div>
              <div className="field">
                <label>County / Region</label>
                <input value={newLocation.county} onChange={(e) => setNewLocation((prev) => ({ ...prev, county: e.target.value }))} />
              </div>
              <div className="field">
                <label>Subcounty</label>
                <input value={newLocation.subcounty} onChange={(e) => setNewLocation((prev) => ({ ...prev, subcounty: e.target.value }))} />
              </div>
              <div className="field">
                <label>Site name</label>
                <input value={newLocation.site_name} onChange={(e) => setNewLocation((prev) => ({ ...prev, site_name: e.target.value }))} />
              </div>
              <div className="field field-full">
                <label>Coordinates (click on map or enter manually)</label>
                <div className="coord-inputs">
                  <input type="number" step="any" placeholder="Latitude" value={newLocation.latitude} onChange={(e) => setNewLocation((prev) => ({ ...prev, latitude: e.target.value }))} />
                  <input type="number" step="any" placeholder="Longitude" value={newLocation.longitude} onChange={(e) => setNewLocation((prev) => ({ ...prev, longitude: e.target.value }))} />
                </div>
              </div>
              <div className="field field-full">
                <MapPicker
                  latitude={mapLat}
                  longitude={mapLng}
                  onChange={(lat, lng) => {
                    setMapLat(lat);
                    setMapLng(lng);
                    setNewLocation((prev) => ({ ...prev, latitude: String(lat), longitude: String(lng) }));
                  }}
                />
              </div>
            </div>
            <div className="action-row" style={{ marginTop: 16 }}>
              <Button type="button" onClick={handleCreateLocation}>Save location</Button>
            </div>
          </section>
        )}

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
