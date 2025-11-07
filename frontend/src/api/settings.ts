import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { ISettings } from '../interfaces/settings'


export const settingsApi = createApi({
    reducerPath: "settingsApi",
    baseQuery: fetchBaseQuery({
        baseUrl: `/api/settings`,
		// credentials: "include"
    }),
    endpoints: (builder) => ({
        /**
         * Fetches the current settings from the server.
         * @returns {ISettings} The settings object.
         */
        getSettings: builder.query<ISettings, void>({
            query: () => "",
        }),
        /**
        * Creates new settings on the server.
        * @param {ISettings} settings - The settings object to create.
        */
        createSettings: builder.mutation<void, ISettings>({
            query: (settings) => ({
                url: "",
                method: "POST",
                body: settings,
            }),
        }),
    }),
});

export const {
    useGetSettingsQuery,
    useCreateSettingsMutation,
} = settingsApi;
