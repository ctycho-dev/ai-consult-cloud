import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ISettingsState {
  isSettingsOpen: boolean;
}

const initialState: ISettingsState = {
  isSettingsOpen: false,
};


const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    toggleSettings: (state) => {
      state.isSettingsOpen = !state.isSettingsOpen;
    },
    setSettingsOpen: (state, action: PayloadAction<boolean>) => {
      state.isSettingsOpen = action.payload;
    },
  },
  selectors: {
    selectIsSettingsOpen: (state) => state.isSettingsOpen,
  },
});


export const { toggleSettings, setSettingsOpen } = settingsSlice.actions;
export const { selectIsSettingsOpen } = settingsSlice.selectors;

export default settingsSlice.reducer;