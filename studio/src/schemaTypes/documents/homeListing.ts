import {HomeIcon} from '@sanity/icons'
import {defineField, defineType} from 'sanity'

/**
 * A home currently for sale, shown on the /homes-for-sale page (2026 Figma
 * design "Homes for Sale Filter Simple"). The filter sidebar filters on
 * community, status, square footage, beds, baths, garage, and hobby rooms.
 */
export const homeListing = defineType({
  name: 'homeListing',
  title: 'Home Listing',
  icon: HomeIcon,
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      description: 'Usually the floor plan name, e.g. "Elmwood" or "Single Family".',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      description: 'The listing detail page URL: /homes-for-sale/<slug>.',
      options: {source: 'title'},
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'community',
      title: 'Community',
      type: 'string',
      options: {
        list: ['SunRiver Firelight', 'SunRiver Villas', 'SunRiver St George'],
        layout: 'radio',
      },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'status',
      title: 'Status',
      type: 'string',
      options: {
        list: ['Move in Ready', 'For Sale', 'Under Contract', 'Sold'],
        layout: 'radio',
      },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'statusDate',
      title: 'Status date',
      type: 'date',
      description:
        'The day the home went under contract or sold. Under-contract and sold homes stay on the Homes for Sale page for two months after this date, then drop out of the default view (visitors can still tick that status in the filter).',
      hidden: ({parent}) => parent?.status !== 'Sold' && parent?.status !== 'Under Contract',
    }),
    defineField({
      name: 'price',
      title: 'Price (USD)',
      type: 'number',
      description:
        'For SunRiver Firelight homes, the total from the Move-In Ready Homes price sheet (base price plus design upgrades).',
    }),
    defineField({
      name: 'askForPricing',
      title: 'Show "Ask for pricing" instead of the price',
      type: 'boolean',
      description:
        'For featured homes. The price stays stored (it keeps the listing sorted) but visitors see "Ask for pricing".',
      initialValue: false,
    }),
    defineField({
      name: 'squareFootage',
      title: 'Square Footage',
      type: 'number',
    }),
    defineField({
      name: 'beds',
      title: 'Bedrooms',
      type: 'number',
    }),
    defineField({
      name: 'baths',
      title: 'Bathrooms',
      type: 'number',
    }),
    defineField({
      name: 'garageSpaces',
      title: 'Garage Spaces',
      type: 'number',
      description: 'Half spaces are fine, e.g. 2.5.',
    }),
    defineField({
      name: 'hobbyRooms',
      title: 'Hobby Rooms',
      type: 'number',
    }),
    defineField({
      name: 'address',
      title: 'Address',
      type: 'string',
      description: 'e.g. "182 S Cottonwood Dr, Toquerville, UT"',
    }),
    defineField({
      name: 'mlsNumber',
      title: 'MLS Number',
      type: 'string',
      description: 'For internal reference; not shown on the site.',
    }),
    defineField({
      name: 'youtubeShortIds',
      title: 'YouTube video IDs',
      type: 'array',
      description:
        'IDs of YouTube Shorts or videos touring this home, e.g. "Fp6ru4PMd_k" from youtube.com/shorts/Fp6ru4PMd_k. Each one is shown as a video tour on the listing page, in this order.',
      of: [
        {
          type: 'string',
          validation: (rule) =>
            rule.regex(/^[A-Za-z0-9_-]{11}$/, {name: 'YouTube video ID', invert: false}),
        },
      ],
    }),
    defineField({
      name: 'photo',
      title: 'Photo',
      type: 'image',
      options: {hotspot: true},
      fields: [
        {
          name: 'alt',
          type: 'string',
          title: 'Alternative text',
          description: 'Important for SEO and accessibility.',
        },
      ],
    }),
    defineField({
      name: 'gallery',
      title: 'Photo Gallery',
      type: 'array',
      description: 'Additional photos shown on the listing detail page.',
      of: [
        {
          type: 'image',
          options: {hotspot: true},
          fields: [
            {
              name: 'alt',
              type: 'string',
              title: 'Alternative text',
            },
          ],
        },
      ],
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
      rows: 6,
      description: 'Listing description shown on the detail page.',
    }),
    defineField({
      name: 'descriptionHeading',
      title: 'Description Heading',
      type: 'string',
      description: 'e.g. "Single Family Home in Toquerville". Shown above the description.',
    }),
    defineField({
      name: 'isNew',
      title: 'Show "NEW" badge',
      type: 'boolean',
      initialValue: false,
    }),
  ],
  preview: {
    select: {
      title: 'title',
      address: 'address',
      price: 'price',
      media: 'photo',
    },
    prepare({title, address, price, media}) {
      const priceLabel = typeof price === 'number' ? `$${price.toLocaleString('en-US')}` : null
      return {
        title,
        subtitle: [priceLabel, address].filter(Boolean).join(' · ') || undefined,
        media,
      }
    },
  },
})
