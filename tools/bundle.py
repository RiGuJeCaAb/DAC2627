import json, yaml, sys
order = ['scrInicio','scrL1BoasVindas','scrL1Pedido','scrL1Saudacao','scrL3Lista','scrL3Detalhe','scrL3Publicacao']
out = ['Screens:']
for scr in order:
    out.append(f'  {scr}:')
    props = json.load(open(f'yaml/{scr}.screen-props.json'))
    out.append('    Properties:')
    for k in sorted(props):
        v = props[k]
        lines = v.split('\n')
        if len(lines) == 1 and ': ' not in v:
            out.append(f'      {k}: {v}')
        else:
            out.append(f'      {k}: |-')
            for ln in lines: out.append(f'        {ln}')
    out.append('    Children:')
    for ln in open(f'yaml/{scr}.controls.yaml').read().rstrip('\n').split('\n'):
        out.append('      ' + ln)
txt = '\n'.join(out) + '\n'
d = yaml.safe_load(txt); assert list(d['Screens']) == order
open('yaml/RESP_7_SCREENS.yaml','w').write(txt)
print(len(txt))
