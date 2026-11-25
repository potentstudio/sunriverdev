import {defineArrayMember, defineField, defineType} from 'sanity'
import {
  ClockIcon,
  EnvelopeIcon,
  HeartIcon,
  HomeIcon,
  ImageIcon,
  ImagesIcon,
  UsersIcon,
} from '@sanity/icons'

/**
 * Homepage sections as page builder blocks (owner request 2026-10-10: edit
 * the designed pages by hand). Each block mirrors one section of the Figma
 * "Home Clark PLAY" homepage; the frontend keeps the section's layout and
 * falls back to the design's own copy and photos for any field left empty,
 * so a block can be added with nothing filled in and still look finished.
 *
 * Multi-paragraph copy uses plain text fields: a blank line starts a new
 * paragraph.
 */

const paragraphs = (name: string, title: string, rows = 6) =>
  defineField({
    name,
    title,
    type: 'text',
    rows,
    description: 'Leave a blank line between paragraphs.',
  })

const photo = (name: string, title: string, description?: string) =>
  defineField({
    name,
    title,
    type: 'image',
    options: {hotspot: true},
    description,
    fields: [{name: 'alt', type: 'string', title: 'Alternative text'}],
  })

export const homeHero = defineType({
  name: 'homeHero',
  title: 'Home: Hero',
  type: 'object',
  icon: ImageIcon,
  fields: [
    defineField({name: 'heading', title: 'Heading', type: 'string'}),
    defineField({name: 'cta', title: 'Button', type: 'simpleCta'}),
    // Field keeps its original name ("poster") from the video version of
    // the hero so existing documents still work.
    photo('poster', 'Photo', 'Full-width photo behind the headline.'),
  ],
  preview: {
    select: {title: 'heading', media: 'poster'},
    prepare: ({title, media}) => ({title: title || 'Hero', subtitle: 'Home: Hero', media}),
  },
})

export const homeRetirementBand = defineType({
  name: 'homeRetirementBand',
  title: 'Home: Blue story band',
  type: 'object',
  icon: HeartIcon,
  fields: [
    defineField({name: 'heading', title: 'Heading', type: 'string'}),
    paragraphs('body', 'Copy (optional)'),
    defineField({name: 'cta', title: 'Button', type: 'simpleCta'}),
    photo('photo', 'Cutout photo', 'A photo with a transparent background works best.'),
  ],
  preview: {
    select: {title: 'heading', media: 'photo'},
    prepare: ({title, media}) => ({title: title || 'Blue story band', subtitle: 'Home: Blue story band', media}),
  },
})

export const homeMeansMoreCard = defineType({
  name: 'homeMeansMoreCard',
  title: 'Card',
  type: 'object',
  fields: [
    defineField({name: 'label', title: 'Label', type: 'string', description: 'e.g. Live In'}),
    paragraphs('body', 'Copy', 5),
    photo('icon', 'Icon', 'Small yellow icon; leave empty to keep the design icon.'),
    defineField({name: 'cta', title: 'Button', type: 'simpleCta'}),
  ],
  preview: {
    select: {title: 'label', subtitle: 'body', media: 'icon'},
  },
})

export const homeMeansMore = defineType({
  name: 'homeMeansMore',
  title: 'Home: Live In / Live Out / Live On',
  type: 'object',
  icon: UsersIcon,
  fields: [
    defineField({name: 'chip', title: 'Chip', type: 'string', description: 'e.g. #LiveYoung'}),
    defineField({name: 'headingAccent', title: 'Heading, yellow part', type: 'string', description: 'e.g. "Here, it"'}),
    defineField({name: 'headingMain', title: 'Heading, blue part', type: 'string', description: 'e.g. "means more."'}),
    defineField({
      name: 'cards',
      title: 'Cards',
      type: 'array',
      of: [defineArrayMember({type: 'homeMeansMoreCard'})],
      validation: (rule) => rule.max(3),
    }),
  ],
  preview: {
    select: {accent: 'headingAccent', main: 'headingMain'},
    prepare: ({accent, main}) => ({
      title: [accent, main].filter(Boolean).join(' ') || 'Live In / Live Out / Live On',
      subtitle: 'Home: Live In / Live Out / Live On',
    }),
  },
})

export const homePhotoBand = defineType({
  name: 'homePhotoBand',
  title: 'Home: Photo band',
  type: 'object',
  icon: ImageIcon,
  fields: [
    defineField({name: 'textBefore', title: 'Text (regular)', type: 'string', description: 'e.g. YOUR'}),
    defineField({name: 'textBold', title: 'Text (bold)', type: 'string', description: 'e.g. NEW LIFESTYLE'}),
    defineField({name: 'textAfter', title: 'Text after (regular)', type: 'string', description: 'e.g. AWAITS'}),
    photo('image', 'Background photo'),
  ],
  preview: {
    select: {a: 'textBefore', b: 'textBold', c: 'textAfter', media: 'image'},
    prepare: ({a, b, c, media}) => ({
      title: [a, b, c].filter(Boolean).join(' ') || 'Photo band',
      subtitle: 'Home: Photo band',
      media,
    }),
  },
})

