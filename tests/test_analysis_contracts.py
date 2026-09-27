import pytest
from geosave.analysis_contracts import CounterfactualPair,benjamini_hochberg,flip_rate
def pair(i,a,b,status='valid'):return CounterfactualPair(str(i),'b'+str(i),'c'+str(i),'law_swap',a,b,status)
def test_flip_rate_excludes_parse_failures():
 result=flip_rate([pair(1,'A1','A2'),pair(2,'A1','A1'),pair(3,'A1','A2','failed')]); assert result=={'eligible_pairs':2,'flips':1,'flip_rate':.5}
def test_bh_is_deterministic_and_monotone():
 q=benjamini_hochberg({'h1':.01,'h2':.04,'h3':.03}); assert q=={'h2':.04,'h3':.04,'h1':.03}
 with pytest.raises(ValueError):benjamini_hochberg({'bad':1.1})
