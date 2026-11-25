import {CalendarIcon} from '@sanity/icons'
import {format, parseISO} from 'date-fns'
import {defineField, defineType} from 'sanity'

/**
 * Calendar event. Covers the old site's /calendar/<slug> URLs. Only title and
 * slug are required so SEO stub documents can exist before real content
 * arrives; eventDate stays empty until the real date is known (never guessed).
 */
export const event = defineType({
  name: 'event',
  title: 'Event',
  icon: CalendarIcon,
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      description:
        'Must match the indexed URL from the old site exactly (sunriver.com/calendar/<slug>).',
      options: {
        source: 'title',
        maxLength: 200,
        isUnique: (value, context) => context.defaultIsUnique(value, context),
      },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'eventDate',
      title: 'Event Date',
      type: 'datetime',
      description: 'Leave empty if the real date is unknown. Never guess.',
    }),
    defineField({
      name: 'location',
      title: 'Location',
      type: 'string',
    }),
    defineField({
      name: 'excerpt',
      title: 'Excerpt',
      type: 'text',
    }),
    defineField({
      name: 'body',
      title: 'Body',
      type: 'blockContent',
    }),
  ],
  preview: {
    select: {
      title: 'title',
      eventDate: 'eventDate',
    },
    prepare({title, eventDate}) {
      return {
        title,
        subtitle: eventDate ? format(parseISO(eventDate), 'LLL d, yyyy') : '[no date]',
      }
    },
  },
})
