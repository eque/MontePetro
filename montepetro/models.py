import logging
from copy import deepcopy
from montepetro.seed_generators import SeedGenerator
from future.utils import iteritems


class Model(object):
    def __init__(self, name, seed):
        self.name = name
        self.seed = seed
        self.seed_generator = SeedGenerator(self.seed)
        self.properties = {}
        self.regions = {}

    def add_region(self, region):
        if region.name in self.regions.keys():
            logging.log(logging.ERROR,
                        "Encountered duplicate region" + str(region.name) + " in Model " + self.name + ".")
            raise KeyError
        else:
            for key in region.properties.keys():
                # update the regional property seed
                region.properties[key].update_seed(self.seed_generator)
                # delete any values
                region.properties[key].values = None
            self.regions[region.name] = region

    def add_property(self, prop):
        if prop.name in self.properties.keys():
            logging.log(logging.ERROR,
                        "Encountered duplicate property" + str(prop.name) + " in Model " + self.name + ".")
            raise KeyError
        else:
            prop.update_seed(self.seed_generator)
            self.properties[prop.name] = prop

    def add_defined_properties_to_regions(self):
        for region_name, region in iteritems(self.regions):
            for property_name, property in iteritems(self.properties):
                if property_name not in region.properties.keys():
                    region.add_property(deepcopy(property))
                    region.properties[property_name].update_seed(self.seed_generator)

    def add_regional_property(self, prop_name, prop):
        for region_name, region in iteritems(self.regions):
            region.properties[prop_name] = prop(region)
            region.properties[prop_name].generate_values()

    def run(self, config):
        for region_name, region in iteritems(self.regions):
            region_config = config[region_name]
            for property_name, property in iteritems(region.properties):
                regional_property_config = region_config[property_name]
                property.generate_values(**regional_property_config)

    def add_region2(self, region):
        if region.name in self.regions.keys():
            logging.log(logging.ERROR,
                        "Encountered duplicate region" + str(region.name) + " in Model " + self.name + ".")
            raise KeyError
        else:
            self.regions[region.name] = region
            self.properties[region.name] = {}

    def add_property2(self, region_name, prop):

        if prop.name in self.properties[region_name].keys():
            logging.log(logging.ERROR,
                    "Encountered duplicate property" + str(prop.name) + " in Model " + self.name + ".")
            raise KeyError
        else:
            prop.update_seed(self.seed_generator)
            self.properties[region_name][prop.name] = prop

    def add_constantfactorRegion(self, region_name, propname, factor):
        self.regions[region_name].properties[propname] = factor

    def add_defined_properties_to_regions2(self):
        for region_name, region in iteritems(self.regions):
            for property_name in self.properties[region_name].keys():
                if property_name not in region.properties.keys():
                    region.add_property(deepcopy(self.properties[region_name][property_name]))
                    region.properties[property_name].update_seed(self.seed_generator)

    def run2(self, config):
        for region_name, region in iteritems(self.regions):
            region_config = config[region_name]
            for property_name, props in iteritems(region.properties):
                regional_property_config = region_config[property_name]
                props.generate_values(**regional_property_config)
