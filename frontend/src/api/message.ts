import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { IMessage, IMessageCreate } from "@/interfaces/message";

export const messageApi = createApi({
    reducerPath: 'messageApi',
    baseQuery: fetchBaseQuery({
        baseUrl: `/api/v1/message`,
		// credentials: "include"
    }),
    endpoints: (builder) => ({
        getMessages: builder.query<IMessage[], string>({
            query: (chatId: string) => ({
                url: `/chat/${chatId}`,
                method: 'GET'
            }),
        }),
        getMessageById: builder.query<IMessage, string>({
            query: (companyId: string) => `/${companyId}`,
        }),
        createMessage: builder.mutation<IMessage[], IMessageCreate>({
            query: (body) => ({
                url: '/',
                method: 'POST',
                body: body,
            }),
        }),
        retryMessage: builder.mutation<void, string>({
            query: (msgId: string) => ({
                url: `/${msgId}/retry`,
                method: 'POST',
            }),
        }),
    }),
});

export const {
    useGetMessagesQuery,
    useGetMessageByIdQuery,
    useCreateMessageMutation,
    useRetryMessageMutation
} = messageApi;