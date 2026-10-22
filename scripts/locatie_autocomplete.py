"""
Interactieve stagemarkt prompt met autocomplete voor niveau, opleiding, locatie en straal.

Gebruik:
    python scripts/locatie_autocomplete.py

Vereist: prompt_toolkit
"""

from __future__ import annotations

from typing import Any
import asyncio
import difflib
import operator
from time import monotonic

from prompt_toolkit.application import get_app
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession

from stagemarkt import Niveau, StagemarktClient, Straal

client = StagemarktClient()

tasks: set[asyncio.Task] = set()


def create_task(coro: Any) -> asyncio.Task:
    try:
        loop = asyncio.get_running_loop()
        task = loop.create_task(coro)
    except RuntimeError:
        task = asyncio.create_task(coro)

    task.add_done_callback(tasks.discard)
    tasks.add(task)

    return task


def get_score(name: str, term: str) -> float:
    n = name.casefold()
    t = term.casefold()
    if not t:
        return 1.0
    if t in n:
        pos = n.find(t)
        return max(0.0, 0.95 - 0.03 * pos)
    return difflib.SequenceMatcher(None, t, n).ratio()


class CustomCompleter(Completer):
    """Base class for custom completers with caching and async fetch."""

    def __init__(self, niveau: Niveau) -> None:
        self.niveau: Niveau = niveau
        self._cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
        self._ttl_seconds = 30.0
        self._inflight: set[str] = set()

    def _cache_get(self, term: str) -> list[dict[str, Any]] | None:
        hit = self._cache.get(term)
        if hit is None:
            return []

        ts, values = hit
        if (monotonic() - ts) > self._ttl_seconds:
            self._cache.pop(term, None)
            return None
        return values

    def _cache_set(self, term: str, values: list[dict[str, Any]]) -> None:
        now = monotonic()
        self._cache[term] = (now, values)
        # Also seed shorter prefixes so backspace immediately has cached suggestions
        t = term.strip()
        for i in range(2, len(t)):
            prefix = t[:i]
            existing = self._cache.get(prefix)
            if existing is None or len(existing[1]) < len(values):
                self._cache[prefix] = (now, values)
        # Invalidate UI so newly fetched suggestions appear without extra typing
        try:
            app = get_app()
            app.invalidate()
            # Actively start completion to refresh dropdown on updates/backspace
            if app.current_buffer is not None:
                app.current_buffer.start_completion(select_first=False)
        except Exception:  # noqa: BLE001, S110
            pass

    def _merge_cached_candidates(self, term: str) -> list[str]:
        term_cf = term.casefold()
        out: list[str] = []
        seen: set[str] = set()
        for k, (_, vals) in self._cache.items():
            k_cf = k.casefold()
            if term_cf.startswith(k_cf) or k_cf.startswith(term_cf):
                for s in vals:
                    name = s.get("naam")
                    if not name:
                        continue
                    key = name.casefold()
                    if key in seen:
                        continue
                    seen.add(key)
                    if isinstance(s, dict) and "naam" in s:
                        out.append(s["naam"])
                    elif isinstance(s, str):
                        out.append(s)
        return out

    def _has_fresh_related_cache(self, term: str) -> bool:
        tcf = term.casefold()
        now = monotonic()
        for k, (ts, vals) in self._cache.items():
            if (now - ts) > self._ttl_seconds:
                continue
            kcf = k.casefold()
            if (tcf.startswith(kcf) or kcf.startswith(tcf)) and vals:
                return True
        return False

    def _has_inflight_related(self, term: str) -> bool:
        tcf = term.casefold()
        for k in self._inflight:
            kcf = k.casefold()
            if tcf.startswith(kcf) or kcf.startswith(tcf):
                return True
        return False


class OpleidingCompleter(CustomCompleter):
    """Synchronous completer that serves cached suggestions and fetches updates
    asynchronously in the running event loop.

    This avoids blocking the prompt and prevents creating extra clients/loops.
    """

    def _start_fetch(self, term: str) -> None:
        # Skip fetch when we have a fresh exact/prefix cache or related inflight request
        if self._cache_get(term) is not None:
            return
        if self._has_fresh_related_cache(term):
            return
        if self._has_inflight_related(term):
            return
        self._inflight.add(term)

        async def _do():
            try:
                results = await _fetch_opleiding_suggesties(self.niveau, term)
                self._cache_set(term, results)
            except Exception as e:  # noqa: BLE001
                print(f"Error fetching opleiding suggestions for term={term!r}: {e!r}")
                # Swallow; UI will keep working with cached/prefix results
                pass
            finally:
                self._inflight.discard(term)

        try:
            create_task(_do())
        except RuntimeError:  # noqa: S110
            # No running loop; ignore (shouldn't happen when used inside prompt_toolkit)
            pass

    def get_completions(self, document, complete_event):
        term = document.text_before_cursor.strip()
        if len(term) < 2:
            return
        # Build candidate list from cache with prefix merging
        direct = self._cache_get(term) or []
        merged = self._merge_cached_candidates(term)
        # Prefer direct cache first, then merged uniques
        names_seen: set[str] = set()
        candidates: list[dict] = []
        for v in direct + merged:
            name = v.get("naam")
            if not name:
                continue
            key = name.casefold()
            if key in names_seen:
                continue
            names_seen.add(key)
            candidates.append(v)

        # Only fetch if we have no candidates yet
        if not candidates:
            self._start_fetch(term)

        # Score, sort by relevance, filter by threshold and limit
        scored: list[tuple[float, dict]] = []
        for v in candidates:
            s = get_score(v.get("naam", ""), term)
            scored.append((s, v))
        scored.sort(key=operator.itemgetter(0), reverse=True)
        out: list[dict] = []
        for s, v in scored:
            if s < 0.35:
                continue
            out.append(v)
            if len(out) >= 10:
                break

        for o in out:
            display = f"{o['naam']} ({o['crebocode']})"
            yield Completion(o["naam"], start_position=-len(term), display=display)


