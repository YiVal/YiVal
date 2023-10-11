from yival.schemas.experiment_config import WrapperVariation
from yival.schemas.varation_generator_configs import BaseVariationGeneratorConfig
from yival.variation_generators.base_variation_generator import BaseVariationGenerator


class DummyVariationGenerator(BaseVariationGenerator):

    def generate_variations(self):
        for i in range(3):
            yield [WrapperVariation(value_type="str", value="dummy")]


def test_variation_generator_registration():
    BaseVariationGenerator.register_variation_generator(
        "Dummy", DummyVariationGenerator, BaseVariationGeneratorConfig
    )

    assert BaseVariationGenerator.get_variation_generator(
        "Dummy"
    ) == DummyVariationGenerator
    assert BaseVariationGenerator.get_config_class(
        "Dummy"
    ) == BaseVariationGeneratorConfig


def test_variation_generator_generate_variations():
    generator = DummyVariationGenerator(config=BaseVariationGeneratorConfig())

    variations = list(generator.generate_variations())

    assert len(variations) == 3
    for variation_list in variations:
        assert len(variation_list) == 1
        assert isinstance(variation_list[0], WrapperVariation)
