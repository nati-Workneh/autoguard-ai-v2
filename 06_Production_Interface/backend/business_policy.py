"""Authoritative, model-independent operational routing policy."""
from __future__ import annotations
import json
from pathlib import Path
POLICY_PATH=Path(__file__).resolve().parents[2]/'07_Economic_Model'/'business_policy.json'
def load_business_policy(path:Path=POLICY_PATH)->dict:
 p=json.loads(path.read_text(encoding='utf-8'))
 for k in ['policy_version','business_threshold','manual_review_required_at_or_above_business_threshold']:
  if k not in p: raise ValueError(f'Missing business-policy field: {k}')
 if not isinstance(p['business_threshold'],(int,float)) or not 0<=p['business_threshold']<=1: raise ValueError('business_threshold must be within [0, 1]')
 return p
def business_action(probability:float,policy:dict|None=None)->str:
 p=policy or load_business_policy();return 'Manual review recommended' if probability>=p['business_threshold'] else 'Automatic processing eligible'
