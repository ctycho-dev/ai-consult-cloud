import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { ICompany, ICreateCompanyRequest, IUpdateCompanyRequest } from "../interfaces/company";

export const companyApi = createApi({
    reducerPath: 'companyApi',
    baseQuery: fetchBaseQuery({
        baseUrl: `/api/companies`,
		// credentials: "include"
    }),
    endpoints: (builder) => ({
        getCompanies: builder.query<ICompany[], void>({
            query: () => ({
                url: '/',
                method: 'GET'
            }),
        }),
        getCompanyById: builder.query<ICompany, string>({
            query: (companyId: string) => `/${companyId}`,
        }),
        createCompany: builder.mutation<ICompany, ICreateCompanyRequest>({
            query: (body) => ({
                url: '/',
                method: 'POST',
                body: body,
            }),
        }),
        updateCompany: builder.mutation<ICompany, { id: string; data: IUpdateCompanyRequest }>({
            query: ({ id, data }) => ({
                url: `/${id}`,
                method: 'PUT',
                body: data,
            }),
        }),
        deleteCompany: builder.mutation<void, string>({
            query: (companyId: string) => ({
                url: `/${companyId}`,
                method: 'DELETE',
            }),
        }),
    }),
});

export const {
    useGetCompaniesQuery,
    useGetCompanyByIdQuery,
    useCreateCompanyMutation,
    useUpdateCompanyMutation,
    useDeleteCompanyMutation,
} = companyApi;