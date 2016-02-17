/**
 * Created by rgeorgi on 2/16/16.
 */

$(document).keydown(function(e) {
    $selectedInput = $('.line-input:focus');
    if ($selectedInput) {
        var pos = $selectedInput.caret();
        var upDown = false;
        switch (e.which) {
            case 38: //up
                $prevRow  = $selectedInput.closest('tr').prev('.textrow');
                $prevLine = $prevRow.find('.line-input');
                $prevLine.focus();
                $prevLine.caret(pos);
                upDown = true;
                break;
            case 40: //down
                $nextRow = $selectedInput.closest('tr').next('.textrow');
                $nextLine = $nextRow.find('.line-input');
                $nextLine.focus();
                upDown = true;
                break;
        }
        if (upDown) {
            setTimeout(function () {
                $selectedInput = $('.line-input:focus');
                $selectedInput.caret(pos);
            }, 5);
        }

    }

});

// Set caret position easily in jQuery
// Written by and Copyright of Luke Morton, 2011
// Licensed under MIT
(function ($) {
    // Behind the scenes method deals with browser
    // idiosyncrasies and such
    $.caretTo = function (el, index) {
        if (el.createTextRange) {
            var range = el.createTextRange();
            range.move("character", index);
            range.select();
        } else if (el.selectionStart != null) {
            el.focus();
            el.setSelectionRange(index, index);
        }
    };

    // Another behind the scenes that collects the
    // current caret position for an element

    // TODO: Get working with Opera
    $.caretPos = function (el) {
        if ("selection" in document) {
            var range = el.createTextRange();
            try {
                range.setEndPoint("EndToStart", document.selection.createRange());
            } catch (e) {
                // Catch IE failure here, return 0 like
                // other browsers
                return 0;
            }
            return range.text.length;
        } else if (el.selectionStart != null) {
            return el.selectionStart;
        }
    };

    // The following methods are queued under fx for more
    // flexibility when combining with $.fn.delay() and
    // jQuery effects.

    // Set caret to a particular index
    $.fn.caret = function (index, offset) {
        if (typeof(index) === "undefined") {
            return $.caretPos(this.get(0));
        }

        return this.queue(function (next) {
            if (isNaN(index)) {
                var i = $(this).val().indexOf(index);

                if (offset === true) {
                    i += index.length;
                } else if (typeof(offset) !== "undefined") {
                    i += offset;
                }

                $.caretTo(this, i);
            } else {
                $.caretTo(this, index);
            }

            next();
        });
    };

    // Set caret to beginning of an element
    $.fn.caretToStart = function () {
        return this.caret(0);
    };

    // Set caret to the end of an element
    $.fn.caretToEnd = function () {
        return this.queue(function (next) {
            $.caretTo(this, $(this).val().length);
            next();
        });
    };
}(jQuery));

function setCaretToPos (input, pos) {
  setSelectionRange(input, pos, pos);
}