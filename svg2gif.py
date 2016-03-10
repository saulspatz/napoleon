import os, subprocess
inkscape = '/Applications/Inkscape.app/Contents/Resources/bin/inkscape'
width = '75'
top = '/Users/saul/Desktop'

for sourceDir in (os.path.join(top,'2ColorSuits'),os.path.join(top,'4ColorSuits')):
    for f in os.listdir(sourceDir):
        if f.endswith('svg') and 'Joker' in f:
            base = os.path.splitext(f)[0]
            svg = os.path.join(sourceDir, f)
            png = os.path.join(sourceDir,'pngs', base+'.png')
            gif = os.path.join(sourceDir,'gifs', base+'.gif')
            subprocess.run([inkscape,'-z','-D','-f', svg, '-w', width, '-e', png])
            subprocess.run(['convert', png, gif])
        
        
    