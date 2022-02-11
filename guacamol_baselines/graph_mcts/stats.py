import os
from os import path
import pickle
import pkg_resources
from collections import namedtuple

from .analyze_dataset import StatsCalculator

Stats = namedtuple(
    "Stats",
    [
        "average_size",
        "size_std_dev",
        "rxn_smarts_make_ring",
        "rxn_smarts_ring_list",
        "rxn_smarts_list",
        "p",
        "p_ring",
    ],
)


def scale_p_ring(rxn_smarts_ring_list, p_ring, new_prob_double):
    p_single = []
    p_double = []
    for smarts, p in zip(rxn_smarts_ring_list, p_ring):
        if "=" in smarts:
            p_double.append(p)
        else:
            p_single.append(p)

    # TODO commented because not used in original
    # prob_single = sum(p_single)
    prob_double = sum(p_double)
    scale_double = new_prob_double / prob_double
    scale_single = (1.0 - new_prob_double) / (1 - prob_double)
    for i, smarts in enumerate(rxn_smarts_ring_list):
        if "=" in smarts:
            p_ring[i] *= scale_double
        else:
            p_ring[i] *= scale_single

    return p_ring


def get_stats_from_pickle(dir_path: str) -> Stats:
    """
    Get distribution statistics from pickle files generated with analyze_dataset.py
    """
    size_stats_path = None if not dir_path else os.path.join(dir_path, 'size_stats.p')
    rs_make_king_path = None if not dir_path else os.path.join(dir_path, 'rs_make_ring.p')
    rs_ring_path = None if not dir_path else os.path.join(dir_path, 'rs_ring.p')
    r_s1_path = None if not dir_path else os.path.join(dir_path, 'r_s1.p')
    p1_path = None if not dir_path else os.path.join(dir_path, 'p1.p')
    p_ring_path = None if not dir_path else os.path.join(dir_path, 'p_ring.p')

    if not dir_path:
        pkg_model_path = pkg_resources.resource_filename("guacamol_baselines", "graph_mcts/size_stats.p")
        if path.exists(pkg_model_path):
            size_stats_path = pkg_model_path
        pkg_model_path = pkg_resources.resource_filename("guacamol_baselines", "graph_mcts/rs_make_ring.p")
        if path.exists(pkg_model_path):
            rs_make_king_path = pkg_model_path
        pkg_model_path = pkg_resources.resource_filename("guacamol_baselines", "graph_mcts/rs_ring.p")
        if path.exists(pkg_model_path):
            rs_ring_path = pkg_model_path
        pkg_model_path = pkg_resources.resource_filename("guacamol_baselines", "graph_mcts/r_s1.p")
        if path.exists(pkg_model_path):
            r_s1_path = pkg_model_path
        pkg_model_path = pkg_resources.resource_filename("guacamol_baselines", "graph_mcts/p1.p")
        if path.exists(pkg_model_path):
            p1_path = pkg_model_path
        pkg_model_path = pkg_resources.resource_filename("guacamol_baselines", "graph_mcts/p_ring.p")
        if path.exists(pkg_model_path):
            p_ring_path = pkg_model_path

    average_size, size_std_dev = pickle.load(open(size_stats_path, 'rb'))
    rxn_smarts_make_ring = pickle.load(open(rs_make_king_path, 'rb'))
    rxn_smarts_ring_list = pickle.load(open(rs_ring_path, 'rb'))

    rxn_smarts_list = pickle.load(open(r_s1_path, 'rb'))
    p = pickle.load(open(p1_path, 'rb'))

    prob_double = 0.8
    p_ring = pickle.load(open(p_ring_path, 'rb'))
    p_ring = scale_p_ring(rxn_smarts_ring_list, p_ring, prob_double)

    return Stats(average_size=average_size, size_std_dev=size_std_dev,
                 rxn_smarts_make_ring=rxn_smarts_make_ring,
                 rxn_smarts_ring_list=rxn_smarts_ring_list,
                 rxn_smarts_list=rxn_smarts_list,
                 p=p,
                 p_ring=p_ring)


def get_stats_from_smiles(smiles_file: str) -> Stats:
    """
    Generate distribution statistics from a file with SMILES strings.
    """
    stats_calculator = StatsCalculator(smiles_file=smiles_file)
    average_size, size_std_dev = stats_calculator.size_statistics()
    rxn_smarts_make_ring = stats_calculator.rxn_smarts_make_rings()
    rxn_smarts_ring_list = stats_calculator.rxn_smarts_rings()
    rxn_smarts_list = stats_calculator.rxn_smarts()
    p = stats_calculator.pair_probs()
    prob_double = 0.8
    p_ring = stats_calculator.ring_probs()
    p_ring = scale_p_ring(rxn_smarts_ring_list, p_ring, prob_double)

    return Stats(
        average_size=average_size,
        size_std_dev=size_std_dev,
        rxn_smarts_make_ring=rxn_smarts_make_ring,
        rxn_smarts_ring_list=rxn_smarts_ring_list,
        rxn_smarts_list=rxn_smarts_list,
        p=p,
        p_ring=p_ring,
    )