export const homeTrackRecord = defineType({
  name: 'homeTrackRecord',
  title: 'Home: Track record collage',
  type: 'object',
  icon: ImagesIcon,
  fields: [
    defineField({name: 'heading', title: 'Heading', type: 'string'}),
    paragraphs('body', 'Copy'),
    defineField({name: 'kicker', title: 'Closing line (yellow)', type: 'string'}),
    photo('photoWide', 'Wide photo (hikers)'),
    photo('photoFrame1', 'Framed tall photo (pickleball)'),
    photo('photoTall', 'Tall photo (bikes)'),
    photo('photoFrame2', 'Framed small photo (yoga)'),
  ],
  preview: {
    select: {title: 'heading', media: 'photoWide'},
    prepare: ({title, media}) => ({title: title || 'Track record collage', subtitle: 'Home: Track record collage', media}),
  },
})

export const homeFloorPlanBand = defineType({
  name: 'homeFloorPlanBand',
  title: 'Home: Floor plan band',
  type: 'object',
  icon: HomeIcon,
  fields: [
    defineField({name: 'heading', title: 'Heading', type: 'string'}),
    defineField({
      name: 'floorPlans',
      title: 'Featured floor plans',
      type: 'array',
      of: [defineArrayMember({type: 'reference', to: [{type: 'floorPlan'}]})],
      description: 'Leave empty to show the three smallest plans.',
      validation: (rule) => rule.max(3),
    }),
    defineField({name: 'ctaText', title: 'Button text', type: 'string', description: 'Links to /floor-plans'}),
  ],
  preview: {
    select: {title: 'heading'},
    prepare: ({title}) => ({title: title || 'Floor plan band', subtitle: 'Home: Floor plan band'}),
  },
})

export const homeTimelineStep = defineType({
  name: 'homeTimelineStep',
  title: 'Step',
  type: 'object',
  fields: [
    defineField({name: 'title', title: 'Title', type: 'string'}),
    defineField({name: 'body', title: 'Copy', type: 'text', rows: 2}),
  ],
  preview: {select: {title: 'title', subtitle: 'body'}},
})

export const homeTimeline = defineType({
  name: 'homeTimeline',
  title: 'Home: Where you begin (timeline)',
  type: 'object',
  icon: ClockIcon,
  fields: [
    defineField({name: 'heading', title: 'Heading', type: 'string'}),
    defineField({
      name: 'steps',
      title: 'Steps',
      type: 'array',
      of: [defineArrayMember({type: 'homeTimelineStep'})],
    }),
    defineField({name: 'cta', title: 'Button', type: 'simpleCta'}),
    photo('backgroundImage', 'Background photo', 'Shown under a blue wash.'),
  ],
  preview: {
    select: {title: 'heading', media: 'backgroundImage'},
    prepare: ({title, media}) => ({title: title || 'Where you begin', subtitle: 'Home: Where you begin (timeline)', media}),
  },
})

export const homeLeadForm = defineType({
  name: 'homeLeadForm',
  title: 'Home: Lead form band',
  type: 'object',
  icon: EnvelopeIcon,
  fields: [
    defineField({name: 'heading', title: 'Heading', type: 'string'}),
    paragraphs('body', 'Copy', 3),
    defineField({
      name: 'form',
      title: 'HubSpot form',
      type: 'string',
      options: {
        list: [
          {title: 'Find a Home (interest form)', value: 'findAHome'},
          {title: 'Contact', value: 'contact'},
        ],
        layout: 'radio',
      },
      initialValue: 'findAHome',
    }),
    defineField({
      name: 'variant',
      title: 'Colour',
      type: 'string',
      options: {
        list: [
          {title: 'Sun Yellow', value: 'yellow'},
          {title: 'SunRiver Blue', value: 'blue'},
        ],
        layout: 'radio',
      },
      initialValue: 'yellow',
    }),
  ],
  preview: {
    select: {title: 'heading', variant: 'variant'},
    prepare: ({title, variant}) => ({
      title: title || 'Lead form band',
      subtitle: `Home: Lead form band (${variant === 'blue' ? 'blue' : 'yellow'})`,
    }),
  },
})

export const homeBlockTypes = [
  homeHero,
  homeRetirementBand,
  homeMeansMoreCard,
  homeMeansMore,
  homePhotoBand,
  homeTrackRecord,
  homeFloorPlanBand,
  homeTimelineStep,
  homeTimeline,
  homeLeadForm,
]

/** Block type names offered in page builders. */
export const HOME_BLOCK_NAMES = [
  'homeHero',
  'homeRetirementBand',
  'homeMeansMore',
  'homePhotoBand',
  'homeTrackRecord',
  'homeFloorPlanBand',
  'homeTimeline',
  'homeLeadForm',
] as const
