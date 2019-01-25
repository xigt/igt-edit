/**
 * Created by rgeorgi on 1/20/17.
 */
function wIdNum(obj) {
    var myId = cssId(obj);
    return idNum(myId);
}

function itemType(obj) {
    var idRegex = /([^0-9]+)/;
    return idRegex.exec(cssId(obj))[1];
}

function cssId(obj) {
    return $(obj).attr('id');
}

function idNum(s) {
    var idRegex = /([0-9]+)/;
    return parseInt(idRegex.exec(s)[1])
}

function isItemType(obj, t) { return itemType(obj) == t;}
function isGw(obj) {return isItemType(obj, 'gw');}
function isTw(obj) {return isItemType(obj, 'tw');}
function isLw(obj) {return isItemType(obj, 'w');}
function isGm(obj) {return isItemType(obj, 'g');}
function isLm(obj) {return isItemType(obj, 'm');}


/* HIGHLIGHTING FOR HOVER */

function highlight(obj) {
    highlight_helper(obj, true);
}

function unhighlight(obj) {
    highlight_helper(obj, false);
}

function getAln(arr, myId, myIdx) {
    // console.log('Pairing "'+myId+'" with idx='+myIdx+' in arr '+arr.toString());
    var retArr = [];
    var otherIdx = myIdx == 0 ? 1 : 0;
    for (i=0; i<arr.length; i++) {
        var eltId = arr[i][myIdx];
        var oId = arr[i][otherIdx];
        if (eltId == myId)
            retArr.push(oId);
    }
    return retArr;
}

function getTwGmAln(myId, myIdx) {
    return getAln(tw_gm_aln, myId, myIdx);
}

function getGmLmAln(myId, myIdx) {
    return getAln(gm_lm_aln, myId, myIdx);
}

// -------------------------------------------
// COLORS FOR ALIGNMENTS
// -------------------------------------------

SELF_COLOR = 'tomato';

ALN_COLOR = 'DeepSkyBlue'; // For elements an elt is aligned with directly
REL_COLOR = 'PowderBlue'; // For elements aligned with a related element

SUB_COLOR = 'lightsalmon'; // For elements subsumed by this element
SUP_COLOR = 'lightgreen'; // For parents of this element

function highlightList(arr, color, entering) {
    color = entering ? color : 'white';
    idArr = arr.map(function(s){return '#'+s;});
    // console.log('Highlighting "' + arr.join(',') +'" with ' + color);
    $(idArr.join(',')).css('background-color', color);
}

function highlight_helper(obj, entering) {
    var myNum = wIdNum(obj);
    var myId = cssId(obj);

    // If we are in alignment mode, add a
    // border, then halt
    if (alignClicked) {
        if (obj == alignClicked) {return} // don't alter the item already clicked
        if (entering) var border = 'solid pink';
        else var border = 'solid white';
        $(obj).css('border', border);
        return
    }


    var rels = [];
    var subs = [];
    var sups = [];
    var alns = [];

    if (isGw(obj)) {
        // SUB: gm, REL: m, ALN: w, tw
        var myGms = childMorphs(myId); subs = subs.concat(myGms);
        var alnHash = glossWordLookup(myId);
        alns = alns.concat(alnHash["tw"]); // Add translation words
        subs = subs.concat(alnHash["lm"]); // Add lang morphemes
        alns = alns.concat(alnHash["lw"]); // Add lang words
    } else if (isGm(obj)) {
        var myGw = parentWord(myId); sups = sups.concat([myGw]);
        var myTws = getTwGmAln(myId, 1); alns = alns.concat(myTws);
        var myLms = getGmLmAln(myId, 0); alns = alns.concat(myLms);
        var myLws = parentWords(myLms); sups = sups.concat(myLws);
    } else if (isTw(obj)) {
        // ALN: Gw, Lw REL: Gm
        var alnHash = transWordLookup(myId);
        sups = sups.concat(alnHash["gw"]);
        alns = alns.concat(alnHash["gm"]);
        sups = sups.concat(alnHash["lw"]);
        subs = subs.concat(alnHash["lm"]);
    } else if (isLw(obj)) {
        var alnHash = langWordLookup(myId);
        subs.push(alnHash["lm"]);
        subs = subs.concat(alnHash["lm"]);
        alns = alns.concat(alnHash["gw"]);
        subs = subs.concat(alnHash["gm"]);
        alns = alns.concat(alnHash["tw"]);
    } else if (isLm(obj)) {
        var alnHash = langMorphLookup(myId);
        sups = sups.concat(alnHash["lw"]);
        alns = alns.concat(alnHash["gm"]);
        sups = sups.concat(alnHash["gw"]);
        alns = alns.concat(alnHash["tw"]);
    }

    highlightList(rels, REL_COLOR, entering);
    highlightList(subs, SUB_COLOR, entering);
    highlightList(sups, SUP_COLOR, entering);
    highlightList(alns, ALN_COLOR, entering);
    highlightList([myId], SELF_COLOR, entering);
}


