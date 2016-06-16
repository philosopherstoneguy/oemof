# -*- coding: utf-8 -*-
""" list:  Groupings needed on an energy system for it to work with solph.

TODO: Maybe move this to the module docstring? It shoule be somewhere prominent
      so solph user's immediately see that they need to use :const:`GROUPINGS`
      when they want to create an energy system for use with solph.

If you want to use solph on an energy system, you need to create it with these
groupings specified like this:

    .. code-block: python

    from oemof.network import EnergySystem
    import solph

    energy_system = EnergySystem(groupings=solph.GROUPINGS)

"""
from oemof.core import energy_system as core_es
from .network import Bus, LinearTransformer, Storage
from .options import Investment
from . import blocks
import oemof.groupings as groupings


def constraint_grouping(node):
    """Grouping function for constraints.

    This function can be passed in a list to :attr:`groupings` of
    :class:`oemof.solph.network.EnergySystem`.
    """
    if isinstance(node, Bus) and node.balanced:
        return blocks.Bus
    if isinstance(node, LinearTransformer):
        return blocks.LinearTransformer
    if isinstance(node, Storage) and isinstance(node.investment, Investment):
        return blocks.InvestmentStorage
    if isinstance(node, Storage):
        return blocks.Storage


investment_flow_grouping = groupings.FlowsWithNodes(
    constant_key=blocks.InvestmentFlow,
    # stf: a tuple consisting of (source, target, flow), so stf[2] is the flow.
    filter=lambda stf: stf[2].investment is not None)


def standard_flow_key(n):
    """Function returns keys for the energysystem attribute :attr:`es.groups`
    to store all standard flows (no investment, no discrete).
    """
    for f in n.outputs.values():
        if f.investment is None:
            return blocks.Flow


def standard_flows(n):
    """Function returns elements for group in energysystem attribute
    :attr:`es.groups` with key generated from :meth:`standard_flow_key`.
    """
    return [(n, t, f) for (t, f) in n.outputs.items()
            if f.investment is None]


def merge_standard_flows(n, group):
    """Extends the group with key returned from :meth:`standard_flow_key` with
    elements from meth:`standard_flows`
    """
    group.extend(n)
    return group

standard_flow_grouping = core_es.Grouping(
    key=standard_flow_key,
    value=standard_flows,
    merge=merge_standard_flows)


def discrete_flow_key(n):
    """Function returns keys for the energysystem attribute :attr:`es.groups`
    to store flows with :attr:`discrete` being set to an instance of
    :attr:`oemof.solph.options.Discrete` object.
    """
    for f in n.outputs.values():
        if f.discrete is not None:
            return blocks.Discrete


def discrete_flows(n):
    """Function returns elements for group in energysystem attribute
    :attr:`es.groups` with key generated from :meth:`discrete_flow_key`.
    """
    return [(n, t, f) for (t, f) in n.outputs.items()
            if f.discrete is not None]


def merge_discrete_flows(n, group):
    """Extends the group with key returned from :meth:`discrete_flow_key` with
    elements from meth:`discrete_flows`
    """
    group.extend(n)
    return group

discrete_flow_grouping = core_es.Grouping(
    key=discrete_flow_key,
    value=discrete_flows,
    merge=merge_discrete_flows)

GROUPINGS = [constraint_grouping, investment_flow_grouping,
             standard_flow_grouping, discrete_flow_grouping]
