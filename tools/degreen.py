"""Recolour greenish colour literals for the Væringjar restyle.
 muted greens  -> neutral grey of equal luminance (alpha kept)
 bright greens -> accent: var(--vj-accent) in CSS contexts, literal ACC_HEX elsewhere
Usage: degreen2.py FILE...   (edits in place; prints a per-file count)"""
import re, sys, os
ACC_HEX=(140,196,154)
KEEP={(140,196,154),(47,106,69)}  # the theme accents themselves
def classify(r,g,b):
    if (round(r),round(g),round(b)) in KEEP: return None
    mx,mn=max(r,g,b),min(r,g,b)
    # green-dominant: clearly green, or a green tint on a dark/neutral colour
    if not (g==mx and (g-max(r,b)>=14 or (g-r>=6 and g-b>=3))): return None
    sat=(mx-mn)/mx if mx else 0
    if sat>0.42 and mx>170: return 'acc'
    L=round(0.2126*r+0.7152*g+0.0722*b); return (L,L,L)
def fmt(kind, alpha, css):
    if kind=='acc':
        if css:
            if alpha is None or float(alpha)>=1: return 'var(--vj-accent)'
            return f'color-mix(in srgb,var(--vj-accent) {round(float(alpha)*100,1)}%,transparent)'
        kind=ACC_HEX
    r,g,b=kind
    return f'rgba({r},{g},{b},{alpha})' if alpha is not None else '#%02x%02x%02x'%(r,g,b)
def recolour(text, css):
    cnt=[0]
    def hx(m):
        h=m.group(1)
        if len(h)==3: h=''.join(c*2 for c in h)
        r,g,b=(int(h[i:i+2],16) for i in (0,2,4)); k=classify(r,g,b)
        if k is None: return m.group(0)
        cnt[0]+=1; return fmt(k,None,css)
    def rg(m):
        a=[x.strip() for x in m.group(2).split(',')]
        if len(a) not in (3,4): return m.group(0)
        try: r,g,b=(float(x) for x in a[:3])
        except: return m.group(0)
        k=classify(r,g,b)
        if k is None: return m.group(0)
        cnt[0]+=1; return fmt(k, a[3] if len(a)==4 else None, css)
    text=re.sub(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-zA-Z_-])',hx,text)
    text=re.sub(r'(rgba?)\(([^()]*)\)',rg,text)
    return text,cnt[0]
total=0
for p in sys.argv[1:]:
    s=open(p,encoding='utf-8').read(); ext=os.path.splitext(p)[1]
    if ext=='.css': s2,n=recolour(s,True)
    elif ext=='.html':
        n=0
        def blk(m):
            global_n=recolour(m.group(0),True); blk.n+=global_n[1]; return global_n[0]
        blk.n=0
        s2=re.sub(r'<style[^>]*>.*?</style>|style="[^"]*"',blk,s,flags=re.S)
        def other(m):
            t,k=recolour(m.group(0),False); other.n+=k; return t
        other.n=0
        # remaining literals outside style contexts (svg attributes etc.)
        parts=re.split(r'(<style[^>]*>.*?</style>|style="[^"]*")',s2,flags=re.S)
        s2=''.join(x if i%2 else re.sub(r'(?:fill|stroke|stop-color|flood-color|color)="[^"]*"',other,x) for i,x in enumerate(parts))
        n=blk.n+other.n
    else: s2,n=recolour(s,False)
    if n: open(p,'w',encoding='utf-8').write(s2); print(n,p); total+=n
print('TOTAL',total)
