import { UploadStatus } from "@/enums/enums"

export interface IStorage {
    id: string
    name: string
    vector_store_id: UploadStatus
    default: boolean
    created_at: string
}

export interface IStorageCreate {
    name: string
}

export interface IStorageUpdate {
    default: boolean
}
