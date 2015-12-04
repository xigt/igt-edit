/**
 * Created by rgeorgi on 12/3/15.
 */

/* Go ahead and store the clean lines, so that they can
 * be restored if needed. */
function stashLines(rowClass) {
    $(rowClass).each(function(i, elt) {
        id = $(elt).attr('id');
        textval = $(elt).find('.line-input').val();
        localStorage.setItem(id, textval);
    });
}

function stashCleanLines() {
    stashLines('.cleanrow');
}

function stashNormLines() {
    stashLines('.normalrow');
}

