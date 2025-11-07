import { Role } from "@/enums/enums";

export interface IUser {
	id: string
	email: string;
	role: Role
	valid: boolean
	created_at: string

	// OpenAI config
	model?: string;
	instructions?: string | null;
	user_instructions?: string | null;
	tools: string[];
}

export interface IUserShort {
	id: string
	email: string;
	role: string
	valid: boolean
	created_at: string
}

export interface IUserSelectStorage {
	user_id?: string | null;
	vs_id: string
}

export interface IUserResponse {
	user: IUser;
	token: string;
}

export interface ICreateUserRequest {
	email: string;
	password: string;
	role?: string
}

export interface ILoginRequest {
	email: string;
	password: string;
}

export interface ILoginResponse {
	access_token: string;
	token_type: string;
}

