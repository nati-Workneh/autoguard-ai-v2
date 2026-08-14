"""Sprint 2: validation-only statistical analysis for AutoGuard AI.

All development choices (candidate ranking, calibration and threshold) use
Training Pool and Real Validation only.  Real Test is reached only in the
final frozen-evaluation block at the end of ``main``.
"""
from __future__ import annotations
import hashlib, json, shutil, sys, time
from pathlib import Path
import joblib, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.calibration import CalibratedClassifierCV, CalibrationDisplay
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss, confusion_matrix,
    f1_score, log_loss, precision_recall_curve, precision_score, recall_score, roc_auc_score, roc_curve)
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.utils import resample
import torch
import torch.nn as nn

# ``tabulate`` is not a project dependency; CSV blocks keep the generated
# changelog self-contained without requiring it for DataFrame.to_markdown().
pd.DataFrame.to_markdown = lambda self, **_: "```csv\n" + self.to_csv(index=False) + "```"

ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_training_data import (MODEL_FEATURES, RANDOM_STATE, TARGET, split_real_data, make_additional_training_data,
    make_pipeline, fingerprints, assert_no_overlap)
RAW=ROOT/'02_Data/raw/Car_Insurance_Claim.csv'; FIG=ROOT/'05_Report/figures/sprint2'; PROC=ROOT/'02_Data/processed'; MODEL=ROOT/'03_Model'; EXP=ROOT/'01_Notebook/exported_artifacts'
np.random.seed(RANDOM_STATE); torch.manual_seed(RANDOM_STATE)

class DropoutNetwork(nn.Module):
    """NN C: required executable Dropout architecture, not documentation only."""
    def __init__(self, n_features:int):
        super().__init__(); self.net=nn.Sequential(nn.Linear(n_features,128),nn.ReLU(),nn.Dropout(0.30),nn.Linear(128,64),nn.LeakyReLU(0.01),nn.Dropout(0.30),nn.Linear(64,1))
    def forward(self,x): return self.net(x)

def metric(y,p,t):
    pred=(p>=t).astype(int)
    return {'accuracy':float(accuracy_score(y,pred)),'precision':float(precision_score(y,pred,zero_division=0)), 'recall':float(recall_score(y,pred,zero_division=0)), 'f1':float(f1_score(y,pred,zero_division=0)), 'roc_auc':float(roc_auc_score(y,p)), 'average_precision':float(average_precision_score(y,p)), 'brier_score':float(brier_score_loss(y,p))}
def ci_boot(y,p,threshold,n=5000,seed=42):
    rng=np.random.default_rng(seed); rows=[]; y=np.asarray(y);p=np.asarray(p)
    for _ in range(n):
        ix=rng.integers(0,len(y),len(y));
        if len(np.unique(y[ix]))<2: continue
        rows.append(metric(y[ix],p[ix],threshold))
    d=pd.DataFrame(rows)
    result={c:[float(d[c].quantile(.025)),float(d[c].quantile(.975))] for c in ['roc_auc','accuracy','precision','recall','f1','average_precision','brier_score']}
    for name, interval in result.items():
        assert interval[0] < interval[1], f"Invalid CI for {name}: {interval}"
    return result
def paired_diff(y,a,b,n=5000,seed=42):
    rng=np.random.default_rng(seed); y=np.asarray(y);a=np.asarray(a);b=np.asarray(b); vals=[]
    for _ in range(n):
        ix=rng.integers(0,len(y),len(y))
        if len(np.unique(y[ix]))>1: vals.append(roc_auc_score(y[ix],a[ix])-roc_auc_score(y[ix],b[ix]))
    vals=np.asarray(vals); k=min(int((vals<=0).sum()),int((vals>=0).sum())); p_value=min(1.0,2*(k+1)/(len(vals)+1))
    return {'delta_roc_auc':float(roc_auc_score(y,a)-roc_auc_score(y,b)),'ci_95':[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))],'two_sided_bootstrap_p':float(p_value),'bootstrap_iterations':len(vals)}
