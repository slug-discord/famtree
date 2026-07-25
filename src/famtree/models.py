from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Gender = Literal["male", "female"]


class Person(BaseModel):
    """One member of the tree."""

    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    avatar_url: Optional[str] = None
    gender: Optional[Gender] = None


class Theme(BaseModel):
    """Colours and font for a rendered tree, as CSS-ready strings."""

    model_config = ConfigDict(frozen=True)

    background: str = "#0e0e11"
    node_bg: str = "#1a1a1d"
    node_border: str = "rgba(255,255,255,0.08)"
    text: str = "#ffffff"
    subtext: str = "rgba(255,255,255,0.55)"
    edge: str = "rgba(255,255,255,0.22)"
    partner_edge: str = "rgba(226,116,195,0.75)"
    root_accent: str = "#6366f1"
    male_accent: str = "#4a90d9"
    female_accent: str = "#e274c3"
    font_family: str = "'Segoe UI', system-ui, -apple-system, sans-serif"

    @classmethod
    def named(
        cls, 
        name: str
    ) -> "Theme":
        """Return a built-in preset, or the default when unknown."""
        return _THEMES.get(name.lower(), cls())


_THEMES: dict[str, "Theme"] = {
    "dark": Theme(),
    "light": Theme(
        background="#f4f4f6",
        node_bg="#ffffff",
        node_border="rgba(0,0,0,0.10)",
        text="#111114",
        subtext="rgba(0,0,0,0.55)",
        edge="rgba(0,0,0,0.25)",
        root_accent="#5554c4",
    ),
    "sunset": Theme(
        background="#1a0f1f",
        node_bg="#2a1526",
        node_border="rgba(226,116,195,0.25)",
        edge="rgba(226,116,195,0.35)",
        root_accent="#e274c3",
    ),
}


class Tree(BaseModel):
    """A rooted family graph: people plus parent and partner relations."""

    root: int
    people: dict[int, Person]
    parent_edges: list[tuple[int, int]] = Field(default_factory=list)
    partner_edges: list[tuple[int, int]] = Field(default_factory=list)

    def person(
        self, 
        uid: int
    ) -> Person:
        """Look up a person, falling back to a bare node for unknown ids."""
        return self.people.get(uid) or Person(
            id=uid, 
            name=str(uid)
        )
