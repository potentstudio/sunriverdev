import {amenity} from './documents/amenity'
import {event} from './documents/event'
import {floorPlan} from './documents/floorPlan'
import {homeListing} from './documents/homeListing'
import {page} from './documents/page'
import {post} from './documents/post'
import {amenitiesSection} from './objects/amenitiesSection'
import {callToAction} from './objects/callToAction'
import {infoSection} from './objects/infoSection'
import {settings} from './singletons/settings'
import {homePage} from './singletons/homePage'
import {link} from './objects/link'
import {blockContent} from './objects/blockContent'
import button from './objects/button'
import {blockContentTextOnly} from './objects/blockContentTextOnly'
import {simpleCta} from './objects/home/simpleCta'
import {homeBlockTypes} from './objects/home/homeBlocks'

// Export an array of all the schema types.  This is used in the Sanity Studio configuration. https://www.sanity.io/docs/studio/schema-types

export const schemaTypes = [
  // Singletons
  settings,
  homePage,
  // Documents
  page,
  post,
  event,
  floorPlan,
  amenity,
  homeListing,
  // Objects
  button,
  blockContent,
  blockContentTextOnly,
  infoSection,
  callToAction,
  amenitiesSection,
  link,
  simpleCta,
  ...homeBlockTypes,
]
