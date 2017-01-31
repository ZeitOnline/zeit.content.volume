(function($) {

$(document).bind('fragment-ready', function(event) {
    // Not optimal JS, cause JS might does weired stuff, if u cast Bool
    if (! Boolean($('body.type-volume.location-workingcopy').length)) {
        return;
    }
    // Check first if this Choose cover element already exists.
    if ($('#choose-cover').length > 0) {
        return;
    }
    // XXX We might want to use a more specific selector than just
    // ".column-right" and take the fieldnames into account (would have to be a
    // substring match on "fieldname-cover*", so it might be complicated).
    // Add a bold 'COVERS:' before each fieldset
    $('fieldset.column-right').first().before(
        '<fieldset class="column-right choose">' +
        '<b>COVERS:</b> <select id="choose-cover">' +
        '</select></fieldset>');

    // All fieldsets on the right (a field group added in the forms Base view)
    // get all options from  legend tag and add them as an option in dropdown.
    $('fieldset.column-right legend').each(function(i, element) {
        $('#choose-cover').append(
            '<option>' + $(element).text() + '</option>');
    });

    // verändert sich was dann rufe showfields auf und blende entsprechende
    // Elemente ein aus.
    var choose_cover = $('#choose-cover');
    choose_cover.on('change', function(event) {
        show_fieldsets(this.value);
    });
    // Am Anfang einfach ein mal triggern, um nur das DIE ZEit Element zu
    // zeigen
    choose_cover.trigger('change');
});

var show_fieldsets = function(selected_text) {
    $('fieldset.column-right').each(function(i, element) {
        element = $(this);
        if (element.hasClass('choose')) {
            return;
        }
        if (element.find('legend').first().text() == selected_text) {
            element.show();
        } else {
            element.hide();
        }
    });
};

}(jQuery));
