import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import {
    IUser,
    ICreateUserRequest,
    ILoginRequest,
    ILoginResponse,
    IUserSelectStorage
} from "../interfaces/user";

export const userApi = createApi({
    reducerPath: 'userApi',
    baseQuery: fetchBaseQuery({
        baseUrl: `/api/v1/user`,
        // credentials: "include"
    }),
    endpoints: (builder) => ({

        getUsers: builder.query<IUser[], void>({
            query: () => ({
                url: '/',
                method: 'GET'
            }),
        }),

        getUserById: builder.query<IUser, string>({
            query: (userId: string) => `/${userId}`,
        }),
        createUser: builder.mutation<IUser, ICreateUserRequest>({
            query: (body) => ({
                url: '/',
                method: 'POST',
                body: body,
            }),
        }),
        selectStorage: builder.mutation<IUser, IUserSelectStorage>({
            query: (body) => ({
                url: `/${body.vs_id}/select`,
                method: 'POST',
                body: body,
            }),
        }),
        loginUser: builder.mutation<ILoginResponse, ILoginRequest>({
            query: (body) => {
                const formData = new FormData();

                formData.append('username', body.email);
                formData.append('password', body.password);

                return {
                    url: '/login',
                    method: 'POST',
                    body: formData
                };
            },
        }),
        logoutUser: builder.mutation<any, void>({
            query: () => ({
                url: '/logout',
                method: 'POST'
            }),
        }),
        verifyUser: builder.mutation<IUser, void>({
            query: () => ({
                url: '/verify',
                method: 'POST'
            }),
        }),
        deleteUser: builder.mutation<void, string>({
            query: (fileId) => ({
                url: `/${fileId}`,
                method: "DELETE",
            }),
        }),
    }),
});

export const {
    useGetUsersQuery,
    useGetUserByIdQuery,
    useCreateUserMutation,
    useSelectStorageMutation,
    useLoginUserMutation,
    useLogoutUserMutation,
    useVerifyUserMutation,
    useDeleteUserMutation
} = userApi;