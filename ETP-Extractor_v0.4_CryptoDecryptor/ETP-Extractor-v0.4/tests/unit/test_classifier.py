from etp_extractor.consumables.classifier import classify


def test_classifies_o_ring() -> None:
    result = classify("PACKING, PREFORMED O-RING")
    assert result.is_consumable
    assert result.category == "O_RING"


def test_non_consumable() -> None:
    result = classify("HOUSING ASSEMBLY")
    assert not result.is_consumable
