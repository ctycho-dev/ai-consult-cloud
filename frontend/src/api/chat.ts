import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { IChat, IChatShort, IChatUpdate, ICreateChat } from "@/interfaces/chat";

export const chatApi = createApi({
    reducerPath: 'chatApi',
    baseQuery: fetchBaseQuery({
        baseUrl: `/api/v1/chat`,
		// credentials: "include"
    }),
    endpoints: (builder) => ({
        getChats: builder.query<IChatShort[], void>({
            query: () => ({
                url: '/',
                method: 'GET'
            }),
        }),
        getChatsByUser: builder.query<IChatShort[], void>({
            query: () => ({
                url: '/user',
                method: 'GET'
            }),
        }),
        getChatById: builder.query<IChat, string>({
            query: (companyId: string) => `/${companyId}`,
        }),
        createChat: builder.mutation<IChat, ICreateChat>({
            query: (body) => ({
                url: '/',
                method: 'POST',
                body: body,
            }),
        }),
        updateChat: builder.mutation<IChat, { id: string; data: IChatUpdate }>({
            query: ({ id, data }) => ({
                url: `/${id}`,
                method: 'PUT',
                body: data,
            }),
        }),
        deleteChat: builder.mutation<void, string>({
            query: (companyId: string) => ({
                url: `/${companyId}`,
                method: 'DELETE',
            }),
        }),
    }),
});

export const {
    useGetChatsQuery,
    useGetChatsByUserQuery,
    useGetChatByIdQuery,
    useCreateChatMutation,
    useUpdateChatMutation,
    useDeleteChatMutation,
} = chatApi;