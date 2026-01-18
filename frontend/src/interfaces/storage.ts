import { UploadStatus } from "@/enums/enums"

export interface IStorage {
    id: string
    name: string
    vectorStoreId: UploadStatus
    default: boolean
    createdAt: string
    botId: string
    botName: string
    s3Bucket: string
}

export interface IStorageCreate {
    name: string
}

export interface IStorageUpdate {
    default: boolean
}
