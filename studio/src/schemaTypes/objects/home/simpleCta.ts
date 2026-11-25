import {defineField, defineType} from 'sanity'
import {LinkIcon} from '@sanity/icons'

/**
 * A button with a plain destination: a site path such as "/floor-plans" or a
 * full URL. Used by the homepage blocks, where every call to action points at
 * a known page.
 */
export const simpleCta = defineType({
  name: 'simpleCta',
  title: 'Button',
  type: 'object',
  icon: LinkIcon,
  fields: [
    defineField({
      name: 'text',
      title: 'Button text',
      type: 'string',
    }),
    defineField({
      name: 'href',
      title: 'Destination',
      type: 'string',
      description: 'A page on this site, e.g. /floor-plans or /contact-us, or a full https:// URL.',
      validation: (rule) =>
        rule.custom((value) =>
          !value || /^(\/|https?:\/\/|mailto:|tel:)/.test(value)
            ? true
            : 'Start with / for a page on this site, or with https://',
        ),
    }),
  ],
  options: {collapsible: true, collapsed: false},
})
