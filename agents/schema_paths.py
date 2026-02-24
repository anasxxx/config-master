import copy
from typing import Any, Iterable, List, Set


def _is_primitive(x: Any) -> bool:
    return x is None or isinstance(x, (str, int, float, bool))


def build_leaf_paths(
    template_obj: Any,
    *,
    exclude_prefixes: Iterable[str] = ("options",),
) -> Set[str]:
    """
    Retourne tous les chemins "leaf" remplissables depuis un template JSON.

    - Dict => segments par clés
    - List => on modèle avec l'index 0 (".0.") basé sur le 1er élément du template
    - Leaf = primitive (str/int/float/bool/None) OU conteneur vide (dict/list vide)
    - exclude_prefixes => permet d'exclure des branches (ex: "options")
    """
    out: Set[str] = set()

    def rec(node: Any, path: List[str]):
        # Exclusion par préfixe
        if path and path[0] in set(exclude_prefixes):
            return

        # primitives => leaf
        if _is_primitive(node):
            if path:
                out.add(".".join(path))
            return

        # list => recurse sur élément 0
        if isinstance(node, list):
            idx_path = (path + ["0"]) if path else ["0"]

            if len(node) == 0:
                out.add(".".join(idx_path))
                return

            rec(node[0], idx_path)
            return

        # dict => recurse clés ; dict vide => leaf
        if isinstance(node, dict):
            if len(node) == 0:
                if path:
                    out.add(".".join(path))
                return

            for k, v in node.items():
                if isinstance(k, str):
                    rec(v, path + [k])
            return

        # autre type => ignore

    rec(template_obj, [])
    return out