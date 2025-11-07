export interface ISource {
  file_id: number
  file_name: string | null
  page: number | null
}



export interface IMessage {
    id: string
    chat_id: string
    content: string
    sources: ISource[] | null
    state: string
    role: string
    created_at: Date
}

export interface IMessageCreate {
    content: string
    chat_id: string
}