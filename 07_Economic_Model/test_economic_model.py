import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from economic_model import economics,calculate_operational_routing,calculate_critical_fn_cost_for_net_zero,calculate_critical_fn_cost_for_year1_break_even,describe_year1_fn_cost_break_even
B={'annual_applications':1000,'manual_review_minutes':20,'ai_assisted_review_minutes':10,'underwriter_hourly_cost':50,'implementation_cost':1000,'annual_maintenance_cost':100,'false_positive_cost':5,'false_negative_cost':150,'true_positive_operational_cost':5,'annual_fte_hours':1800}
CM=[50,10,5,35]
def r(x=B):return economics(CM,100,.3,x)
def test_routing_total():assert calculate_operational_routing(*CM)['total_cases']==100
def test_all_predicted_negative_is_automated():assert calculate_operational_routing(50,0,50,0)['automation_rate']==1
def test_all_predicted_positive_is_reviewed():assert calculate_operational_routing(0,50,0,50)['manual_review_rate']==1
def test_automation_includes_false_negatives():assert calculate_operational_routing(*CM)['automation_rate']==.55
def test_rates_sum_to_one():q=calculate_operational_routing(*CM);assert q['automation_rate']+q['manual_review_rate']==1
def test_zero_routing():assert calculate_operational_routing(0,0,0,0)['automation_rate']==0
def test_scaled_counts():q=r();assert q['tn']+q['fp']+q['fn']+q['tp']==1000
def test_year1_formula():q=r();assert q['year1_roi_pct']==(q['annual_net_benefit']-1000)/1000*100
def test_recurring_roi_formula():q=r();assert q['recurring_operating_roi_pct']==q['annual_net_benefit']/q['recurring_operating_cost']*100
def test_positive_payback():assert r()['payback_months']>0
def test_negative_benefit_no_payback():assert r({**B,'annual_maintenance_cost':1e7})['payback_months'] is None
def test_zero_volume():q=r({**B,'annual_applications':0});assert q['automation_rate']==0 and q['manual_review_rate']==0
def test_zero_maintenance_allowed():assert r({**B,'annual_maintenance_cost':0})['annual_maintenance_cost']==0
def test_invalid_assumption_fails():
 try:r({**B,'false_negative_cost':-1})
 except AssertionError:return
 assert False
def test_no_double_counting_error_components():q=r();assert q['total_error_cost']==q['annual_fp_cost']+q['annual_fn_cost']+q['annual_tp_operational_cost']
def test_manual_review_cases():assert calculate_operational_routing(*CM)['manual_review_cases']==45
def test_critical_fn_cost_reproduces_zero_net():
 q=r();c=calculate_critical_fn_cost_for_net_zero(q);assert abs(r({**B,'false_negative_cost':c})['annual_net_benefit'])<1e-6
def test_year1_fn_root_reproduces_year1_break_even_when_positive():
 q=r({**B,'implementation_cost':1})
 c=calculate_critical_fn_cost_for_year1_break_even(q)
 assert c is not None and c>0
 assert abs(r({**B,'implementation_cost':1,'false_negative_cost':c})['year1_roi_pct'])<1e-6
def test_negative_year1_fn_root_is_reported_as_infeasible():
 c=calculate_critical_fn_cost_for_year1_break_even(r({**B,'implementation_cost':1_000_000}))
 assert c is not None and c<0
 assert describe_year1_fn_cost_break_even(c)=='No feasible non-negative FN-cost solution'
