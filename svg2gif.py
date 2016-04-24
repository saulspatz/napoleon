import os, subprocess
inkscape = '/Applications/Inkscape.app/Contents/Resources/bin/inkscape'
width = '75'
top = '/Users/saul/Desktop/4ColorSuits'
source = os.path.join(top,'horizontal','spriteHorizNew.svg')
target = os.path.join(top,'horizontal')
suits = ['spade','heart','diamond','club']
ranks = ['Ace','2','3','4','5','6','7','8','9','10','Jack','Queen','King']
w = 210
h = 315

def convert(base,x0,x1,y0,y1):
    area = '-a %d:%d:%d:%d'%(x0,y0,x1,y1)
    png = os.path.join(target, 'pngs',base+'.png')
    gif = os.path.join(target,'gifs', base+'.gif')
    svg =  os.path.join(target,'svgs', base+'.svg')

    subprocess.run([inkscape,'-z',area,'-f', source, '-w', width, '-e', png])
    subprocess.run(['convert', png, gif])            

for s, suit in enumerate(suits):
    for r,rank in enumerate(ranks):
        x0 = r*w
        x1 = x0+w
        y0=s*h
        y1 = y0+h
        base = suit+rank 
        convert(base,x0,x1,y0,y1)

others = ['blueBack','redBack','redJoker','blackJoker']

for c, base in enumerate(others):
    x0 = 13*w
    x1 = x0+w
    y0= c*h
    y1= y0+h
    convert(base,x0,x1,y0,y1)
    