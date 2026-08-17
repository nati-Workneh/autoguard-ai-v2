"""Sprint 3.1 audited, configurable economic decision layer (no ML training)."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import joblib,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedGroupKFold
ROOT=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent;FIG=HERE/'figures'
def json_safe(value):
 if isinstance(value,float) and not np.isfinite(value): return None
 if isinstance(value,dict): return {k:json_safe(v) for k,v in value.items()}
 if isinstance(value,list): return [json_safe(v) for v in value]
 return value
def assumptions(): return pd.read_csv(HERE/'economic_assumptions.csv').set_index('parameter')
def scenario(a,name): return {k:float(a.loc[k,{'Conservative':'conservative_value','Expected':'expected_value','Optimistic':'optimistic_value'}[name]]) for k in a.index}
def fingerprint(frame):
 cols=[c for c in frame.columns if c not in {'ID','OUTCOME'}]
 return pd.util.hash_pandas_object(frame[cols].astype('string').fillna('<MISSING>'),index=False).astype(str)
def split_data(data):
 def holdout(frame,seed):
  keep,take=next(StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=seed).split(frame,frame.OUTCOME,fingerprint(frame)))
  return frame.iloc[keep].copy(),frame.iloc[take].copy()
 train_val,test=holdout(data,42);train,validation=holdout(train_val,43);return train,validation,test
def calculate_operational_routing(tn,fp,fn,tp):
 total=tn+fp+fn+tp
 if not total:return {'total_cases':0,'automated_cases':0,'manual_review_cases':0,'automation_rate':0.0,'manual_review_rate':0.0}
 automated=tn+fn;manual=fp+tp;result={'total_cases':total,'automated_cases':automated,'manual_review_cases':manual,'automation_rate':automated/total,'manual_review_rate':manual/total};assert abs(result['automation_rate']+result['manual_review_rate']-1)<1e-9;return result
def validate(x):
 for k,v in x.items(): assert v>=0,f'{k} must be non-negative'
def calculate_critical_fn_cost_for_net_zero(result):
 return (result['annual_net_benefit']+result['annual_fn_cost'])/result['fn'] if result['fn'] else None
def calculate_critical_fn_cost_for_year1_break_even(result):
 return (result['annual_net_benefit']+result['annual_fn_cost']-result['implementation_cost'])/result['fn'] if result['fn'] else None
def describe_year1_fn_cost_break_even(critical_fn_cost):
 return ('No feasible non-negative FN-cost solution' if critical_fn_cost is not None and critical_fn_cost < 0 else 'Feasible non-negative FN-cost solution')
def calculate_volume_break_even(cm,n,t,x):
 return next((v for v in range(1,100001) if economics(cm,n,t,{**x,'annual_applications':v})['year1_roi_pct']>=0),None)
def calculate_implementation_cost_break_even(result): return result['annual_net_benefit']
def economics(cm,n,t,x):
 validate(x);scale=x['annual_applications']/n if n else 0;tn,fp,fn,tp=[z*scale for z in cm];route=calculate_operational_routing(tn,fp,fn,tp);base=x['annual_applications']*x['manual_review_minutes']/60*x['underwriter_hourly_cost'];ai_labor=route['manual_review_cases']*x['ai_assisted_review_minutes']/60*x['underwriter_hourly_cost'];fp_cost=fp*x['false_positive_cost'];fn_cost=fn*x['false_negative_cost'];tp_cost=tp*x['true_positive_operational_cost'];error=fp_cost+fn_cost+tp_cost;recurring=ai_labor+x['annual_maintenance_cost']+error;net=base-recurring;year1=(net-x['implementation_cost'])/x['implementation_cost']*100 if x['implementation_cost'] else None;recurring_roi=net/recurring*100 if recurring else None;payback=x['implementation_cost']/(net/12) if net>0 else None
 return {**route,'threshold':t,'tn':tn,'fp':fp,'fn':fn,'tp':tp,'baseline_manual_cost':base,'ai_assisted_labor_cost':ai_labor,'annual_labor_savings':base-ai_labor,'annual_fp_cost':fp_cost,'annual_fn_cost':fn_cost,'annual_tp_operational_cost':tp_cost,'total_error_cost':error,'annual_maintenance_cost':x['annual_maintenance_cost'],'recurring_operating_cost':recurring,'annual_net_benefit':net,'implementation_cost':x['implementation_cost'],'year1_roi_pct':year1,'recurring_operating_roi_pct':recurring_roi,'payback_months':payback,'manual_hours_before':x['annual_applications']*x['manual_review_minutes']/60,'manual_hours_after':route['manual_review_cases']*x['ai_assisted_review_minutes']/60,'review_hours_saved':x['annual_applications']*x['manual_review_minutes']/60-route['manual_review_cases']*x['ai_assisted_review_minutes']/60}
def main():
 FIG.mkdir(parents=True,exist_ok=True);a=assumptions();m=json.loads((ROOT/'01_ML_Model/model_v2_metadata.json').read_text());pipe=joblib.load(ROOT/'01_ML_Model/model_v2.pkl');_,va,te=split_data(pd.read_csv(ROOT/'02_Data/Car_Insurance_Claim_50000_FINAL.csv'));p=pipe.predict_proba(va[m['feature_list']])[:,1];exp=scenario(a,'Expected');rows=[]
 for t in np.arange(.05,.91,.05): rows.append(economics(confusion_matrix(va.OUTCOME,p>=t,labels=[0,1]).ravel(),len(va),round(float(t),2),exp))
 grid=pd.DataFrame(rows);bt=float(grid.loc[grid.annual_net_benefit.idxmax(),'threshold']);assert bt in set(grid.threshold);grid.to_csv(HERE/'threshold_economics.csv',index=False)
 sc=[]
 cm=confusion_matrix(va.OUTCOME,p>=bt,labels=[0,1]).ravel()
 for name in ['Conservative','Expected','Optimistic']:sc.append({'scenario':name,**economics(cm,len(va),bt,scenario(a,name))})
 sc=pd.DataFrame(sc);assert sc.loc[2,'annual_net_benefit']>=sc.loc[1,'annual_net_benefit']>=sc.loc[0,'annual_net_benefit'];sc.to_csv(HERE/'scenario_results.csv',index=False)
 # Explicit break-even roots for expected scenario; FN cost enters linearly.
 e=sc.iloc[1];critical_net=calculate_critical_fn_cost_for_net_zero(e);critical_year1=calculate_critical_fn_cost_for_year1_break_even(e);be=calculate_volume_break_even(cm,len(va),bt,exp)
 # Algebraic roots are numerically verified.  Negative Year-1 root is an
 # infeasible operational cost, reported rather than applied.
 check=economics(cm,len(va),bt,{**exp,'false_negative_cost':critical_net});assert abs(check['annual_net_benefit'])<1e-6
 # Sensitivity and genuine low/high tornado inputs.
 sens=[]
 for key in ['annual_applications','manual_review_minutes','ai_assisted_review_minutes','underwriter_hourly_cost','false_positive_cost','false_negative_cost','implementation_cost','annual_maintenance_cost']:
  vals=[]
  for ch in [-.3,0,.3]:
   x=exp.copy();x[key]*=1+ch;vals.append(economics(cm,len(va),bt,x)['annual_net_benefit']);sens.append({'parameter':key,'change_pct':ch*100,'annual_net_benefit':vals[-1]})
 sens=pd.DataFrame(sens);sens.to_csv(HERE/'sensitivity_analysis.csv',index=False);tornado=sens.pivot(index='parameter',columns='change_pct',values='annual_net_benefit');tornado['impact']=tornado[30]-tornado[-30];tornado=tornado.reindex(tornado.impact.abs().sort_values().index);tornado.to_csv(HERE/'tornado_inputs.csv')
 plt.style.use('seaborn-v0_8-whitegrid');fig,ax=plt.subplots(figsize=(8,5));ax.barh(tornado.index,tornado[0]-tornado[-30],left=tornado[-30],label='Low → Base');ax.barh(tornado.index,tornado[30]-tornado[0],left=tornado[0],label='Base → High');ax.set(title='Tornado: annual net benefit sensitivity',xlabel='Annual net benefit (USD)');ax.legend();fig.tight_layout();fig.savefig(FIG/'tornado_sensitivity.png',dpi=180);plt.close(fig)
 fig,ax=plt.subplots(figsize=(8,5));ax.plot(grid.threshold,grid.annual_net_benefit);ax.axvline(m['threshold_analysis']['selected_threshold'],ls='--',label='Validation F1 threshold');ax.axvline(bt,ls=':',label='Business threshold');ax.legend();ax.set(title='Validation business threshold economics',xlabel='Threshold',ylabel='Expected annual net benefit (USD)');fig.tight_layout();fig.savefig(FIG/'threshold_economic_value.png',dpi=180);plt.close(fig)
 fig,ax=plt.subplots(figsize=(8,5));x=np.arange(3);ax.bar(x-.2,sc.year1_roi_pct,.4,label='Year-1 ROI');ax.bar(x+.2,sc.recurring_operating_roi_pct,.4,label='Recurring operating ROI');ax.set_xticks(x,sc.scenario);ax.legend();ax.set(title='Scenario ROI definitions kept separate',ylabel='ROI (%)');fig.tight_layout();fig.savefig(FIG/'scenario_roi_comparison.png',dpi=180);plt.close(fig)
 fig,ax=plt.subplots(figsize=(7,5));ax.bar(['Baseline manual','AI-assisted review','Automated'],[e.manual_hours_before,e.manual_hours_after,e.automated_cases*exp['ai_assisted_review_minutes']/60]);ax.set(title='Expected routing and manual-review reduction',ylabel='Annual hours');fig.tight_layout();fig.savefig(FIG/'manual_review_reduction.png',dpi=180);plt.close(fig)
 # Test accessed once after Validation threshold freeze.
 pt=pipe.predict_proba(te[m['feature_list']])[:,1];tcm=confusion_matrix(te.OUTCOME,pt>=bt,labels=[0,1]).ravel();test=economics(tcm,len(te),bt,exp);assert test['threshold']==bt
 kpi={k:e[k] for k in ['threshold','automation_rate','manual_review_rate','manual_hours_before','manual_hours_after','review_hours_saved','annual_labor_savings','annual_fp_cost','annual_fn_cost','total_error_cost','recurring_operating_cost','annual_net_benefit','implementation_cost','year1_roi_pct','recurring_operating_roi_pct','payback_months']};pd.DataFrame([kpi]).to_csv(HERE/'business_kpi_summary.csv',index=False)
 out=json_safe({'model_version':m['version'],'artifact_sha256':hashlib.sha256((ROOT/'01_ML_Model/model_v2.pkl').read_bytes()).hexdigest(),'validation_f1_threshold':m['threshold_analysis']['selected_threshold'],'business_threshold':bt,'business_threshold_selection_dataset':'validation','threshold_selection_dataset':'validation','scenarios':sc.to_dict('records'),'test_observed_confusion_matrix':dict(zip(['tn','fp','fn','tp'],map(int,tcm))),'test_routing':test,'break_even':{'minimum_annual_volume_year1_roi_nonnegative':be,'maximum_implementation_cost_year1_roi_nonnegative':calculate_implementation_cost_break_even(e),'critical_fn_cost_annual_net_benefit_zero':critical_net,'critical_fn_cost_year1_roi_zero':critical_year1,'year1_fn_cost_break_even_interpretation':describe_year1_fn_cost_break_even(critical_year1)}})
 policy={'policy_version':'v4.0.0','business_threshold':bt,'validation_f1_threshold':m['threshold_analysis']['selected_threshold'],'manual_review_required_at_or_above_business_threshold':True,'human_review_required_for_high_risk':True,'selection_dataset':'validation','selection_objective':'maximize_expected_annual_net_benefit','economic_model_version':'v4.0.0','source':'AutoGuard AI economic optimization'}
 (HERE/'business_policy.json').write_text(json.dumps(policy,indent=2,allow_nan=False),encoding='utf-8')
 (HERE/'economic_results.json').write_text(json.dumps(out,indent=2,allow_nan=False),encoding='utf-8');print(json.dumps(out,indent=2,allow_nan=False))
if __name__=='__main__':main()
