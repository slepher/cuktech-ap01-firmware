"""Read-only, bounded PWM source anchor checks; no target execution."""
import json
import re
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
SDK = Path('D:/Documents/PlatformIO/Projects/bouffalo_sdk')
NUTTX = '/home/slepher/nuttx-ap01-sim/nuttx'
checks = []

def check(origin, relative, content, label, pattern):
    matches = list(re.finditer(pattern, content, re.M))
    assert matches, label
    checks.append(dict(origin=origin, file=relative, label=label,
                       lines=[content.count('\n', 0, m.start()) + 1 for m in matches]))

def sdk(relative):
    return (SDK / relative).read_text(encoding='utf-8')

def nuttx(relative):
    result = subprocess.run(['wsl', '-d', 'Ubuntu-24.04', '--', 'cat',
                             NUTTX + '/' + relative], check=True,
                            capture_output=True)
    return result.stdout.decode('utf-8')

p = 'arch/risc-v/src/bl602/bl602_pwm_lowerhalf.c'
c = nuttx(p)
for label, pattern in [
    ('optional 80MHz source', r'#define BL_PWM_BUS_BCLK\s+\(80000000\)'),
    ('private object holds five pins', r'uint32_t\s+chan_pin\[5\]'),
    ('direct integer period calculation', r'uint16_t period = BL_PWM_CLK / freq;'),
    ('zero lower threshold', r'^  threshold1 = 0;'),
    ('edge threshold uses /65535', r'threshold2 = \(uint16_t\)\(\(uint32_t\)period \* duty / 65535\);'),
    ('caller channel selection', r'int8_t chan = info->channels\[i\].channel;'),
    ('start calls frequency then duty', r'bl602_pwm_freq\(priv, chan, info->frequency\);\s+bl602_pwm_duty\(priv, chan, info->channels\[i\].duty\);'),
]:
    check('NuttX candidate', p, c, label, pattern)
for label, token in [('no 65536 search bound', '65536'),
                     ('no floating arithmetic spelling', 'double')]:
    assert token not in c, label
    checks.append(dict(origin='NuttX candidate', file=p, label=label,
                       absence_scope='this file only'))
p = 'include/nuttx/timers/pwm.h'
c = nuttx(p)
check('NuttX candidate', p, c, 'channel duty and channel identifier',
      r'ub16_t duty;[\s\S]*?int8_t channel;')
check('NuttX candidate', p, c, 'conditional two-argument lower start',
      r'CODE int \(\*start\)\(FAR struct pwm_lowerhalf_s \*dev,\s+FAR const struct pwm_info_s \*info\);')
p = 'arch/risc-v/src/bl602/hardware/bl602_pwm.h'
c = nuttx(p)
check('NuttX candidate', p, c, 'separate low/high registers',
      r'#define BL602_PWM0_THRE1_OFFSET\s+0x000024[\s\S]*?#define BL602_PWM0_THRE2_OFFSET\s+0x000028')
p = 'drivers/lhal/src/bflb_pwm_v2.c'
c = sdk(p)
for label, pattern in [
    ('init consumes divider', r'regval \|= \(uint32_t\)config->clk_div << PWM_CLK_DIV_SHIFT;'),
    ('init consumes period', r'regval \|= \(uint32_t\)config->period << PWM_PERIOD_SHIFT;'),
    ('PBCLK selection 1', r'config->clk_source == BFLB_SYSTEM_PBCLK\) \{\s+regval \|= \(1 << PWM_REG_CLK_SEL_SHIFT\);'),
    ('packs caller thresholds', r'regval = \(\(uint32_t\)high_threhold << 16\) \| low_threhold;'),
    ('threshold channel stride', r'putreg32\(regval, dev->reg_base \+ PWM_MC0_CH0_THRE_OFFSET \+ ch \* 4\);'),
    ('positive enable shift', r'regval \|= \(PWM_CH0_PEN << 4 \* ch\);'),
    ('start clears stop enable', r'regval &= ~PWM_STOP_EN;'),
]:
    check('SDK candidate', p, c, label, pattern)
for token in ['80000000', '65536', '0x8000']:
    assert token not in c, token
    checks.append(dict(origin='SDK candidate', file=p,
                       label='no literal ' + token, absence_scope='this file only'))
p = 'drivers/lhal/include/hardware/pwm_v2_reg.h'
c = sdk(p)
for name, value in [('PWM_MC0_CONFIG0_OFFSET','0x40'),
                    ('PWM_MC0_CONFIG1_OFFSET','0x44'),
                    ('PWM_MC0_PERIOD_OFFSET','0x48'),
                    ('PWM_MC0_CH0_THRE_OFFSET','0x50'),
                    ('PWM_CLK_DIV_SHIFT','0U'),('PWM_REG_CLK_SEL_SHIFT','30U'),
                    ('PWM_CH0_THREH_SHIFT','16U')]:
    check('SDK candidate', p, c, name, rf'#define {name}\s+\({value}\)')
result = dict(scope='source-text anchors only; inherited D15/D16 ROM contract not rerun',
              identities='reuse A13/A14/F07 and D07/D11/D12; not ROM source authentication',
              checks=checks, passed=len(checks),
              limitations='absence is literal/file bounded; no arbitrary renamed algorithm search, build or ABI proof')
(OUT / 'source-check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f'{len(checks)} bounded source checks passed')
