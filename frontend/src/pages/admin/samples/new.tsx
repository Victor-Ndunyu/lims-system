import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/router";

import { AdminLayout, Alert, Button, StatusBadge } from "../../../components/ui";
import { createSample, fetchStaffLookups } from "../../../lib/api";
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
  const router = useRouter();

  useEffect(() => {
    fetchStaffLookups()
      .then((data) => setLookups(data))
      .catch((err) => setError(err.message));
  }, []);

  const handleChange = (field: keyof SampleFormData, value: string | AttachmentInput[]) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleAttachmentChange = (index: number, field: keyof AttachmentInput, value: string) => {
    setForm((current) => {
      const attachments = [...current.attachments];
      attachments[index] = { ...attachments[index], [field]: value };
      return { ...current, attachments };
    });
  };

  const addAttachment = () => {
    setForm((current) => ({
      ...current,
      attachments: [...current.attachments, { file_name: "", file_type: "", file_url: "" }],
    }));
  };

  const removeAttachment = (index: number) => {
    setForm((current) => ({
      ...current,
      attachments: current.attachments.filter((_, i) => i !== index),
    }));
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
            <select id="location" value={form.location_id} onChange={(event) => handleChange("location_id", event.target.value)}>
              <option value="">Select location</option>
              {lookups.locations.map((location) => (
                <option key={location.id} value={location.id}>
                  {location.site_name || `${location.country} / ${location.county || ""}`}
                </option>
              ))}
            </select>
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
            <Button tone="secondary" onClick={addAttachment}>
              Add attachment
            </Button>
          </div>
          <div className="record-list">
            {form.attachments.map((attachment, index) => (
              <div className="card" key={index}>
                <div className="form-grid">
                  <div className="field">
                    <label>File name</label>
                    <input value={attachment.file_name} onChange={(event) => handleAttachmentChange(index, "file_name", event.target.value)} />
                  </div>
                  <div className="field">
                    <label>File type</label>
                    <input value={attachment.file_type} onChange={(event) => handleAttachmentChange(index, "file_type", event.target.value)} />
                  </div>
                  <div className="field field-full">
                    <label>File URL</label>
                    <input value={attachment.file_url} onChange={(event) => handleAttachmentChange(index, "file_url", event.target.value)} />
                  </div>
                </div>
                <div style={{ marginTop: 16 }}>
                  <Button tone="ghost" onClick={() => removeAttachment(index)}>
                    Remove attachment
                  </Button>
                </div>
              </div>
            ))}
          </div>
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
