import sys

def char_cmp(x, y):
    rv = cmp(x['nbits'], y['nbits'])
    if not rv:
        rv = cmp(x['bpat'], y['bpat'])
    if not rv:
        rv = cmp(x['ascii'], y['ascii'])
    return rv

characters = []

for line in sys.stdin:
    line = line.rstrip()
    obracket = line.rfind('[')
    nbits = int(line[obracket + 1:-1])

    ascii = int(line[10:13].strip())

    bar = line.find('|', 9)
    obracket = line.find('[', bar)
    bpat = line[bar + 1:obracket - 1].strip().rstrip('|')

    characters.append({'ascii': ascii, 'nbits': nbits, 'bpat': bpat})

characters.sort(cmp=char_cmp)
raw_entries = []
for c in characters:
    raw_entries.append((c['ascii'], c['bpat']))

class DefaultList(list):
    def __init__(self, default=None):
        self.__default = default

    def __ensure_size(self, sz):
        while sz > len(self):
            self.append(self.__default)

    def __getitem__(self, idx):
        self.__ensure_size(idx + 1)
        rv = super(DefaultList, self).__getitem__(idx)
        return rv

    def __setitem__(self, idx, val):
        self.__ensure_size(idx + 1)
        super(DefaultList, self).__setitem__(idx, val)

def expand_to_8bit(bstr):
    while len(bstr) < 8:
        bstr += '0'
    return int(bstr, 2)

table = DefaultList()
for r in raw_entries:
    ascii, bpat = r
    ascii = int(ascii)
    bstrs = bpat.split('|')
    curr_table = table
    while len(bstrs) > 1:
        idx = expand_to_8bit(bstrs[0])
        if curr_table[idx] is None:
            curr_table[idx] = DefaultList()
        curr_table = curr_table[idx]
        bstrs.pop(0)

    idx = expand_to_8bit(bstrs[0])
    curr_table[idx] = {'prefix_len': len(bstrs[0]),
                        'mask': int(bstrs[0], 2),
                        'value': ascii}

def make_entry_list(table, max_prefix_len):
    if max_prefix_len == 8:
        return table
    return [t for t in table if isinstance(t, dict) and t['prefix_len'] > 0]

def output_table(table, name_suffix=''):
    max_prefix_len = 0
    for i, t in enumerate(table):
        if isinstance(t, dict):
            if t['prefix_len'] > max_prefix_len:
                max_prefix_len = t['prefix_len']
        elif t is not None:
            output_table(t, '%s_%s' % (name_suffix, i))

    tablename = 'huff_incoming%s' % (name_suffix if name_suffix else '_root',)
    sys.stdout.write('static huff_table %s = {\n' % (tablename,))
    sys.stdout.write('  .prefix_len = %s,\n' % (max_prefix_len,))
    sys.stdout.write('  .entries = {\n')
    entries = make_entry_list(table, max_prefix_len)
    prefix_len = 0
    value = 0
    ptr = 'nullptr'
    for i, t in enumerate(entries):
        if isinstance(t, dict):
            prefix_len = t['prefix_len']
            value = t['value']
            ptr = 'nullptr'
        elif t is not None:
            prefix_len = 0
            value = 0
            subtable = '%s_%s' % (name_suffix, i)
            ptr = '&huff_incoming%s' % (subtable,)
        sys.stdout.write('    { .prefix_len = %s, .value = %s, .ptr = %s }' %
                         (prefix_len, value, ptr))
        if i < (len(table) - 1):
            sys.stdout.write(',')
        sys.stdout.write('\n')
    sys.stdout.write('  }\n')
    sys.stdout.write('};\n')
    sys.stdout.write('\n')

sys.stdout.write('''#ifndef mozilla__net__Http2HuffIncoming_h
#define mozilla__net__Http2HuffIncoming_h

namespace mozilla {
namespace net {

struct huff_table;

struct huff_entry {
  uint8_t prefix_len;
  uint8_t value;
  huff_table *ptr;
};

struct huff_table {
  uint8_t prefix_len;
  huff_entry *entries;
};

''')

output_table(table)

sys.stdout.write('''} // namespace net
} // namespace mozilla

#endif // mozilla__net__Http2HuffIncoming_h
''')