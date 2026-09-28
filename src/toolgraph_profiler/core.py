from collections import Counter,defaultdict
from dataclasses import dataclass
import html
@dataclass(frozen=True)
class Span:
 id:str; name:str; start:float; end:float; parent:str|None=None; status:str='ok'; lock_wait:float=0.0
 @property
 def duration(self): return self.end-self.start

def parse(rows): return [Span(str(x['id']),x['name'],float(x['start']),float(x['end']),str(x['parent']) if x.get('parent') is not None else None,x.get('status','ok'),float(x.get('lock_wait',0))) for x in rows]
def analyze(spans):
 by={s.id:s for s in spans}; memo={}
 def path_cost(s):
  if s.id in memo:return memo[s.id]
  base=s.duration
  memo[s.id]=(base,[s.id]) if not s.parent else ((lambda p:(p[0]+base,p[1]+[s.id]))(path_cost(by[s.parent])))
  return memo[s.id]
 best=max((path_cost(s) for s in spans),default=(0,[]),key=lambda x:x[0]); names=Counter(s.name for s in spans); failed=Counter(s.name for s in spans if s.status!='ok')
 ordered=sorted(spans,key=lambda s:(s.start,s.end)); gaps=[max(0,b.start-a.end) for a,b in zip(ordered,ordered[1:])]
 children=defaultdict(int)
 for s in spans:
  if s.parent: children[s.parent]+=1
 return {'span_count':len(spans),'wall_time':max((s.end for s in spans),default=0)-min((s.start for s in spans),default=0),'critical_path_duration':best[0],'critical_path':best[1],'retry_candidates':{k:v-1 for k,v in names.items() if v>1},'failed_by_tool':dict(failed),'max_fanout':max(children.values(),default=0),'idle_gap_total':sum(gaps),'lock_wait_total':sum(s.lock_wait for s in spans)}
def svg(spans,width=900,row=34):
 if not spans:return '<svg xmlns="http://www.w3.org/2000/svg"/>'
 lo=min(s.start for s in spans); hi=max(s.end for s in spans); scale=(width-220)/max(.001,hi-lo); h=45+row*len(spans)
 parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}">','<style>text{font-family:monospace;font-size:12px}.bar{fill:#222}.wait{fill:#999}</style>']
 for i,s in enumerate(sorted(spans,key=lambda x:x.start)):
  y=25+i*row; x=200+(s.start-lo)*scale; bw=max(2,s.duration*scale); parts += [f'<text x="8" y="{y+14}">{html.escape(s.name)}</text>',f'<rect class="bar" x="{x:.1f}" y="{y}" width="{bw:.1f}" height="18" rx="3"/>']
  if s.lock_wait: parts.append(f'<rect class="wait" x="{x:.1f}" y="{y+19}" width="{s.lock_wait*scale:.1f}" height="4"/>')
 parts.append('</svg>'); return ''.join(parts)
