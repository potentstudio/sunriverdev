/**
 * Studio configuration for the SunRiver website's Sanity content (project ib6s13lu, dataset production).
 *
 * The website (the static site in this repository) reads three kinds of content from Sanity: Bucketlist Living
 * posts, floor plans and home listings. Publishing any of them rebuilds the site by itself. The other document
 * types (pages, home page, site settings, events, amenities) were made for the earlier Next.js prototype and are
 * not read by the website; they are kept so the existing documents still open, under their own group in the sidebar.
 *
 * There is no live preview here: the prototype's click-to-edit preview needed a Next.js site, and the website is
 * static. To see a change, publish it and look at the site a minute later.
 */

import {defineConfig} from 'sanity'
import {structureTool} from 'sanity/structure'
import {visionTool} from '@sanity/vision'
import {schemaTypes} from './schemaTypes'
import {structure} from './structure'
import {unsplashImageAsset} from 'sanity-plugin-asset-source-unsplash'
import {assist} from '@sanity/assist'

export type StudioConfigOptions = {
  projectId?: string
  dataset?: string
}

export function createStudioConfig({
  projectId = 'ib6s13lu',
  dataset = 'production',
}: StudioConfigOptions = {}) {
  return defineConfig({
    name: 'default',
    title: 'SunRiver Firelight',

    projectId,
    dataset,

    plugins: [
      structureTool({
        structure, // the sidebar, see ./structure
      }),
      unsplashImageAsset(),
      assist(),
      visionTool(),
    ],

    schema: {
      types: schemaTypes,
    },
  })
}
