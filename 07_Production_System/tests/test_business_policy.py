from pathlib import Path
from backend.business_policy import business_action,load_business_policy
def test_policy_boundaries():
 p=load_business_policy();assert business_action(.14,p)=='Automatic processing eligible';assert business_action(.15,p)=='Manual review recommended';assert business_action(.20,p)=='Manual review recommended'
def test_invalid_policy_fails(tmp_path:Path):
 q=tmp_path/'p.json';q.write_text('{"business_threshold": 2}');
 try:load_business_policy(q)
 except ValueError:return
 assert False
