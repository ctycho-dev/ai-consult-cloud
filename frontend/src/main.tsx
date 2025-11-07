import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createTheme, MantineProvider } from '@mantine/core';
import App from './App.tsx';
import { Provider } from "react-redux";
import { store } from "./store/store.ts";

import '@mantine/core/styles.css';
import './index.css'

const theme = createTheme({
  fontFamily: 'Open Sans, sans-serif',
  primaryColor: 'cyan',
  components: {
    Button: {
      styles: {
        root: {
          background: 'oklch(21% 0.034 264.665)',
          lineHeight: '20px',
          fontWeight: 600,
          borderRadius: '8px',
          transition: 'all 0.2s ease',
          border: '0'
        },
        label: {
          padding: '0',
          color: '#fff',
        }
      },
    },
    Input: {
      styles: {
        input: {
          width: '100%',
          padding: '7px 10px',
          border: '2px solid #e8e9ef',
          borderRadius: '0.5rem',
          outline: 'none'
        },
      },
    },
    InputWrapper: {
      styles: {
        label: {
          color: 'var(--color-muted-foreground)'
        },
      },
    }
  }
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MantineProvider theme={theme} defaultColorScheme="light">
      <Provider store={store}>
        <App />
      </Provider>
    </MantineProvider>
  </StrictMode>
)
