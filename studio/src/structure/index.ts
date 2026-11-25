import {
  CalendarIcon,
  CogIcon,
  ComposeIcon,
  DocumentsIcon,
  HomeIcon,
  PinIcon,
  StarIcon,
} from '@sanity/icons'
import type {StructureBuilder, StructureResolver} from 'sanity/structure'

/**
 * Structure builder is useful whenever you want to control how documents are grouped and
 * listed in the studio or for adding additional in-studio previews or content to documents.
 * Learn more: https://www.sanity.io/docs/structure-builder-introduction
 */

const DISABLED_TYPES = ['settings', 'homePage', 'assist.instruction.context']

// Types given an explicit position in the sidebar below
const ORDERED_TYPES = ['page', 'post', 'event', 'floorPlan', 'homeListing', 'amenity']

export const structure: StructureResolver = (S: StructureBuilder) =>
  S.list()
    .title('Website Content')
    .items([
      // What the website reads. Publishing any of these rebuilds the site.
      S.documentTypeListItem('post').title('Bucketlist Living').icon(ComposeIcon),
      S.documentTypeListItem('floorPlan').title('Floor Plans').icon(HomeIcon),
      S.documentTypeListItem('homeListing').title('Homes for Sale (photos and videos)').icon(PinIcon),
      S.divider(),
      // Made for the earlier prototype. The website does not read these.
      S.listItem()
        .title('Not used by the website')
        .icon(DocumentsIcon)
        .child(
          S.list()
            .title('Not used by the website')
            .items([
              S.listItem()
                .title('Home Page')
                .child(S.document().schemaType('homePage').documentId('homePage'))
                .icon(HomeIcon),
              S.listItem()
                .title('Site Settings')
                .child(S.document().schemaType('settings').documentId('siteSettings'))
                .icon(CogIcon),
              S.documentTypeListItem('page').title('Pages').icon(DocumentsIcon),
              S.documentTypeListItem('event').title('Events').icon(CalendarIcon),
              S.documentTypeListItem('amenity').title('Amenities').icon(StarIcon),
            ]),
        ),
      // Future document types that are not placed above still show up here
      // instead of silently disappearing from the sidebar.
      ...S.documentTypeListItems().filter(
        (listItem) => ![...ORDERED_TYPES, ...DISABLED_TYPES].includes(listItem.getId() as string),
      ),
    ])
