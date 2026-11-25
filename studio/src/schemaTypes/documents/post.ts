import {DocumentTextIcon} from '@sanity/icons'
import {format, parseISO} from 'date-fns'
import {defineField, defineType} from 'sanity'

/**
 * Blog post schema (MIGRATION_PLAN Q10). Purpose-built for the Bucketlist
 * Living blog import: author is a plain string (no person type). Slugs
 * preserve the exact indexed URLs from the old Squarespace site
 * (sunriver.com/bucketlistliving/<slug>) so no SEO links break.
 */

export const post = defineType({
  name: 'post',
  title: 'Post',
  icon: DocumentTextIcon,
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
        'For migrated posts this must match the indexed URL from the old site exactly (sunriver.com/bucketlistliving/<slug>). Generate from the title for new posts only.',
      options: {
        source: 'title',
        maxLength: 200,
        isUnique: (value, context) => context.defaultIsUnique(value, context),
      },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'publishDate',
      title: 'Publish Date',
      type: 'datetime',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'excerpt',
      title: 'Excerpt',
      type: 'text',
    }),
    defineField({
      name: 'coverImage',
      title: 'Cover Image',
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
      name: 'body',
      title: 'Body',
      type: 'blockContent',
    }),
    defineField({
      name: 'author',
      title: 'Author',
      type: 'string',
    }),
    defineField({
      name: 'categories',
      title: 'Categories',
      type: 'array',
      of: [{type: 'string'}],
      options: {layout: 'tags'},
      description:
        'Must match the old site category names exactly (e.g. "Clubs & Groups", "Sunriver Boys") so /bucketlistliving/category/<name> URLs keep working.',
    }),
    defineField({
      name: 'tags',
      title: 'Tags',
      type: 'array',
      of: [{type: 'string'}],
      options: {layout: 'tags'},
      description:
        'Must match the old site tag names exactly (e.g. "Kayla V.", "St. George Happenings") so /bucketlistliving/tag/<name> URLs keep working.',
    }),
  ],
  preview: {
    select: {
      title: 'title',
      publishDate: 'publishDate',
      media: 'coverImage',
    },
    prepare({title, publishDate, media}) {
      return {
        title,
        subtitle: publishDate ? format(parseISO(publishDate), 'LLL d, yyyy') : undefined,
        media,
      }
    },
  },
})
