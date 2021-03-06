import sys

sys.stdout.write('''/*
 * THIS FILE IS AUTO-GENERATED. DO NOT EDIT!
 */
#ifndef mozilla__net__Http2HuffmanOutgoing_h
#define mozilla__net__Http2HuffmanOutging_h

namespace mozilla {
namespace net {

struct HuffmanOutgoingEntry {
  uint8_t mLength;
  uint32_t mValue;
};

static HuffmanOutgoingEntry HuffmanOutgoing[] = {
''')

entries = []
for line in sys.stdin:
    line = line.strip()
    obracket = line.rfind('[')
    nbits = int(line[obracket + 1:-1])

    encend = obracket - 1
    hexits = nbits / 4
    if hexits * 4 != nbits:
        hexits += 1

    enc = line[encend - hexits:encend]
    val = int(enc, 16)

    entries.append({'length': nbits, 'value': val})

line = []
for i, e in enumerate(entries):
    sys.stdout.write('  { %s, 0x%08x }' %
                     (e['length'], e['value']))
    if i < (len(entries) - 1):
        sys.stdout.write(',')
    sys.stdout.write('\n')

sys.stdout.write('''};

} // namespace net
} // namespace mozilla

#endif // mozilla__net__Http2HuffmanOutgoing_h
''')

