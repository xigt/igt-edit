/**
 * Created by rgeorgi on 12/3/15.
 */

function assign_tooltips() {
    /*  */
    $('#rating-green').tooltip({
        content:"I am confident that this IGT is clean."
    });

    $('#rating-yellow').tooltip({
       content : "I am not confident that this IGT is clean."
    });

    $('#rating-red').tooltip({
       content : "I am confident that this IGT is unclean."
    });

    $('#glm').tooltip({
        content: "Does the gloss line have the same number of morphs as the language line?"
    });
    $('#glw').tooltip({
        content: "Does the gloss line have the same number of whitespace-separated tokens as the language line?"
    });
    $('#tag').tooltip({
        content: "Does the normalized tier have any lines other than L, G, T?"
    });
    $('#col').tooltip({
       content: "Are the tokens of the Language and Gloss line arranged using whitespace such that every token of one line is contained by another?"
    });

    $('.undo').tooltip({
        content: "Undelete the tier"
    });
}