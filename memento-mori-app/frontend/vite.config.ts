import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Replace USER/REPO below: base should be "/REPO/" when deployed to Pages
export default defineConfig({
  plugins: [vue()],
  base: process.env.GITHUB_PAGES ? '/<REPO_NAME>/' : '/',
})