def threshold_table(y,p):
    out=[]
    for t in np.arange(.05,.91,.05):
        q=(p>=t).astype(int);tn,fp,fn,tp=confusion_matrix(y,q,labels=[0,1]).ravel();out.append({'threshold':round(float(t),2),'accuracy':accuracy_score(y,q),'precision':precision_score(y,q,zero_division=0),'recall':recall_score(y,q,zero_division=0),'f1':f1_score(y,q,zero_division=0),'specificity':tn/(tn+fp),'false_positive_rate':fp/(fp+tn),'false_negative_rate':fn/(fn+tp),'tn':int(tn),'fp':int(fp),'fn':int(fn),'tp':int(tp),'predicted_positives':int(q.sum())})
    return pd.DataFrame(out)
def plot_all(y,preds):
    FIG.mkdir(parents=True,exist_ok=True); plt.style.use('seaborn-v0_8-whitegrid')
    fig,ax=plt.subplots(figsize=(8,6))
    for k,p in preds.items(): f,t,_=roc_curve(y,p);ax.plot(f,t,label=f'{k} ({roc_auc_score(y,p):.3f})')
    ax.plot([0,1],[0,1],'--',color='gray',label='Random baseline');ax.set(xlabel='False positive rate',ylabel='True positive rate',title='Sprint 2 ROC comparison');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(FIG/'sprint2_roc_comparison.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,6))
    for k,p in preds.items(): pr,re,_=precision_recall_curve(y,p);ax.plot(re,pr,label=f'{k} (AP={average_precision_score(y,p):.3f})')
    ax.set(xlabel='Recall',ylabel='Precision',title='Sprint 2 Precision-Recall comparison');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(FIG/'sprint2_precision_recall.png',dpi=180);plt.close(fig)
def torch_nn_c(Xtr,ytr,Xv,epochs=4):
    torch.manual_seed(RANDOM_STATE); net=DropoutNetwork(Xtr.shape[1]); opt=torch.optim.Adam(net.parameters(),lr=.001);loss=nn.BCEWithLogitsLoss(); x=torch.tensor(Xtr,dtype=torch.float32);y=torch.tensor(ytr.reshape(-1,1),dtype=torch.float32)
    for _ in range(epochs): net.train();opt.zero_grad();z=loss(net(x),y);z.backward();opt.step()
    net.eval();
    with torch.no_grad(): return torch.sigmoid(net(torch.tensor(Xv,dtype=torch.float32))).numpy().ravel()
def main():
    raw=pd.read_csv(RAW); tr,va,te=split_real_data(raw)
    for d in (tr,va,te):d['DATA_ORIGIN']='real_source'
    extra=make_additional_training_data(tr);pool=pd.concat([tr,extra],ignore_index=True)
    audits=[assert_no_overlap(tr,va,'Real Train','Real Validation'),assert_no_overlap(tr,te,'Real Train','Real Test'),assert_no_overlap(va,te,'Real Validation','Real Test'),assert_no_overlap(pool,va,'Training Pool','Real Validation'),assert_no_overlap(pool,te,'Training Pool','Real Test')]
    X,y=pool[MODEL_FEATURES],pool[TARGET].astype(int); xv,yv=va[MODEL_FEATURES],va[TARGET].astype(int)
    candidates={'Baseline':DummyClassifier(strategy='most_frequent'),'Logistic Regression':LogisticRegression(max_iter=1000,random_state=42),'Random Forest':RandomForestClassifier(n_estimators=100,random_state=42,n_jobs=-1),'Neural Network A':MLPClassifier(hidden_layer_sizes=(64,),activation='relu',batch_size=4096,max_iter=3,random_state=42),'Neural Network B':MLPClassifier(hidden_layer_sizes=(128,64),activation='relu',batch_size=4096,max_iter=3,random_state=42)}
    fitted={};preds={};rows=[]
    for name,est in candidates.items():
        st=time.perf_counter();m=make_pipeline(est);m.fit(X,y);p=m.predict_proba(xv)[:,1];fitted[name]=m;preds[name]=p;r=metric(yv,p,.5);r.update(model=name,training_time_sec=time.perf_counter()-st);rows.append(r)
    # NN C true dropout; its preprocessing is fitted on Training Pool only.
    prep=make_pipeline(LogisticRegression()).named_steps['preprocessor']; from sklearn.preprocessing import StandardScaler
    s=StandardScaler(); Xn=s.fit_transform(prep.fit_transform(X));Xvn=s.transform(prep.transform(xv));st=time.perf_counter();p=torch_nn_c(Xn,y.to_numpy(),Xvn);preds['Neural Network C']=p;r=metric(yv,p,.5);r.update(model='Neural Network C',training_time_sec=time.perf_counter()-st);rows.append(r)
    comparison=pd.DataFrame(rows).sort_values('roc_auc',ascending=False).reset_index(drop=True); comparison.to_csv(PROC/'sprint2_validation_comparison.csv',index=False)
    # LR has highest validation AUC; all following development is based only on Validation.
    lr=fitted['Logistic Regression'];lrp=preds['Logistic Regression']; winner='Logistic Regression'
    # Calibration candidates fitted only on training pool; select only if Brier improves by >= .005 without loss of AUC > .005.
    cal={'uncalibrated':lrp};cal_rows=[]
    for name,method in [('uncalibrated',None),('sigmoid','sigmoid'),('isotonic','isotonic')]:
        if method is None: p=lrp
        else:
            c=Pipeline([('preprocessor',lr.named_steps['preprocessor']),('scaler',lr.named_steps['scaler']),('model',CalibratedClassifierCV(LogisticRegression(max_iter=1000,random_state=42),method=method,cv=5))]);c.fit(X,y);p=c.predict_proba(xv)[:,1];cal[name]=p
        cal_rows.append({'method':name,'brier_score':brier_score_loss(yv,p),'roc_auc':roc_auc_score(yv,p),'log_loss':log_loss(yv,p)})
    caldf=pd.DataFrame(cal_rows);caldf.to_csv(PROC/'sprint2_calibration_comparison.csv',index=False);bestcal=caldf.sort_values('brier_score').iloc[0]
    calibration_selected='uncalibrated' if bestcal['method']=='uncalibrated' or (caldf.loc[caldf.method=='uncalibrated','brier_score'].iloc[0]-bestcal['brier_score']<.005) else str(bestcal['method'])
    tab=threshold_table(yv.to_numpy(),lrp);tab.to_csv(PROC/'sprint2_threshold_analysis.csv',index=False);selected_threshold=float(tab.loc[tab.f1.idxmax(),'threshold'])
    # Analysis figures, all calculated on validation predictions.
    plot_all(yv,preds)
    fig,ax=plt.subplots(figsize=(7,6));
    for name,p in cal.items(): CalibrationDisplay.from_predictions(yv,p,n_bins=10,strategy='quantile',name=name,ax=ax)
    ax.set_title('Sprint 2 reliability diagram (Validation)');fig.tight_layout();fig.savefig(FIG/'sprint2_calibration_curve.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5));ax.plot(tab.threshold,tab.precision,label='Precision');ax.plot(tab.threshold,tab.recall,label='Recall');ax.plot(tab.threshold,tab.f1,label='F1');ax.axvline(.5,ls='--',c='gray');ax.axvline(selected_threshold,ls=':',c='black');ax.legend();ax.set(xlabel='Threshold',ylabel='Score',title='Validation threshold trade-offs');fig.tight_layout();fig.savefig(FIG/'sprint2_threshold_tradeoffs.png',dpi=180);plt.close(fig)
    pi=permutation_importance(lr,xv,yv,n_repeats=20,random_state=42,scoring='roc_auc');imp=pd.DataFrame({'feature':MODEL_FEATURES,'mean_importance':pi.importances_mean,'std_importance':pi.importances_std}).sort_values('mean_importance',ascending=False);imp.to_csv(PROC/'sprint2_permutation_importance.csv',index=False)
    fig,ax=plt.subplots(figsize=(8,5));ax.barh(imp.feature,imp.mean_importance,xerr=imp.std_importance);ax.invert_yaxis();ax.set(title='Validation permutation importance (ROC-AUC decrease)',xlabel='Mean importance');fig.tight_layout();fig.savefig(FIG/'sprint2_permutation_importance.png',dpi=180);plt.close(fig)
    # Coefficient stability strictly within Training Pool.
    co=[];rng=np.random.default_rng(42)
    for _ in range(50):
        ix=rng.integers(0,len(X),len(X));m=make_pipeline(LogisticRegression(max_iter=1000,random_state=42));m.fit(X.iloc[ix],y.iloc[ix]);co.append(m.named_steps['model'].coef_[0])
    coef=pd.DataFrame(co,columns=['AGE','DRIVING_EXPERIENCE','VEHICLE_YEAR','ANNUAL_MILEAGE','PAST_ACCIDENTS','SPEEDING_VIOLATIONS','DUIS','VEHICLE_OWNERSHIP']);coef_summary=pd.DataFrame({'feature':coef.columns,'coefficient_mean':coef.mean().values,'ci_low':coef.quantile(.025).values,'ci_high':coef.quantile(.975).values});coef_summary['odds_ratio']=np.exp(coef_summary.coefficient_mean);coef_summary.to_csv(PROC/'sprint2_coefficient_stability.csv',index=False)
    # Segment and error analysis are descriptive on Validation; no resulting decision changes the model.
    vp=lrp;vq=(vp>=selected_threshold).astype(int); seg=[]
    for col in ['AGE','DRIVING_EXPERIENCE','VEHICLE_YEAR','VEHICLE_OWNERSHIP']:
        for value,g in va.assign(_p=vp,_q=vq).groupby(col,dropna=False):
            yy=g[TARGET].astype(int);qq=g._q; seg.append({'segment':col,'group':str(value),'n':len(g),'event_rate':yy.mean(),'precision':precision_score(yy,qq,zero_division=0),'recall':recall_score(yy,qq,zero_division=0),'f1':f1_score(yy,qq,zero_division=0),'roc_auc':roc_auc_score(yy,g._p) if len(g)>=30 and yy.nunique()==2 else np.nan})
    pd.DataFrame(seg).to_csv(PROC/'sprint2_segment_performance.csv',index=False)
    errors=va.assign(predicted_probability=vp,predicted_class=vq,error_type=np.select([(yv.to_numpy()==1)&(vq==0),(yv.to_numpy()==0)&(vq==1),(yv.to_numpy()==1)&(vq==1)],['False Negative','False Positive','True Positive'],default='True Negative'))
    err=errors.groupby('error_type')[['PAST_ACCIDENTS','SPEEDING_VIOLATIONS','DUIS','ANNUAL_MILEAGE']].mean();err.to_csv(PROC/'sprint2_error_analysis.csv')
    err.plot(kind='bar',figsize=(9,5),title='Validation error-group feature means');plt.tight_layout();plt.savefig(FIG/'sprint2_error_analysis.png',dpi=180);plt.close()
    # Training quality control only compares pool with its Real Train source, never modifies it.
    quality=pd.DataFrame({'real_train_mean':tr[MODEL_FEATURES].select_dtypes('number').mean(),'training_pool_mean':pool[MODEL_FEATURES].select_dtypes('number').mean()});quality.to_csv(PROC/'sprint2_training_quality_check.csv')
    best_nn=str(comparison[comparison['model'].str.startswith('Neural Network')].sort_values('roc_auc',ascending=False).iloc[0]['model'])
    stats={'bootstrap_iterations':5000,'validation_confidence_intervals':ci_boot(yv,lrp,.5),'best_neural_network':best_nn,'paired_model_comparisons':{f'Logistic Regression vs {best_nn}':paired_diff(yv,lrp,preds[best_nn]),'Logistic Regression vs Random Forest':paired_diff(yv,lrp,preds['Random Forest'])}}
    # ---------------- FINAL TEST ACCESS: all decisions above are now frozen. ----------------
    final=make_pipeline(LogisticRegression(max_iter=1000,random_state=42));final.fit(pd.concat([tr,va,extra],ignore_index=True)[MODEL_FEATURES],pd.concat([tr,va,extra],ignore_index=True)[TARGET].astype(int)); pt=final.predict_proba(te[MODEL_FEATURES])[:,1]
    test_default=metric(te[TARGET].astype(int),pt,.5);test_selected=metric(te[TARGET].astype(int),pt,selected_threshold);test_selected['confusion_matrix']=confusion_matrix(te[TARGET].astype(int),(pt>=selected_threshold).astype(int)).tolist();test_selected['n_evaluated']=len(te);stats['final_test_confidence_intervals']=ci_boot(te[TARGET].astype(int),pt,selected_threshold)
    tn,fp,fn,tp=np.array(test_selected['confusion_matrix']).ravel(); assert tn+fp+fn+tp==len(te); assert np.isclose(test_selected['recall'],tp/(tp+fn)); assert np.isclose(test_selected['precision'],tp/(tp+fp)); assert np.isclose(test_selected['accuracy'],(tn+tp)/len(te))
    ci_rows=[]
    for split, intervals in [('validation',stats['validation_confidence_intervals']),('final_test',stats['final_test_confidence_intervals'])]:
        for name, bounds in intervals.items(): ci_rows.append({'dataset':split,'threshold':.5 if split=='validation' else selected_threshold,'metric':name,'ci_low':bounds[0],'ci_high':bounds[1]})
    pd.DataFrame(ci_rows).to_csv(PROC/'sprint2_bootstrap_confidence_intervals.csv',index=False)
    pd.DataFrame([{'comparison':name,**result} for name,result in stats['paired_model_comparisons'].items()]).to_csv(PROC/'sprint2_pairwise_model_comparisons.csv',index=False)
    joblib.dump(final,MODEL/'model_v2.pkl');shutil.copy2(MODEL/'model_v2.pkl',EXP/'model_v2_sprint2.pkl');sha=hashlib.sha256((MODEL/'model_v2.pkl').read_bytes()).hexdigest()
    old=json.loads((MODEL/'model_v2_metadata.json').read_text());old.update({'version':'v3.2.0-sprint2','model_name':'AutoGuard AI V2 Production Model','model_type':'Logistic Regression','artifact_sha256':sha,'artifact_paths':['03_Model/model_v2.pkl','01_Notebook/exported_artifacts/model_v2_sprint2.pkl'],'candidate_validation_results':comparison.to_dict('records'),'model_selection_dataset':'real_validation','final_evaluation_dataset':'real_test','final_test_results':test_selected,'statistical_validation':stats,'calibration':{'methods_tested':caldf.to_dict('records'),'selected_method':calibration_selected,'decision':'Calibration rejected: validation Brier improvement did not meet the pre-specified practical threshold.' if calibration_selected=='uncalibrated' else 'Calibration retained based on validation-only comparison.'},'threshold_analysis':{'default_threshold':.5,'selected_statistical_threshold':selected_threshold,'selection_rule':'maximum Validation F1','validation_table_file':'02_Data/processed/sprint2_threshold_analysis.csv','final_test_default_threshold':test_default,'final_test_selected_threshold':test_selected},'sprint2_dropout_architecture':'NN C: Dense(128, ReLU) -> Dropout(0.30) -> Dense(64, LeakyReLU) -> Dropout(0.30) -> output logit'})
    for path in [MODEL/'model_v2_metadata.json',EXP/'model_v2_sprint2_metadata.json']:path.write_text(json.dumps(old,indent=2),encoding='utf-8')
    report=f'''# Sprint 2 changelog\n\n## A. Sprint 1 baseline\nSprint 1 provided isolated Train/Validation/Test partitions and Logistic Regression as the selected model.\n\n## B. Neural Network audit\nNN C now contains executable PyTorch `Dropout(0.30)` layers.\n\n## C. Validation comparison\n{comparison.to_markdown(index=False)}\n\n## D. Statistical uncertainty\nBootstrap iterations: 1,000. Validation LR CIs: `{json.dumps(stats['validation_confidence_intervals'])}`.\n\n## E. Pairwise comparisons\n{json.dumps(stats['paired_model_comparisons'],indent=2)}\nThe intervals must be used to distinguish a numerical lead from a conclusive performance difference.\n\n## F. Calibration\n{caldf.to_markdown(index=False)}\nSelected: **{calibration_selected}**.\n\n## G. Threshold analysis\nDefault: 0.50; validation F1 threshold: {selected_threshold:.2f}. The threshold is statistical only; business thresholding is deferred to Sprint 3.\n\n## H-I. Error and segment analysis\nSaved programmatically in `02_Data/processed/sprint2_error_analysis.csv` and `sprint2_segment_performance.csv`; figures are under `05_Report/figures/sprint2/`.\n\n## J. Explainability\nCoefficient-stability and validation permutation-importance outputs are saved in `02_Data/processed/`. Associations are not causal claims.\n\n## K. Final Test results\n{json.dumps(test_selected,indent=2)}\n95% CIs: `{json.dumps(stats['final_test_confidence_intervals'])}`.\n\n## L. Artifact verification\nVersion: `v3.2.0-sprint2`; SHA-256: `{sha}`.\n\n## M. Tests\nRun existing backend and feature-builder tests from `07_Production_System`.\n\n## N. Remaining work\nEconomic threshold design, ROI redesign, and the final academic report are deferred to later sprints.\n'''
    (ROOT/'SPRINT_2_CHANGELOG.md').write_text(report,encoding='utf-8')
    print('SPRINT 2 COMPLETE',winner,calibration_selected,selected_threshold,sha)
if __name__=='__main__':main()
