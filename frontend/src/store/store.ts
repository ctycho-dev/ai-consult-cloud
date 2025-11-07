import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit'
import { settingsApi } from "@/api/settings.ts";
import { fileApi } from "@/api/file";
import { chatApi } from "@/api/chat";
import { storageApi } from "@/api/storage";
import { messageApi } from "@/api/message";
import { userApi } from "@/api/user.ts";
import { companyApi } from "@/api/company.ts";
import { setupListeners } from "@reduxjs/toolkit/query";
import settingsReducer from '@/store/settingsSlice'
// import userReducer from '@/store/userSlice'
import chatReducer from '@/store/chatSlice'

export const store = configureStore({
	reducer: {
		// user: userReducer,
		chats: chatReducer,
		settings: settingsReducer,
		[settingsApi.reducerPath]: settingsApi.reducer,
		[chatApi.reducerPath]: chatApi.reducer,
		[storageApi.reducerPath]: storageApi.reducer,
		[messageApi.reducerPath]: messageApi.reducer,
		[fileApi.reducerPath]: fileApi.reducer,
		[userApi.reducerPath]: userApi.reducer,
		[companyApi.reducerPath]: companyApi.reducer,
	},
	middleware: (getDefaultMiddleware) =>
		getDefaultMiddleware().concat(
			settingsApi.middleware,
			chatApi.middleware,
			storageApi.middleware,
			messageApi.middleware,
			fileApi.middleware,
			userApi.middleware,
			companyApi.middleware,
		),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
export type AppStore = typeof store
export type AppThunk<ThunkReturnType = void> = ThunkAction<
	ThunkReturnType,
	RootState,
	unknown,
	Action
>

setupListeners(store.dispatch)

