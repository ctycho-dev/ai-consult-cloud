export enum Role {
  ADMIN = "admin",
  USER = "user",
  ASSISTANT = "assistant",
}

export enum MessageStates {
  CREATED = "created",
  PROCESSING = "processing",
  FINISHED = "finished",
  TIMEOUT = "timeout",
  CANCELED = "canceled",
  ERROR = "error",
}

export enum UploadStatus {
  PROCESSING = "processing",
  SUCCESS = "success",
  ERROR = "error",
}

// enums/enums.ts

/**
 * Where a file came from.
 */
export enum FileOrigin {
  UPLOAD = "upload",
  S3_IMPORT = "s3_import",
  OPENAI_ONLY = "openai_only",
}

/**
 * Lifecycle states of a file in the storage/indexing pipeline.
 *
 * DB-first flow:
 * 1. PENDING    – DB row created, nothing stored yet
 * 2. UPLOADING  – Uploading to canonical S3
 * 3. STORED     – Canonical S3 upload done, before OpenAI handoff
 * 4. INDEXING   – File accepted by OpenAI, vectors building
 * 5. INDEXED    – Ready in OpenAI vector store
 * 6. FAILED     – Terminal error, check `last_error`
 */
export enum FileState {
  PENDING = "pending",
  UPLOADING = "uploading",
  STORED = "stored",
  INDEXING = "indexing",
  INDEXED = "indexed",
  DELETING = "deleting",
  UPLOAD_FAILED = "upload_failed",
  DELETE_FAILED = "delete_failed",
}

/**
 * Status of deletion process.
 * Used to support retryable, resumable cleanup across distributed systems.
 */
export enum DeleteStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  FAILED = "failed",
  COMPLETED = "completed",
}
