# Esther PI: build the Vids clip queue from storyboard + shot windows + picture links (imgs.json; re-run when more pictures exist)
import json, math
R='https://pub-2993fb3bf56d45ffb3d678320781fe03.r2.dev/'
sb=json.load(open('../Esther_PI_storyboard.json')); win=json.load(open('windows.json')); imgs=json.load(open('imgs.json'))
TAIL=(" Keep every face, beard and garment exactly as in the start image. God is never shown: no figure, no face, no light-being."
      " Everyone stays modestly and fully clothed. No violence. No text on screen. No narration, no voiceover, no dialogue, no music. Natural ambient sound only.")
q=[]
for n,(s,w) in enumerate(zip(sb,win),1):
    if s['scene']==7: continue          # outro = channel outro clip
    d=w['end']-w['start']; ln=max(4,min(15,math.ceil(d+0.6)))
    if str(n) not in imgs: continue
    p=s['animation_prompt'].split('Keep every face')[0].strip()
    q.append(dict(key=f'v{n:02d}',len=ln,img=R+imgs[str(n)],name=f'Esther_PI_v{n:02d}.mp4',prompt=p+TAIL))
json.dump(q,open('vids_queue.json','w'),indent=0)
print(len(q),'clips',sum(x['len'] for x in q),'s')
