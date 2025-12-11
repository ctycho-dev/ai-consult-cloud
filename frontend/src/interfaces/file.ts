// types/file.ts

import { FileOrigin, FileState, DeleteStatus } from "@/enums/enums";

/**
 * Interface matching FastAPI's FileOut Pydantic model.
 * Keep in sync with backend.
 */
export interface IFile {
  // Core identifiers
  id: number;

  // Display/meta
  name: string | null;
  size: number | null;
  contentType: string | null;
  origin: FileOrigin;
  status: FileState;
  lastError: string | null;

  // Canonical S3
  s3Bucket: string;
  s3ObjectKey: string | null;
  s3VersionId: string | null;
  eTag: string | null;
  sha256: string | null;

  // OpenAI
  vectorStoreId: string;
  storageKey: string | null; // OpenAI file ID
  openaiS3Key: string | null; // OpenAI's internal s3_key (rarely used)

  // Deletion Tracking
  deleteStatus: DeleteStatus;
  deletedOpenAI: boolean;
  deletedS3: boolean;
  lastDeleteError: string | null;

  // Timestamps
  createdAt: string; // ISO 8601 string
}

/**
 * Upload interface (for in-progress uploads)
 */
export interface FileUpload {
  id: string;
  file: File;
  status: 'processing' | 'success' | 'error';
}


/**
 * Request payload for uploading files
 */
export interface IGlobalFileRequest {
  files: File[]; // or maybe { file: File } depending on endpoint
}

/**
 * Response from /files/download endpoint
 */
export interface IDownloadFile {
  downloadUrl: string;
}

export interface IFileStats {
  stored: number;
  indexing: number;
  indexed: number;
  upload_failed: number;
  delete_failed: number;
  deleting: number;
  total: number;
}