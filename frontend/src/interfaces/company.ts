
export interface ICompany {
    id: string
	name: string;
    created_at: string
}


export interface ICreateCompanyRequest {
	name: string;
    category: string
}

export interface IUpdateCompanyRequest {
	name: string;
    category: string
}

