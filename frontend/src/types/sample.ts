export interface AttachmentInput {
  file_name: string;
  file_type: string;
  file_url: string;
}

export interface SampleFormData {
  sample_code: string;
  sample_type_id: string;
  collection_date: string;
  collector_id: string;
  location_id: string;
  description: string;
  remarks: string;
  status: string;
  attachments: AttachmentInput[];
}

export interface SampleRow {
  id: string;
  sample_code: string;
  status: string;
  verification_status: string;
  public_visibility: boolean;
  collection_date: string;
  collector_id: string | null;
  location_id: string | null;
  description?: string | null;
  remarks?: string | null;
  attachments?: AttachmentInput[];
}

export interface LookupItem {
  id: string;
  name?: string;
  full_name?: string;
  country?: string;
  county?: string;
  subcounty?: string;
  site_name?: string;
}
