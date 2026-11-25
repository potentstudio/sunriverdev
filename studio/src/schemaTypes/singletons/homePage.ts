import {defineArrayMember, defineField, defineType} from 'sanity'
import {HomeIcon} from '@sanity/icons'

import {HOME_BLOCK_NAMES} from '../objects/home/homeBlocks'

/**
 * The homepage as a single editable document (id "homePage"): a stack of
 * page builder blocks. When this document has no blocks the site renders the
 * designed homepage from code, so it can never go blank.
 */
export const homePage = defineType({
  name: 'homePage',
  title: 'Home Page',
  type: 'document',
  icon: HomeIcon,
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      description: 'Internal name; the browser tab title comes from Site Settings.',
      initialValue: 'Home',
    }),
    defineField({
      name: 'pageBuilder',
      title: 'Sections',
      type: 'array',
      of: [
        ...HOME_BLOCK_NAMES.map((name) => defineArrayMember({type: name})),
        defineArrayMember({type: 'callToAction'}),
        defineArrayMember({type: 'infoSection'}),
        defineArrayMember({type: 'amenitiesSection'}),
      ],
      options: {
        insertMenu: {
          views: [
            {name: 'list'},
            {
              name: 'grid',
              previewImageUrl: (schemaTypeName) =>
                `/static/page-builder-thumbnails/${schemaTypeName}.webp`,
            },
          ],
        },
      },
    }),
  ],
  preview: {
    prepare: () => ({title: 'Home Page'}),
  },
})
