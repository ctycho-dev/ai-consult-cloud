import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { IStorage, IStorageCreate, IStorageUpdate } from "@/interfaces/storage";

export const storageApi = createApi({
    reducerPath: 'storageApi',
    baseQuery: fetchBaseQuery({
        baseUrl: `/api/v1/storage`,
		// credentials: "include"
    }),
    endpoints: (builder) => ({
        getStorages: builder.query<IStorage[], void>({
            query: () => ({
                url: '/',
                method: 'GET'
            }),
        }),
        getStorageById: builder.query<IStorage, string>({
            query: (companyId: string) => `/${companyId}`,
        }),
        createStorage: builder.mutation<IStorage, IStorageCreate>({
            query: (body) => ({
                url: '/',
                method: 'POST',
                body: body,
            }),
        }),
        updateStorage: builder.mutation<IStorage, { id: string; data: IStorageUpdate }>({
            query: ({ id, data }) => ({
                url: `/${id}`,
                method: 'PATCH',
                body: data,
            }),
        }),
        deleteStorage: builder.mutation<void, string>({
            query: (storageId: string) => ({
                url: `/${storageId}`,
                method: 'DELETE',
            }),
        }),
    }),
});

export const {
    useGetStoragesQuery,
    useGetStorageByIdQuery,
    useCreateStorageMutation,
    useUpdateStorageMutation,
    useDeleteStorageMutation,
} = storageApi;