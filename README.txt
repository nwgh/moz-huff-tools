These are tools to create huffman coding tables for use in Gecko's HTTP/2
HPACK implementation. It's pretty simple:

python make_incoming_tables.py < huff_incoming.txt > Http2HuffIncoming.h
python make_outgoing_tables.py < huff_outgoing.txt > Http2HuffOutgoing.h

huff_incoming.txt and huff_outgoing.txt are copy/pasted from the HPACK spec,
with irrelevant lines removed.

Current revision in repo: HPACK draft04
