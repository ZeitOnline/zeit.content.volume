import zeit.content.volume.interfaces
import zeit.cms.content.interfaces
import lxml.objectify
import grokcore.component as grok


@grok.adapter(zeit.content.volume.interfaces.IVolume, name='teaser_text')
@grok.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLTeaserTextReference(context):
    node = lxml.objectify.E.volume(href=context.uniqueId)
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(node)
    return node


class VolumeTeaserTextReference(zeit.cms.content.reference.Reference):
    """Teaser text for Volume in reference."""
    grok.implements(zeit.content.volume.interfaces.IVolumeTeaserTextReference)
    grok.provides(zeit.content.volume.interfaces.IVolumeTeaserTextReference)
    grok.name('teaser_text')

    teaser_text = zeit.cms.content.property.ObjectPathProperty('.teaser_text')
