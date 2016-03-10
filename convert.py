import os, re
sourceDir = '/Users/saul/Desktop/newClubs'
targetDir = '/Users/saul/Desktop/newClubs'
after =r"fill:#e500e5"
before=r"fill:#(000000|050505)"

pattern =re.compile(before)
os.chdir(sourceDir)
for f in os.listdir('.'):
        if not f.endswith('svg'): continue
        #if any(rank in f for rank in ('Jack','Queen','King')):continue
        text=open(f).read()
        text=re.sub(before,after, text)
        with open(os.path.join(targetDir,f), 'w') as fout:
                fout.write(text)
        