function childMorphs(myId) {return $('#'+myId).attr('childMorphs').split(',');}
function parentWord(mId) {return $('#'+mId).attr('parentWord');}
function parentWords(mArr){return mArr.map(function(mId){return parentWord(mId)});}

// Get the lang word(s) which are aligned
// with
function glossWordLookup(myId) {
    var alnHash = {"lw":[], "lm":[], "tw":[]};
    var gMArr = childMorphs(myId);
    for (gmIdx=0; gmIdx<gMArr.length;gmIdx++) {
        var gM = gMArr[gmIdx];
        var tWArr = getTwGmAln(gM, 1);
        alnHash["tw"] = tWArr;
        var lMArr = getGmLmAln(gM, 0);
        for (lmIdx = 0; lmIdx < lMArr.length; lmIdx++) {
            var lMId = lMArr[lmIdx];
            alnHash["lm"].push(lMId);
            alnHash["lw"].push(parentWord(lMId));
        }
    }
    return alnHash;
}

function langMorphLookup(myId) {
    var alnHash={"lw":[], "gw":[], "gm":[], "tw":[]};
    alnHash["lw"] = parentWord(myId);
    var gmArr = getGmLmAln(myId, 1);
    for (gmIdx=0; gmIdx<gmArr.length; gmIdx++){
        var gM = gmArr[gmIdx];
        alnHash["gm"].push(gM);
        alnHash["gw"].push(parentWord(gM));
        var twArr = getTwGmAln(gM, 1);
        for (twIdx=0;twIdx<twArr.length;twIdx++) {
            var tW = twArr[twIdx];
            alnHash["tw"].push(tW);
        }
    }
    return alnHash;
}

// Get the gloss words that dominate the gloss morphs
// to which this translation word is aligned
function transWordLookup(myId) {
    alnHash = {"lw":[],"lm":[],"gw":[],"gm":[]};
    var alnMorphArr = getTwGmAln(myId, 0);
    for (mIdx=0;mIdx<alnMorphArr.length;mIdx++) {
        var gMId = alnMorphArr[mIdx];
        alnHash["gm"].push(gMId);
        alnHash["gw"].push(parentWord(gMId));
        var lMArr = getGmLmAln(gMId, 0);
        for (lmIdx=0;lmIdx<lMArr.length;lmIdx++) {
            var lMId = lMArr[lmIdx];
            alnHash["lm"].push(lMId);
            alnHash["lw"].push(parentWord(lMId));
        }
    }
    return alnHash;
}

function langWordLookup(myId) {
    var alnHash = {"tw":[], "lm":[], "gw":[], "gm":[]}
    var lmArr = childMorphs(myId); alnHash["lm"] = lmArr;
    for (lmIdx=0;lmIdx<lmArr.length;lmIdx++) {
        var lM = lmArr[lmIdx];
        var gmArr = getGmLmAln(lM, 1);
        for (gmIdx=0;gmIdx<gmArr.length; gmIdx++) {
            var gM = gmArr[gmIdx];
            alnHash["gm"].push(gM);
            alnHash["gw"].push(parentWord(gM));
            var twArr = getTwGmAln(gM, 1);
            for (twIdx=0; twIdx<twArr.length;twIdx++) {
                var tW = twArr[twIdx];
                alnHash["tw"].push(tW);
            }
        }
    }
    return alnHash;
}

