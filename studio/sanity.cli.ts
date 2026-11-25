/**
 * Sanity CLI settings for the SunRiver Studio (the editing screen for the website's Sanity content).
 * `npm run deploy` publishes it to https://sunriverdev.sanity.studio
 */
import {defineCliConfig} from 'sanity/cli'

export default defineCliConfig({
  api: {
    projectId: 'ib6s13lu',
    dataset: 'production',
  },
  studioHost: 'sunriverdev',
  deployment: {
    appId: 'glfa1za49tzjhfelo28ydlk8',
    autoUpdates: true,
  },
})
