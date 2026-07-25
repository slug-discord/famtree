from __future__ import annotations

from collections import defaultdict, deque

from .models import Tree


class Layout:
    """Turns a tree's relations into ordered generation rows."""

    @staticmethod
    def assign_generations(
        tree: Tree
    ) -> dict[int, int]:
        """Place each person relative to the root: parents up, children down, partners level."""
        parents_of: dict[int, list[int]] = defaultdict(list)
        children_of: dict[int, list[int]] = defaultdict(list)
        for parent, child in tree.parent_edges:
            parents_of[child].append(parent)
            children_of[parent].append(child)

        partners_of: dict[int, list[int]] = defaultdict(list)
        for a, b in tree.partner_edges:
            partners_of[a].append(b)
            partners_of[b].append(a)

        gen: dict[int, int] = {tree.root: 0}
        queue: deque[int] = deque([tree.root])
        while queue:
            node = queue.popleft()
            g = gen[node]
            for parent in parents_of.get(node, ()):
                if parent not in gen:
                    gen[parent] = g - 1
                    queue.append(parent)
            for child in children_of.get(node, ()):
                if child not in gen:
                    gen[child] = g + 1
                    queue.append(child)
            for partner in partners_of.get(node, ()):
                if partner not in gen:
                    gen[partner] = g
                    queue.append(partner)

        for uid in tree.people:
            gen.setdefault(uid, 0)
        return gen

    @staticmethod
    def build_rows(
        tree: Tree
    ) -> list[list[int]]:
        """Order people into rows, oldest first, keeping couples side by side."""
        gen = Layout.assign_generations(tree)

        partners_of: dict[int, list[int]] = defaultdict(list)
        for a, b in tree.partner_edges:
            partners_of[a].append(b)
            partners_of[b].append(a)

        by_gen: dict[int, list[int]] = defaultdict(list)
        seen: set[int] = set()

        for uid in sorted(
            tree.people, 
            key=lambda u: (gen[u], u)
        ):
            if uid in seen:
                continue
            g = gen[uid]
            by_gen[g].append(uid)
            seen.add(uid)
            for partner in sorted(partners_of.get(uid, ())):
                if partner not in seen and gen.get(partner) == g:
                    by_gen[g].append(partner)
                    seen.add(partner)

        return [by_gen[g] for g in sorted(by_gen)]
