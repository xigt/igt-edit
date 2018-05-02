from intent.alignment.Alignment import Alignment
import json

def aln_to_json(aln, reverse=False):
    """
    :type aln: Alignment
    """
    ret_dir = {}
    if not reverse:
        for tgt in aln.all_tgt():
            ret_dir[tgt] = aln.tgt_to_src(tgt)
    else:
        for src in aln.all_src():
            ret_dir[src] = aln.src_to_tgt(src)
    return ret_dir