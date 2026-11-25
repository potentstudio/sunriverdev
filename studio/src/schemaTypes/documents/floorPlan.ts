import {HomeIcon} from '@sanity/icons'
import {defineField, defineType} from 'sanity'

/**
 * Floor Plan schema. One document per home floor plan offered at SunRiver Firelight.
 */

export const floorPlan = defineType({
  name: 'floorPlan',
  title: 'Floor Plan',
  icon: HomeIcon,
  type: 'document',
  fields: [
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      options: {
        source: 'name',
        maxLength: 96,
        isUnique: (value, context) => context.defaultIsUnique(value, context),
      },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'squareFootage',
      title: 'Square Footage',
      type: 'number',
      validation: (rule) => rule.positive(),
    }),
    defineField({
      name: 'bedrooms',
      title: 'Bedrooms',
      type: 'number',
      validation: (rule) => rule.positive(),
    }),
    defineField({
      name: 'bathrooms',
      title: 'Bathrooms',
      type: 'number',
      description: 'Use decimals for half baths, e.g. 2.5',
      validation: (rule) => rule.positive(),
    }),
    defineField({
      name: 'width',
      title: 'Width (feet)',
      type: 'number',
      validation: (rule) => rule.positive(),
    }),
    defineField({
      name: 'priceRange',
      title: 'Price Range',
      type: 'string',
      description:
        'Display text provided by the owner, e.g. "From the mid $400s". Do not invent pricing.',
    }),
    defineField({
      name: 'specLine',
      title: 'Spec Line',
      type: 'string',
      description: 'Verbatim spec text, e.g. "2 Bed | 2 Bath + Hobby | 2 Car Garage".',
    }),
    defineField({
      name: 'badge',
      title: 'Badge',
      type: 'string',
      description: 'Optional card badge shown on the floor plans page.',
      options: {list: ['New', 'Updated']},
    }),
    defineField({
      name: 'matterportId',
      title: 'Matterport Tour ID',
      type: 'string',
      description: 'The id after ?m= in the my.matterport.com tour URL.',
    }),
    defineField({
      name: 'planDiagram',
      title: 'Floor Plan Diagram',
      type: 'image',
      description: 'The top-down floor plan layout image.',
      fields: [{name: 'alt', type: 'string', title: 'Alternative text'}],
    }),
    defineField({
      name: 'gallery',
      title: 'Photo Gallery',
      type: 'array',
      of: [
        {
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
        },
      ],
    }),
    defineField({
      name: 'features',
      title: 'Features',
      type: 'array',
      of: [{type: 'string'}],
    }),
    defineField({
      name: 'elevationImages',
      title: 'Elevation Images',
      type: 'array',
      of: [
        {
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
        },
      ],
    }),
  ],
  preview: {
    select: {
      title: 'name',
      squareFootage: 'squareFootage',
      bedrooms: 'bedrooms',
      bathrooms: 'bathrooms',
      media: 'gallery.0',
    },
    prepare({title, squareFootage, bedrooms, bathrooms, media}) {
      const subtitle = [
        squareFootage && `${squareFootage} sq ft`,
        bedrooms != null && `${bedrooms} bed`,
        bathrooms != null && `${bathrooms} bath`,
      ]
        .filter(Boolean)
        .join(' / ')
      return {title, subtitle, media}
    },
  },
})
