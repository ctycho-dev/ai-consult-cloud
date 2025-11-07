// src/features/workspaces/workspacesSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { IChat, IChatShort } from '@/interfaces/chat';
import { chatApi } from '@/api/chat';

interface WorkspacesState {
    chats: IChatShort[];
    currentChat: IChat | null;
    isLoading: boolean;
    error: string | null;
}

const initialState: WorkspacesState = {
    chats: [],
    currentChat: null,
    isLoading: false,
    error: null,
};

const chatSlice = createSlice({
    name: 'chats',
    initialState,
    reducers: {
        setCurrentWorkspace: (state, action: PayloadAction<IChat | null>) => {
            state.currentChat = action.payload;
        },
        clearWorkspaces: () => initialState,
    },
    extraReducers: (builder) => {
        // Get workspaces
        builder.addMatcher(
            chatApi.endpoints.getChats.matchPending,
            (state) => {
                state.isLoading = true;
                state.error = null;
            }
        );
        builder.addMatcher(
            chatApi.endpoints.getChats.matchFulfilled,
            (state, action: PayloadAction<IChatShort[]>) => {
                state.isLoading = false;
                state.chats = action.payload;
            }
        );
        builder.addMatcher(
            chatApi.endpoints.getChats.matchRejected,
            (state, action) => {
                state.isLoading = false;
                state.error = action.error.message || 'Failed to load workspaces';
            }
        );

        // Get single workspace
        builder.addMatcher(
            chatApi.endpoints.getChats.matchPending,
            (state) => {
                state.isLoading = true;
                state.error = null;
            }
        );
        builder.addMatcher(
            chatApi.endpoints.getChatsByUser.matchFulfilled,
            (state, action: PayloadAction<IChatShort[]>) => {
                state.isLoading = false;
                state.chats = action.payload;
            }
        );
        builder.addMatcher(
            chatApi.endpoints.getChats.matchFulfilled,
            (state, action: PayloadAction<IChatShort>) => {
                state.isLoading = false;
                state.currentChat = action.payload;
            }
        );
        builder.addMatcher(
            chatApi.endpoints.getChats.matchRejected,
            (state, action) => {
                state.isLoading = false;
                state.error = action.error.message || 'Failed to load workspace';
            }
        );

        // Create workspace
        builder.addMatcher(
            chatApi.endpoints.createChat.matchFulfilled,
            (state, action: PayloadAction<IChat>) => {
                state.chats.push({
                    id: action.payload.id,
                    name: action.payload.name,
                    user_id: action.payload.user_id
                });
                state.currentChat = action.payload;
            }
        );

        // Delete workspace
        builder.addMatcher(
            chatApi.endpoints.deleteChat.matchFulfilled,
            (state, action) => {
                const chatId = action.meta.arg.originalArgs;
                state.chats = state.chats.filter(ws => ws.id !== chatId);
                if (state.currentChat?.id === chatId) {
                    state.currentChat = null;
                }
            }
        );

        // Update workspace
        builder.addMatcher(
            chatApi.endpoints.updateChat.matchFulfilled,
            (state, action) => {
                const { id, name } = action.meta.arg.originalArgs;
                const chat = state.chats.find(ws => ws.id === id);
                if (chat) {
                    chat.name = name;
                }
                if (state.currentChat?.id === id) {
                    state.currentChat.name = name;
                }
            }
        );
    },
});

export const { setCurrentWorkspace, clearWorkspaces } = chatSlice.actions;
export default chatSlice.reducer;