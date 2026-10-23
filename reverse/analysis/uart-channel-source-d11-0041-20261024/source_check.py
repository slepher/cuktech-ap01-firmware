"""Read-only bounded candidate-source check. No ROM export, build or execution."""
from pathlib import Path
import json,re,subprocess
ROOT=Path('D:/Documents/PlatformIO/Projects/bouffalo_sdk')
OUT=Path(__file__).resolve().parent
checks=[]
def check(label, ok):
    assert ok,label
    checks.append(label)
def body(rel,name):
    text=(ROOT/rel).read_text(encoding='utf-8')
    m=re.search(r'^(?:void|bool|int) '+re.escape(name)+r'\([^\n]*\)\n\{',text,re.M)
    assert m,name
    start=m.end(); end=text.index('\n}',start)
    return text[start:end],text[:m.start()].count('\n')+1,text[:end].count('\n')+1
rows=[]
for rel,name,required,forbidden in [
 ('drivers/lhal/src/bflb_uart.c','bflb_uart_deinit',['tx_cfg &= ~UART_CR_UTX_EN;','rx_cfg &= ~UART_CR_URX_EN;'],['bflb_dma_channel_stop','bflb_dma_channel_irq_detach','0x0f']),
 ('drivers/lhal/src/bflb_uart.c','bflb_uart_disable',['tx_cfg &= ~UART_CR_UTX_EN;','rx_cfg &= ~UART_CR_URX_EN;'],['bflb_dma_channel_stop','bflb_dma_channel_irq_detach','0x0f']),
 ('drivers/lhal/src/bflb_dma.c','bflb_dma_channel_deinit',['bflb_dma_channel_stop(dev);','bflb_dma_channel_tcint_mask(dev, true);'],['bflb_dma_channel_irq_detach','free(','0x0f']),
 ('drivers/lhal/src/bflb_dma.c','bflb_dma_channel_stop',['channel_base = dev->reg_base;','regval &= ~DMA_E;'],['dma_callback','free(']),
 ('drivers/lhal/src/bflb_dma.c','bflb_dma_channel_isbusy',['regval = getreg32(channel_base + DMA_CxCONFIG_OFFSET);','if (regval & (1 << 0))'],['nxsem_','nxmutex_']),
 ('drivers/lhal/src/bflb_dma.c','bflb_dma_channel_irq_detach',['dma_callback[dev->idx][dev->sub_idx].handler = NULL;','dma_callback[dev->idx][dev->sub_idx].arg = NULL;','bflb_dma_channel_tcint_mask(dev, true);'],['free(']),
]:
    b,lo,hi=body(rel,name)
    for token in required:check(name+' contains '+token,token in b)
    for token in forbidden:check(name+' excludes '+token,token not in b)
    if name=='bflb_dma_channel_deinit':check('deinit stop before mask',b.index(required[0])<b.index(required[1]))
    rows.append(dict(path=rel,function=name,lines=[lo,hi],conditional='romapi branch delegated where present; non-romapi body compared'))
patterns=[r'(?i)uart_shutdown|bl[a-z0-9_]*_shutdown',r'(?i)dma_channel_(alloc|free|release)|dma.*channel.*(alloc|free)',r'(?i)g_dmach|dmachannel|nxsem_|nxmutex_']
search=[]
for pat in patterns:
    r=subprocess.run(['rg','-n','--glob','*.[ch]',pat,'.'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    check('bounded C/H search no hit: '+pat,r.returncode==1 and not r.stdout and not r.stderr)
    search.append(dict(pattern=pat,scope='rg default visible C/H files; respects ignore/hidden defaults; no binary/archive/history search',hits=0))
report=Path('reverse/reports/ap01/uart-dma-channel-review-d10-0041-20261023.md').read_text(encoding='utf-8')
for token in ['a01b5c48','a00198bc','0x0f','9900','992e','9942']:
    check('inherited D10 anchor '+token,token in report)
result=dict(task='D11',rom_bytes_reread=0,new_rom_functionality=0,certified_whole_library_exclusions=0,candidate_identity='Inherited D07/D08: HEAD 41bf338a57be53919d99f6c6715a96100428c97d, VERSION 2.3.36; not re-certified here',source_anchors=rows,searches=search,checks=checks,check_count=len(checks),limitations=['No matching NuttX allocation/release/shutdown source identified within bounded candidate C/H search','No claim that absent symbol proves absent compiled implementation','ROM version and build configuration remain unknown','Source ROMAPI delegation is not local implementation certification'])
(OUT/'source-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checks':len(checks),'source_functions':len(rows),'new_rom_functionality':0},ensure_ascii=False))
