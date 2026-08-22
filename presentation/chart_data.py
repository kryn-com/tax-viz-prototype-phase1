from models.chart_display import FederalChartSegment, FederalChartViewModel
from models.federal_display import FederalDisplayModel


_COMPONENT_LABELS = (
    ("Ordinary tax", "ordinary_tax"),
    ("LTCG/QD tax", "ltcg_qd_tax"),
    ("NIIT tax", "niit_tax"),
)


def build_federal_chart_view_model(
    model: FederalDisplayModel,
) -> FederalChartViewModel:
    tax_component_segments = tuple(
        FederalChartSegment(label=label, value=getattr(model, attribute))
        for label, attribute in _COMPONENT_LABELS
    )
    ordinary_bracket_segments = tuple(
        FederalChartSegment(
            label=f"Ordinary bracket {index}",
            value=slice_.tax_generated,
            rate=slice_.rate,
        )
        for index, slice_ in enumerate(model.ordinary_bracket_slices, start=1)
    )
    preferential_rate_segments = tuple(
        FederalChartSegment(
            label=f"Preferential rate {slice_.rate:.0%}",
            value=slice_.taxed_amount,
            rate=slice_.rate,
        )
        for slice_ in model.preferential_rate_slices
    )

    return FederalChartViewModel(
        tax_year=model.tax_year,
        filing_status=model.filing_status,
        total_federal_tax=model.total_federal_tax,
        tax_component_segments=tax_component_segments,
        ordinary_bracket_segments=ordinary_bracket_segments,
        preferential_rate_segments=preferential_rate_segments,
    )
