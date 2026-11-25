import {StarIcon} from '@sanity/icons'
import {defineField, defineType} from 'sanity'

/**
 * Amenities Section object. A page builder block that displays a set of
 * amenities. The frontend automatically renders amenities whose status is
 * "future" with forward-looking framing.
 */

export const amenitiesSection = defineType({
  name: 'amenitiesSection',
  title: 'Amenities Section',
  type: 'object',
  icon: StarIcon,
  fields: [
    defineField({
      name: 'heading',
      title: 'Heading',
      type: 'string',
    }),
    defineField({
      name: 'amenities',
      title: 'Amenities',
      type: 'array',
      of: [{type: 'reference', to: [{type: 'amenity'}]}],
      validation: (rule) => rule.required().min(1),
    }),
  ],
  preview: {
    select: {
      title: 'heading',
    },
    prepare({title}) {
      return {
        title: title || 'Amenities Section',
        subtitle: 'Amenities',
      }
    },
  },
})
