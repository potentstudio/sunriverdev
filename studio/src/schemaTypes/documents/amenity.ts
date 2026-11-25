import {StarIcon} from '@sanity/icons'
import {defineField, defineType} from 'sanity'

/**
 * Amenity schema. Community amenities at SunRiver Firelight.
 *
 * The `status` field is load-bearing: amenities that are not yet built must be
 * marked "future" so the frontend renders them with forward-looking framing.
 * See CLAUDE.md content rules.
 */

export const amenity = defineType({
  name: 'amenity',
  title: 'Amenity',
  icon: StarIcon,
  type: 'document',
  fields: [
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
      description:
        'For future amenities, write in future tense ("The Clubhouse will offer..."). Say "members", never "residents". No em-dashes.',
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
      name: 'status',
      title: 'Status',
      type: 'string',
      initialValue: 'future',
      options: {
        list: [
          {title: 'Built', value: 'built'},
          {title: 'Future (not yet built)', value: 'future'},
        ],
        layout: 'radio',
      },
      validation: (rule) => rule.required(),
    }),
  ],
  preview: {
    select: {
      title: 'name',
      status: 'status',
      media: 'photo',
    },
    prepare({title, status, media}) {
      return {
        title,
        subtitle: status === 'future' ? 'Future amenity' : 'Built',
        media,
      }
    },
  },
})
