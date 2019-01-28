# Step 1: IGT Verification
Start by verifying that what is in the editor:
- Is, in fact, an instance of IGT
- Is in the language that it is supposed to be

If it is not, reject the instance with the red icon and click "Submit Instance"

![reject](/Users/rgeorgi/Documents/code/yggdrasil/doc/images/reject.png)


# Step 2: IGT Cleaning
If the IGT has been verified, click "Generate Cleaned tier."

The cleaned tier is meant for fixing whitespace and linebreak errors. For instance:

    L       (2) coka       paye=as                          kusu ne yak ci=Ø=yeG
    G  CR       we.EXCL go.PL=1PL.EXCL.S.                   intentionCOP IN.Q 1PL.       EXCL.S.TR=3.O=say
    G  CR                                   INTR
    T          `We said that we should go.'

* The `INTR` token is split onto a separate line, where it should be the last gram of the `go.PL=1PL.EXCL.S.` gloss. 
* `intention` and the copula particle `COP` are missing a space between the tokens
* There is an extra space between `1PL.` and `EXCL.S.TR=3.O=say`

These whitespace errors should be fixed on the cleaning tier to produce an instance that looks like:

    (2) coka    paye=as                kusu      ne  yak  ci=Ø=ye
        we.EXCL go.PL=1PL.EXCL.S.INTR  intention COP IN.Q 1PL.EXCL.S.TR=3.O=say
        `We said that we should go.'

You may wish to use the "Download PDF Source" to view the instance in the original PDF document to see what its format should be.

If you are unsure what the original author's intention was, click the yellow icon and submit the instance here.

![unsure](/Users/rgeorgi/Documents/code/yggdrasil/doc/images/unsure.png)

# Step 3: Normalized Tier

The normalized tier is meant to be the last text stage prior to automatic processing. Check that the normalized tier has the following properties

## All Content (L,G,T) Lines

- Ensure any metadata (Author Citation, explanation of phenomenon, etc) is placed on its own line, and given the `M` line tag.
- Any single utterances that span multiple lines should be combined to one line
- If there is any syntactic annotation inline with the language line (such as bracketing):
  - Create a separate line that is cleaned of the syntactic annotations and label that the "L/G/T" line
  - Leave the original "L/G/T" line intact, but change its label to "M" and choose the correct flags to describe what annotaiton is present

## Language Line

- Remove any numbering: `(i), 1.`, etc.
- If there is a judgment on the language or gloss line (`*` for ungrammatical/unattested, or `?` for unclear, make sure it appears in the "Judgment" box, not on the line itself)

## Gloss Line

* Remove any punctuation (commas, quotation marks, sentence-final-periods)

## Translation Line

- Remove quotation marks

# Step 4: "Group 2" Tiers

With the normalized tier in the correct format, you should be able to click the "Analyze Normalized Tier" button to auto-generate:

- Word tokenization
- POS Tags
- Word Alignment

This step will require the most linguistic intuition. 

## Alignment

Generally speaking, words should be aligned if they are, or contain, an exact analog to the English word on the translation line, and a minimal number of words to express that concept.

Things to look out for in alignment are

- Gloss abbreviations mapping to words
  - "*the*" or "*a*" on the translation line might be instead indicated with "**DET**" in the gloss. 
- Conceptual Rephrasing
  - **YES:**
    - The "is" in "*there is*" and "*exists*" in a gloss line should be aligned, since these are 	communicating the same existential concept
    - "*eat*-CAUS" should align "*eat*" with a similar verb in English, and **CAUS** with "*make*", since again, the causative is analagous to the "make" in English.
  - **NO:**
    - In a gloss "*sail.PST*" with translation "*sailed*" — only "*sailed*–*sail*" should be aligned. The inflection should be left unaligned.