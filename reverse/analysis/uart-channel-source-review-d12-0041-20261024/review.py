"""D12 focused read-only source review; no ROM reads or SDK-wide searches."""
from pathlib import Path
import json
import re

ROOT = Path('D:/Documents/PlatformIO/Projects/bouffalo_sdk/drivers/lhal/src')
OUT = Path(__file__).resolve().parent
checks = []
anchors = []

def expect(label, condition):
    assert condition, label
    checks.append(label)

def function(file, name):
    text = (ROOT / file).read_text(encoding='utf-8')
    match = re.search(r'^(void|bool) ' + name + r'\([^\n]*\)\n\{', text, re.M)
    assert match, name
    opening = text.index('{', match.start())
    depth = 1
    cursor = opening + 1
    while depth:
        depth += (text[cursor] == '{') - (text[cursor] == '}')
        cursor += 1
    anchors.append({'file': file, 'function': name,
                    'start': text.count('\n', 0, match.start()) + 1,
                    'closing_brace': text.count('\n', 0, cursor - 1) + 1})
    return text[opening + 1:cursor - 1]

uart = [function('bflb_uart.c', n) for n in ['bflb_uart_deinit', 'bflb_uart_disable']]
deinit = function('bflb_dma.c', 'bflb_dma_channel_deinit')
stop = function('bflb_dma.c', 'bflb_dma_channel_stop')
busy = function('bflb_dma.c', 'bflb_dma_channel_isbusy')
detach = function('bflb_dma.c', 'bflb_dma_channel_irq_detach')
mask = function('bflb_dma.c', 'bflb_dma_channel_tcint_mask')
for name, body in zip(['uart_deinit', 'uart_disable'], uart):
    expect(name + ': non-ROMAPI TX/RX clear', all(t in body for t in [
        'tx_cfg &= ~UART_CR_UTX_EN;', 'rx_cfg &= ~UART_CR_URX_EN;']))
    expect(name + ': no direct DMA operation', 'bflb_dma_' not in body)
expect('DMA deinit direct non-ROMAPI callees are stop then mask',
       re.findall(r'\b(bflb_\w+)\(', deinit) == ['bflb_dma_channel_stop', 'bflb_dma_channel_tcint_mask'])
expect('stop is enable-bit clear', 'regval &= ~DMA_E;' in stop)
expect('isbusy reads configuration bit zero', 'if (regval & (1 << 0))' in busy)
expect('detach clears handler then arg then masks',
       detach.index('.handler = NULL;') < detach.index('.arg = NULL;') < detach.index('bflb_dma_channel_tcint_mask(dev, true);'))
expect('detach has no direct free call', not re.search(r'\b\w*free\s*\(', detach))
expect('mask visible implementation touches ITC bit',
       'regval |= DMA_ITC;' in mask and 'regval &= ~DMA_ITC;' in mask)
expect('mask has no callback table or direct free/detach',
       'dma_callback' not in mask and not re.search(r'\b\w*(?:free|detach)\s*\(', mask))
expect('ROMAPI alternatives remain visible for six delegated functions',
       all('#ifdef romapi_' in b for b in uart + [deinit, stop, busy, mask]))
result = {'task': 'D12', 'checks': checks, 'check_count': len(checks),
          'source_anchors': anchors, 'rom_bytes_reread': 0,
          'sdk_wide_searches': 0, 'new_rom_functionality': 0,
          'whole_library_exclusions': 0,
          'scope': 'Seven named functions in two source files only; no macro expansion or ROMAPI machine-code certification'}
(OUT / 'review-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'checks': len(checks), 'focused_functions': len(anchors), 'rom_bytes_reread': 0}))
