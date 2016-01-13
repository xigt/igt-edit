/**
 * Created by rgeorgi on 12/3/15.
 */

function tt(selector, content, hideOnClick) {
    if (typeof hideOnClick === 'undefined') {hideOnClick = false;}

    $(selector).each(function (i, el) {
       if (!$(el).hasClass('tooltip-f')) {
           $(selector).tooltip({
              content:content
           });
           if (hideOnClick) {
               $(selector).click(function(){
                   $(this).tooltip('hide');
               });
           }
       }
    });
}

function assign_tooltips() {
    /*  */
    tt('#rating-green', "I am confident that this IGT is clean.", true);
    tt('#rating-yellow', "I am not confident that this IGT is clean.", true);
    tt('#rating-red', "I am confident that this IGT is unclean.", true);

    tt('#glm', "Does the gloss line have the same number of morphs as the language line?");
    tt('#glw', "Does the gloss line have the same number of whitespace-separated tokens as the language line?");
    tt('#tag', "Does the normalized tier have any lines other than L, G, T?");
    tt('#col', "Are the tokens of the Language and Gloss line arranged using whitespace such that every token of one line is contained by another?");

    hoverIconTooltips();
}

function labelTooltips() {
    tt('.labelspan-AC', "Author Name or Citation");
    tt('.labelspan-DB', "Double Column");
    tt('.labelspan-CN', "Linguistic Construction");
    tt('.labelspan-CR', "Corruption");
    tt('.labelspan-LN', "Language Name");
    tt('.labelspan-SY', "Syntax Information");
    tt('.labelspan-LT', "Literal Translation");
    tt('.labelspan-AL', "Alternative L/G/T");
    tt('.labelspan-EX', "Extra");
}

function hoverIconTooltips() {
    tt('.undo', "Restore the tier to its initial state.");
    tt('.delete', "Mark this tier for deletion, or remove if empty. Click again to undelete.", true);
    tt('.add', "Add a blank new line beneath this line.");
}