// Tell whether or not the word types are the
function similarType(me, other) {
    var myWT = itemType(me);
    var oWT = itemType(other);
    function isLWT(o) {return (itemType(o) == 'w' || itemType(o) == 'gw')}

    return ((myWT == 'tw' && oWT == 'tw') ||
    (isLWT(me) && isLWT(other)))
}

// -------------------------------------
// Add/undo alignments when clicked...
// -------------------------------------
function startAlign(obj) {
    // If we have already clicked an alignment,
    // we need to either add or remove this item


    if (alignClicked) {
        // we would like to cancel the operation without
        // doing anything if another word of the same
        // type is clicked.

        var myWT = itemType(obj);
        var oWT = itemType(alignClicked);

        console.log('Last click: ' + myWT + ' - Previous click: '+ oWT);

        // Logic for selecting a match:
        // 1) LWs can link to GWs or GMs
        // 2) LMs can link to GWs or GMs
        // 3) GWs can link to LWs, LMs or TWs
        // 4) GMs can link to LWs, LMs, or TWs
        // 5) TWs can link to GWs or GMs
        // *) When selecting GW/LW, should act as if all GMs/LMs dominated by
        //    that word are selected.


        if (similarType(obj, alignClicked))
            {stopAlign(obj);}

        // Otherwise, we should handle the request
        // for adding or removing alignment.
        else {
            // Blink three times to indicate this is
            // the one being selected
            count = 0;
            blinkOn = false;
            intervalId = setInterval(function () {
                if (blinkOn) {
                    blinkOn = false;
                    $(obj).css('border', 'solid white');
                } else {
                    blinkOn = true;
                    $(obj).css('border', 'solid red');
                }
                count++;
                if (count == 7) {
                    blinkOn = false;
                    $(obj).css('border', 'solid white');
                    clearInterval(intervalId);
                    addAlign(obj);
                    stopAlign(obj);
                }
            }, 100);
        }

        // And no matter what's clicked, we should
        // exit the alignment mode.

    } else {
        $(obj).css('border', 'solid red');

        alignClicked = obj;
    }
}

// Stop being in adding alignment mode
function stopAlign(obj) {
    $(alignClicked).css('border', 'solid white');
    $(obj).css('border', 'solid white');
    alignClicked = false;

    $('.alignable-word').each(function(i, elt){
       unhighlight(elt);
    });
    highlight(obj);
}

function toggleArr(srcId, tgtId) {
    // This should be regularized such that
    // "src" is always trans_word
    // and "tgt" is always a gloss morph

    for (i=0;i<tw_gm_aln.length;i++) {
        // Remove an alignment that is already stored,
        // and exit
        if (tw_gm_aln[i][0] == srcId && tw_gm_aln[i][1] == tgtId) {
            tw_gm_aln.splice(i, 1);
            console.log("Removing " + srcId + "," + tgtId + " from tw_gm alignments");
            return
        }
    }
    // Otherwise, if the alignment wasn't already there,
    // add it.
    console.log("Adding " + srcId + "," + tgtId + " to tw_gm alignments");
    tw_gm_aln.push([srcId, tgtId]);
}

function addAlign(lastClickedObj) {
    var lastClickedObjId = cssId(lastClickedObj);
    var firstClickedObjId = cssId(alignClicked);

    // function toLw(idStr) {return 'w' + idNum(idStr).toString();}
    // function toTw(idStr) {return 'tw'+ idNum(idStr).toString();}
    //

    console.log('Attempting to align "'+lastClickedObjId+'" to "'+firstClickedObjId+'"');
    // return

    if (isTw(lastClickedObj)) {
        tgtId = firstClickedObjId;
        srcId = lastClickedObjId; // Make sure to regularize
    } else {
        tgtId = lastClickedObjId;
        srcId = firstClickedObjId;
    }

    toggleArr(srcId, tgtId);
}