class LocatieCompleter(CustomCompleter):
    """Synchronous completer that serves cached location suggestions and
    fetches updates asynchronously in the running event loop.
    """

    def _start_fetch(self, term: str) -> None:
        if self._cache_get(term) is not None:
            return
        if self._has_fresh_related_cache(term):
            return
        if self._has_inflight_related(term):
            return
        self._inflight.add(term)

        async def _do():
            try:
                results = await _fetch_locatie_suggesties(term)
                self._cache_set(term, results)
            except Exception:  # noqa: BLE001, S110
                pass
            finally:
                self._inflight.discard(term)

        try:
            create_task(_do())
        except RuntimeError:  # noqa: S110
            pass

    def get_completions(self, document, complete_event):
        term = document.text_before_cursor.strip()
        if len(term) < 2:
            return
        direct = self._cache_get(term) or []
        merged = self._merge_cached_candidates(term)
        # Build unique candidate list
        seen: set[str] = set()
        candidates: list[str] = []
        for s in direct + merged:
            key = s.casefold()
            if key in seen:
                continue
            seen.add(key)
            candidates.append(s)

        # Trigger background fetch only if we have no candidates
        if not candidates:
            self._start_fetch(term)

        # Score, sort by relevance, filter by threshold and limit
        scored: list[tuple[float, str]] = [(get_score(s, term), s) for s in candidates]
        scored.sort(key=operator.itemgetter(0), reverse=True)
        out: list[str] = []
        for score, s in scored:
            if score < 0.35:
                continue
            out.append(s)
            if len(out) >= 10:
                break

        for s in out:
            yield Completion(s, start_position=-len(term), display=s)


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


# Suggesties ophalen voor opleidingen
async def _fetch_opleiding_suggesties(niveau: Niveau, term: str, max_results: int = 20) -> list[dict]:
    result = await client.zoek_opleidingen(niveau=niveau, term=term, limiet=max_results)
    # result.suggesties: list[OpleidingSuggestieItem]
    # Elk item heeft .naam en .crebocode
    a = [{"naam": o.label, "crebocode": o.crebo_code} for o in result.opleidingen if o.label or o.crebo_code]
    print(f"Fetched {len(a)} opleiding suggestions for term={term!r}", a)
    return a


# Suggesties ophalen voor locaties
async def _fetch_locatie_suggesties(term: str, max_results: int = 20) -> list[str]:
    result = await client.zoek_locaties(term=term)
    suggestions = [loc.suggestie for loc in result.locaties if loc.suggestie]
    return _dedupe_keep_order(suggestions)[:max_results]


# --------- INTERACTIEVE PROMPT ---------
async def main() -> None:

    # 1. Kies niveau
    niveau_choices = [(n.name, n) for n in Niveau]
    niveau_text = "\n".join(f"{i + 1}. {name}" for i, (name, _) in enumerate(niveau_choices))
    print("Kies niveau:")
    print(niveau_text)
    while True:
        sel = input("Nummer: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(niveau_choices):
            niveau = niveau_choices[int(sel) - 1][1]
            break
        print("Ongeldige keuze.")

    # 2. Kies opleiding (autocomplete)
    print("Typ een opleiding (autocomplete):")
    session = PromptSession(completer=OpleidingCompleter(niveau), complete_while_typing=True)
    # Ensure completion dropdown refreshes on any edit (incl. backspace)
    try:
        buf = session.default_buffer

        def _on_change(_buf):
            try:
                app = get_app()
                app.invalidate()
            except Exception:
                pass
            _buf.start_completion(select_first=False)

        buf.on_text_changed += _on_change
    except Exception:
        pass
    with patch_stdout():
        opleiding_naam = await session.prompt_async("Opleiding: ")

    # Vind crebocode bij gekozen naam
    opleidingen = await _fetch_opleiding_suggesties(niveau, opleiding_naam, max_results=5)
    opleiding = next((o for o in opleidingen if o["naam"].lower() in opleiding_naam.lower()), None)
    if not opleiding:
        print("Opleiding niet gevonden.")
        return
    crebocode = opleiding["crebocode"]

    # 3. Kies locatie (autocomplete)
    print("Typ een locatie (autocomplete):")
    session = PromptSession(completer=LocatieCompleter(niveau), complete_while_typing=True)
    try:
        buf = session.default_buffer

        def _on_change2(_buf):
            try:
                app = get_app()
                app.invalidate()
            except Exception:
                pass
            _buf.start_completion(select_first=False)

        buf.on_text_changed += _on_change2
    except Exception:
        pass
    with patch_stdout():
        locatie = await session.prompt_async("Locatie: ")

    # 4. Kies straal
    straal_choices = [(s.name, s) for s in Straal]
    straal_text = "\n".join(f"{i + 1}. {name}" for i, (name, _) in enumerate(straal_choices))
    print("Kies straal:")
    print(straal_text)
    while True:
        sel = input("Nummer: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(straal_choices):
            straal = straal_choices[int(sel) - 1][1]
            break
        print("Ongeldige keuze.")

    # Toon samenvatting
    print("\nSamenvatting:")
    print(f"Niveau: {niveau.name}")
    print(f"Opleiding: {opleiding_naam} (crebocode: {crebocode})")
    print(f"Locatie: {locatie}")
    print(f"Straal: {straal.name}")


if __name__ == "__main__":
    import sys

    asyncio.run(main())
