"""
Placeholders and interfaces for Phase 2+ modules. 
These are purely structural for the handoff and contain no implementation.
"""

class SocialSecurityEngine:
    def compute_taxable_benefits(self, *args, **kwargs):
        raise NotImplementedError("Phase 2: Social Security taxability not yet implemented.")

class LTCG_QDEngine:
    def compute_preferential_tax(self, *args, **kwargs):
        raise NotImplementedError("Phase 2: LTCG and Qualified Dividend stacking not yet implemented.")

class NIITEngine:
    def compute_net_investment_income_tax(self, *args, **kwargs):
        raise NotImplementedError("Phase 2: NIIT not yet implemented.")

class StateTaxPlugin:
    def compute_state_tax(self, *args, **kwargs):
        raise NotImplementedError("Phase 2: State tax plugins not yet implemented.")

class IRMAAEngine:
    def compute_surcharge_tiers(self, *args, **kwargs):
        raise NotImplementedError("Phase 2: IRMAA cliffs not yet implemented.")

class PerturbationEngine:
    def generate_marginal_curve(self, *args, **kwargs):
        raise NotImplementedError("Phase 2: Perturbation and marginal sliver analysis not yet implemented.")

class ChartPayloadGenerator:
    def build_waterfall_chart_data(self, *args, **kwargs):
        raise NotImplementedError("Phase 2: Chart payload generation not yet implemented.")