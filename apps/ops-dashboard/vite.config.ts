import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@stadiumos/shared': path.resolve(__dirname, '../../../libs/shared'),
      '@stadiumos/schemas': path.resolve(__dirname, '../../../libs/schemas'),
      '@stadiumos/components': path.resolve(__dirname, '../../../libs/components'),
      '@/': path.resolve(__dirname, './src/'),
    },
  },
  server: {
    port: 3000,
    host: true,
  },
});
