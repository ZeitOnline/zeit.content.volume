import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.content.volume.interfaces


@grok.adapter(zeit.content.volume.interfaces.IVolume, name='teaser_text')
@grok.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLReference(context):
    node = lxml.objectify.E.volume(href=context.uniqueId)
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(node)
    return node


class VolumeReference(zeit.cms.content.reference.Reference):
    """Teaser text for Volume in reference."""
    grok.implements(zeit.content.volume.interfaces.IVolumeReference)
    grok.provides(zeit.content.volume.interfaces.IVolumeReference)
    grok.name('teaser_text')

    teaserText = zeit.cms.content.property.ObjectPathProperty('.teaserText')
