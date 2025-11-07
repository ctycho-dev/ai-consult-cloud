
export interface IResponse {
	status: number
	detail: string
}


export interface IChatShort {
	id: string
	name: string
	user_id: string
}


export interface IChatUpdate {
	id: string
	name: string
}

export interface IChat extends IChatShort {
}

export interface ICreateChat {
	name: string
}

export interface IChatFilesUpload {
	chatId: string
}

export interface IChatResponse {
	name: string
}

export interface ISendMessageRequest {
	chatId: string
	message: string
	company_id: string
	resend: boolean
}